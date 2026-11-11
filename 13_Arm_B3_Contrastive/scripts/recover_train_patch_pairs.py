#!/usr/bin/env python3
"""Recover patch-linked function candidates for finalized vulnerable train donors.

Each Devign candidate is checked against the patch hunk of its recorded commit.
The paired post-patch function is reconstructed by applying the matching hunk at
the C/C++ token level. This creates reviewer candidates, never reviewer-approved
ground truth. ReVeal missing-source records are emitted separately.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / "01_Author_Baseline_Unified" / "output" / "research_freeze_20261101"
OUT = Path(__file__).resolve().parents[1] / "output" / "train_patch_recovery_20261108"
PATCH_CACHE = ROOT.parent / "tmp" / "b3_recovery_src" / "patches"
TOKEN_RE = re.compile(
    r'R"(?P<delim>[^ ()\\\t\r\n]{0,16})\(.*?\)(?P=delim)"'
    r'|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''
    r'|//[^\n]*|/\*.*?\*/|[A-Za-z_][A-Za-z_0-9]*|\d+(?:\.\d+)?|[^\s]', re.S,
)
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)$")
PATCH_REPOS = {"ffmpeg": "FFmpeg/FFmpeg", "qemu": "qemu/qemu"}


def tokenize(code: str) -> list[str]:
    return [m.group() for m in TOKEN_RE.finditer(code) if not m.group().startswith(("//", "/*"))]


def tokens_with_spans(code: str) -> list[tuple[str, int, int]]:
    return [(m.group(), m.start(), m.end()) for m in TOKEN_RE.finditer(code)
            if not m.group().startswith(("//", "/*"))]


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_finalized_vulnerable_train(dataset: str) -> list[dict[str, Any]]:
    finalized = set()
    with (FREEZE / dataset / "donors.jsonl").open(encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            if int(d["target"]) == 1:
                finalized.add(str(d.get("function_uid") or d.get("id")))
    rows = []
    with (FREEZE / dataset / "train_raw.jsonl").open(encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            if d["id"] not in finalized or int(d["target"]) != 1:
                continue
            d["commit_id"] = d.get("commit_id") or None
            if d["commit_id"] == "None":
                d["commit_id"] = None
            rows.append(d)
    return rows


def download_patch(commit: str, repo: str) -> tuple[str, str | None]:
    cache = PATCH_CACHE / repo.replace("/", "__") / f"{commit}.patch"
    if cache.exists() and cache.stat().st_size:
        return commit, None
    url = f"https://github.com/{repo}/commit/{commit}.patch"
    err = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "GRACE-B3-source-recovery/1.0"})
            with urllib.request.urlopen(req, timeout=45) as resp:
                payload = resp.read()
            if not payload.startswith(b"From "):
                raise ValueError(f"unexpected patch response: {payload[:100]!r}")
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_bytes(payload)
            return commit, None
        except Exception as exc:  # keep per-commit failure in the review queue
            err = f"{type(exc).__name__}:{exc}"
            time.sleep(min(2 ** attempt, 8))
    return commit, err


def parse_patch(text: str) -> tuple[str, str, list[dict[str, Any]]]:
    head, _, rest = text.partition("diff --git ")
    subject = ""
    body = ""
    for line in head.splitlines():
        if line.startswith("Subject: "):
            subject = line.removeprefix("Subject: ").strip()
        if line.startswith("    "):
            body += line[4:] + "\n"
    sections = []
    pieces = re.split(r"(?m)^diff --git a/", rest)
    for piece in pieces:
        if not piece.strip():
            continue
        path, _, content = piece.partition(" b/")
        path = path.splitlines()[0].strip() if path else ""
        if path.startswith("a/"):
            path = path[2:]
        if not path:
            continue
        hunks = []
        lines = content.splitlines()
        i = 0
        while i < len(lines):
            m = HUNK_RE.match(lines[i])
            if not m:
                i += 1
                continue
            old_line = int(m.group(1))
            old_count = int(m.group(2) or 1)
            suffix = m.group(5).strip()
            hunk_lines = [lines[i]]
            old_parts, new_parts = [], []
            i += 1
            while i < len(lines) and not lines[i].startswith("@@ ") and not lines[i].startswith("diff --git "):
                line = lines[i]
                if line.startswith(" "):
                    old_parts.append(line[1:]); new_parts.append(line[1:])
                elif line.startswith("-") and not line.startswith("---"):
                    old_parts.append(line[1:])
                elif line.startswith("+") and not line.startswith("+++"):
                    new_parts.append(line[1:])
                elif line.startswith("\\"):
                    pass
                else:
                    break
                hunk_lines.append(line)
                i += 1
            hunks.append({
                "old_start": old_line, "old_count": old_count, "suffix": suffix,
                "old_tokens": tokenize("\n".join(old_parts)),
                "new_tokens": tokenize("\n".join(new_parts)),
                "new_text": "\n".join(new_parts),
                "patch_hunk": "\n".join(hunk_lines),
            })
        sections.append({"path": path, "hunks": hunks})
    return subject, body.strip(), sections


def all_positions(hay: list[str], needle: list[str]) -> list[int]:
    if not needle:
        return []
    return [i for i in range(len(hay) - len(needle) + 1) if hay[i : i + len(needle)] == needle]


def function_name(code_tokens: list[str]) -> str | None:
    for i, tok in enumerate(code_tokens[:-1]):
        if tok == "(" and i > 0 and re.fullmatch(r"[A-Za-z_]\w*", code_tokens[i - 1]):
            return code_tokens[i - 1]
    return None


def patch_candidate(row: dict[str, Any], patch_error: str | None) -> dict[str, Any]:
    commit = row.get("commit_id")
    repo = PATCH_REPOS.get(str(row.get("project", "")).lower())
    out = {
        "id": row["id"], "dataset": row["dataset"], "project": row["project"],
        "source_id": row["source_id"], "label_before": 1, "commit_id": commit,
        "source_code": row["func"], "source_code_sha256": sha256(row["func"]),
        "review_status": "PENDING_REVIEW", "review_decision": None,
        "reviewer": None, "review_notes": None, "patch_status": "UNRESOLVED",
        "repo": repo, "source_commit_url": f"https://github.com/{repo}/commit/{commit}" if repo and commit else None,
        "patch_file": None, "commit_subject": None, "commit_message": None,
        "patched_code": None, "patch_hunks": [], "failure_reason": None,
    }
    if not commit:
        out["failure_reason"] = "FROZEN_REVEAL_DONOR_HAS_NO_COMMIT_ID_OR_REPOSITORY_PATH"
        return out
    if not repo:
        out["failure_reason"] = f"UNMAPPED_PROJECT:{row.get('project')}"
        return out
    if patch_error:
        out["failure_reason"] = "PATCH_DOWNLOAD_FAILED: " + patch_error
        return out
    cache = PATCH_CACHE / repo.replace("/", "__") / f"{commit}.patch"
    try:
        text = cache.read_text(encoding="utf-8", errors="replace")
        subject, body, sections = parse_patch(text)
    except Exception as exc:
        out["failure_reason"] = f"PATCH_PARSE_FAILED:{type(exc).__name__}:{exc}"
        return out
    out["commit_subject"] = subject
    out["commit_message"] = body
    original_spans = tokens_with_spans(row["func"])
    original = [x[0] for x in original_spans]
    fname = function_name(original)
    out["function_name"] = fname
    matched = []
    for section in sections:
        applicable = []
        for hunk in section["hunks"]:
            old = hunk["old_tokens"]
            positions = all_positions(original, old)
            if not positions:
                continue
            hname = fname and re.search(rf"\b{re.escape(fname)}\b", hunk["suffix"])
            # A hunk is linked only by the actual function name or by a unique
            # old-side token context occurring in this donor function.
            if hname or len(positions) == 1:
                applicable.append((positions[0], hunk, len(positions)))
        if applicable:
            matched.append((section["path"], applicable))
    if not matched:
        out["failure_reason"] = "NO_PATCH_HUNK_CONTEXT_MATCHES_DONOR_FUNCTION"
        return out
    # Restrict to the section with most applicable hunks, prefer a named function match.
    matched.sort(key=lambda x: (-len(x[1]), x[0]))
    path, applicable = matched[0]
    applicable.sort(key=lambda x: x[0], reverse=True)
    patched_raw = row["func"]
    overlap = False
    hunk_records = []
    occupied: list[tuple[int, int]] = []
    for pos, hunk, occurrences in applicable:
        old = hunk["old_tokens"]
        end = pos + len(old)
        if any(max(pos, a) < min(end, b) for a, b in occupied):
            continue
        start_char = original_spans[pos][1]
        end_char = original_spans[end - 1][2]
        replacement_lines = hunk["new_text"].splitlines()
        if replacement_lines:
            # The original prefix retains indentation on the first line.
            replacement_lines[0] = replacement_lines[0].lstrip(" \t")
        replacement = "\n".join(replacement_lines)
        patched_raw = patched_raw[:start_char] + replacement + patched_raw[end_char:]
        occupied.append((pos, end))
        overlap = True
        hunk_records.append({"suffix": hunk["suffix"], "patch_hunk": hunk["patch_hunk"],
                             "old_token_occurrences": occurrences})
    if not overlap:
        out["failure_reason"] = "PATCH_HUNKS_MATCHED_BUT_COULD_NOT_BE_APPLIED"
        return out
    # Preserve the donor's formatting outside the exact patch hunk.
    out.update({
        "patch_file": path, "function_name": fname,
        "patched_code": patched_raw, "patched_code_sha256": sha256(patched_raw),
        "patch_hunks": hunk_records, "patch_status": "PAIR_EXTRACTED_REVIEW_REQUIRED",
        "failure_reason": None,
    })
    if tokenize(patched_raw) == original:
        out["patch_status"] = "PATCH_FOUND_BUT_NO_FUNCTION_CODE_CHANGE"
        out["failure_reason"] = "Commit hunk context matched but reconstructed function did not change"
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="diagnostic cap; default processes all finalized train donors")
    ap.add_argument("--workers", type=int, default=24)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    devign = load_finalized_vulnerable_train("devign")
    reveal = load_finalized_vulnerable_train("reveal")
    if args.limit:
        devign, reveal = devign[:args.limit], reveal[:args.limit]
    print(f"scope: Devign={len(devign)}, ReVeal={len(reveal)}", flush=True)
    unique: dict[tuple[str, str], None] = {}
    for row in devign:
        repo = PATCH_REPOS.get(str(row["project"]).lower())
        if row.get("commit_id") and repo:
            unique[(repo, row["commit_id"])] = None
    download_errors: dict[tuple[str, str], str] = {}
    commit_to_repo: dict[str, str] = {}
    for repo, commit in unique:
        commit_to_repo[commit] = repo
    print(f"downloading {len(unique)} distinct source patches with {args.workers} workers", flush=True)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(download_patch, commit, repo) for repo, commit in unique]
        for i, fut in enumerate(as_completed(futures), 1):
            commit, err = fut.result()
            repo = commit_to_repo[commit]
            if err:
                download_errors[(repo, commit)] = err
            if i % 250 == 0:
                print(f"patches downloaded {i}/{len(unique)}; errors={len(download_errors)}", flush=True)
    results = []
    for i, row in enumerate(devign, 1):
        repo = PATCH_REPOS.get(str(row["project"]).lower(), "")
        results.append(patch_candidate(row, download_errors.get((repo, row.get("commit_id")))))
        if i % 500 == 0:
            print(f"Devign candidates reconstructed {i}/{len(devign)}", flush=True)
    reveal_rows = [patch_candidate(row, None) for row in reveal]
    write_jsonl(OUT / "devign_patched_candidates.jsonl", results)
    write_jsonl(OUT / "devign_patched_review_pairs.jsonl",
                [r for r in results if r["patch_status"] == "PAIR_EXTRACTED_REVIEW_REQUIRED"])
    write_jsonl(OUT / "devign_unresolved_review_queue.jsonl",
                [r for r in results if r["patch_status"] != "PAIR_EXTRACTED_REVIEW_REQUIRED"])
    write_jsonl(OUT / "reveal_unresolved_vulnerable_train.jsonl", reveal_rows)
    with (OUT / "review_decision_template.csv").open("w", encoding="utf-8-sig", newline="") as f:
        fields = ["id", "dataset", "project", "source_id", "function_name", "commit_id",
                  "source_commit_url", "patch_file", "commit_subject", "patch_status",
                  "review_status", "reviewer", "review_decision", "review_notes", "failure_reason"]
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in [*results, *reveal_rows]:
            writer.writerow(row)
    dcounts = Counter(r["patch_status"] for r in results)
    rcounts = Counter(r["patch_status"] for r in reveal_rows)
    reasons = Counter(r["failure_reason"] for r in results if r["failure_reason"])
    report = {
        "method": "commit-patch-hunk-token-reconstruction-v1",
        "created_date": "2026-11-08",
        "scope": "finalized frozen train donors with target=1 only",
        "review_policy": "all extracted pairs remain PENDING_REVIEW; none are reviewer-approved",
        "devign": {"finalized_vulnerable_donors": len(devign), "unique_commit_patches": len(unique),
                   "download_failures": len(download_errors), "status_counts": dict(dcounts),
                   "unresolved_reasons": dict(reasons)},
        "reveal": {"finalized_vulnerable_donors": len(reveal),
                   "donors_with_commit_id": sum(bool(r.get("commit_id")) for r in reveal),
                   "status_counts": dict(rcounts)},
        "source_files": {ds: str(FREEZE / ds / "train_raw.jsonl") for ds in ("devign", "reveal")},
    }
    (OUT / "recovery_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "patch_download_errors.json").write_text(json.dumps({f"{r}:{c}": e for (r, c), e in download_errors.items()}, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
