#!/usr/bin/env python3
"""
fetch_public_source.py

Public source reconnaissance fetcher for candidate pair verification.
Python 3.10 standard library only.

Strict Constraints:
- CLI: --candidates PATH, --out NEW_DIR, --max-requests INT (default 16)
- Rejects existing output directory without alteration.
- Destination allowlist: api.github.com ONLY.
  * ffmpeg -> FFmpeg/FFmpeg
  * qemu -> qemu/qemu
- Strict full 40-hex commit SHA validation.
- Never transmits private data, IDs, or tokens in query URLs.
- Disallows redirects (custom HTTPRedirectHandler).
- Enforces User-Agent and Accept headers.
- Response cap: 5 MiB; timeout: 20s; inter-request delay >= 1.0s.
- Halts immediately on HTTP 403 or 429 without retries.
- Validates returned commit SHA against requested commit SHA.
- Archives raw bytes in cache with SHA-256 checksums.
- Logs all attempts to request_log.jsonl.
- Generates source_checks.jsonl with explicit unverified status and limitations.
- Outputs summary.json with counts, file hashes, and limitations.
- Never infers fix relationships from security keywords or direct parentage alone.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


HEX40_PATTERN = re.compile(r"^[0-9a-fA-F]{40}$")
MAX_RESPONSE_BYTES = 5 * 1024 * 1024  # 5 MiB cap
TIMEOUT_SECONDS = 20.0
MIN_INTER_REQUEST_DELAY = 1.0
USER_AGENT = "GRACE-source-audit/1.0"
ACCEPT_HEADER = "application/vnd.github+json"

PROJECT_REPO_MAP = {
    "ffmpeg": "FFmpeg/FFmpeg",
    "qemu": "qemu/qemu",
}

EXPLICIT_LIMITATIONS = (
    "Dataset revision can be unrelated; function bytes, file paths, security relations, "
    "and dual reviews are not authenticated. Never infer a fix relationship from "
    "security words or direct ancestry alone."
)


class StrictNoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """HTTP redirect handler that strictly refuses all redirects."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(
            req.full_url,
            code,
            f"Redirect to '{newurl}' is strictly forbidden by network security policy.",
            headers,
            fp,
        )


def compute_file_sha256(filepath: str) -> str:
    """Compute SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_bytes_sha256(data: bytes) -> str:
    """Compute SHA-256 hash of raw bytes."""
    return hashlib.sha256(data).hexdigest()


def validate_40hex_commit(sha: str) -> bool:
    """Validate that a string is exactly a 40-hexadecimal commit hash."""
    return bool(sha and isinstance(sha, str) and HEX40_PATTERN.match(sha.strip()))


def parse_args() -> argparse.Namespace:
    """Parse and validate command line arguments."""
    parser = argparse.ArgumentParser(
        description="Fetch public commit metadata for reconnaissance without external inference."
    )
    parser.add_argument(
        "--candidates",
        required=True,
        type=str,
        help="Path to local candidates JSONL file.",
    )
    parser.add_argument(
        "--out",
        required=True,
        type=str,
        help="Path to new output directory (must not exist).",
    )
    parser.add_argument(
        "--max-requests",
        type=int,
        default=16,
        help="Maximum number of HTTP requests allowed (default: 16).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # 1. Output directory safety check: reject existing out without alteration
    out_dir = os.path.abspath(args.out)
    if os.path.exists(out_dir):
        sys.stderr.write(
            f"Error: Output directory '{out_dir}' already exists. "
            f"Refusing to alter or overwrite existing path.\n"
        )
        sys.exit(1)

    candidates_path = os.path.abspath(args.candidates)
    if not os.path.isfile(candidates_path):
        sys.stderr.write(f"Error: Candidates file '{candidates_path}' does not exist.\n")
        sys.exit(1)

    input_sha256 = compute_file_sha256(candidates_path)

    # 2. Parse candidates JSONL
    candidates_read = 0
    records_by_project = {"ffmpeg": [], "qemu": []}
    malformed_candidate_rows = 0

    with open(candidates_path, "r", encoding="utf-8") as f:
        for line_idx, line in enumerate(f, start=1):
            line_str = line.strip()
            if not line_str:
                continue
            candidates_read += 1
            try:
                row = json.loads(line_str)
            except Exception:
                malformed_candidate_rows += 1
                continue

            if not isinstance(row, dict):
                malformed_candidate_rows += 1
                continue

            proj = str(row.get("project", "")).strip().lower()
            if proj not in PROJECT_REPO_MAP:
                continue

            v_commit = str(row.get("vulnerable_commit", "")).strip()
            p_commit = str(row.get("patched_candidate_commit", "")).strip()

            if not (validate_40hex_commit(v_commit) and validate_40hex_commit(p_commit)):
                continue

            chars_val = row.get("characters")
            try:
                chars_num = int(chars_val)
            except (ValueError, TypeError):
                chars_num = float("inf")

            v_id = str(row.get("vulnerable_id", ""))
            p_id = str(row.get("patched_candidate_id", ""))

            clean_entry = {
                "project": proj,
                "function_hint": str(row.get("function_hint", "")),
                "vulnerable_id": v_id,
                "patched_candidate_id": p_id,
                "vulnerable_commit": v_commit,
                "patched_candidate_commit": p_commit,
                "characters": chars_num,
                "status": str(row.get("status", "")),
                "raw_row": row,
            }
            records_by_project[proj].append(clean_entry)

    # 3. Select up to 4 shortest pairs per recognized project, stable ID tiebreak, total <= 8
    selected_candidates = []
    for proj in ["ffmpeg", "qemu"]:
        proj_entries = records_by_project[proj]
        proj_entries.sort(
            key=lambda item: (
                item["characters"],
                item["vulnerable_id"],
                item["patched_candidate_id"],
                item["vulnerable_commit"],
                item["patched_candidate_commit"],
            )
        )
        selected_for_proj = proj_entries[:4]
        selected_candidates.extend(selected_for_proj)

    # Limit total selection to at most 8
    selected_candidates = selected_candidates[:8]

    # 4. De-duplicate commit GETs across selected pairs
    commits_to_fetch = []
    seen_commit_keys = set()

    for cand in selected_candidates:
        proj = cand["project"]
        repo = PROJECT_REPO_MAP[proj]
        for commit_sha in [cand["vulnerable_commit"], cand["patched_candidate_commit"]]:
            key = (repo, commit_sha)
            if key not in seen_commit_keys:
                seen_commit_keys.add(key)
                commits_to_fetch.append(key)

    # 5. Initialize output structure
    os.makedirs(out_dir, exist_ok=False)
    cache_dir = os.path.join(out_dir, "cache")
    os.makedirs(cache_dir, exist_ok=True)

    request_log_path = os.path.join(out_dir, "request_log.jsonl")
    source_checks_path = os.path.join(out_dir, "source_checks.jsonl")
    summary_path = os.path.join(out_dir, "summary.json")

    opener = urllib.request.build_opener(StrictNoRedirectHandler())

    request_logs = []
    fetched_data_by_commit = {}  # key: (repo, commit_sha) -> dict of parsed response or None
    cached_file_relative_paths = {}
    rate_limited_count = 0
    requests_attempted = 0
    available_responses = 0
    stop_fetch_loop = False
    last_request_time = 0.0

    # 6. Execute fetch loop with rate limits and response caps
    for repo, commit_sha in commits_to_fetch:
        if requests_attempted >= args.max_requests:
            break

        if stop_fetch_loop:
            break

        # Enforce at least 1.0s delay between calls
        now = time.time()
        elapsed = now - last_request_time
        if elapsed < MIN_INTER_REQUEST_DELAY:
            time.sleep(MIN_INTER_REQUEST_DELAY - elapsed)

        url = f"https://api.github.com/repos/{repo}/commits/{commit_sha}"
        parsed_url = urllib.parse.urlparse(url)
        if parsed_url.netloc != "api.github.com":
            continue

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": ACCEPT_HEADER,
            },
            method="GET",
        )

        requests_attempted += 1
        last_request_time = time.time()
        req_timestamp = datetime.now(timezone.utc).isoformat()

        http_status_or_err = "unknown"
        raw_body = b""
        response_sha256 = ""
        response_byte_count = 0
        is_success = False

        try:
            with opener.open(req, timeout=TIMEOUT_SECONDS) as resp:
                status_code = resp.status
                http_status_or_err = str(status_code)

                # Read up to MAX_RESPONSE_BYTES + 1 to detect oversize
                chunks = []
                total_read = 0
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    chunks.append(chunk)
                    total_read += len(chunk)
                    if total_read > MAX_RESPONSE_BYTES:
                        raise ValueError(f"Response exceeded 5 MiB cap ({total_read} bytes read)")

                raw_body = b"".join(chunks)
                response_byte_count = len(raw_body)
                response_sha256 = compute_bytes_sha256(raw_body)

                if status_code == 200:
                    # Parse JSON and validate response sha equals requested commit
                    try:
                        parsed_json = json.loads(raw_body.decode("utf-8"))
                        returned_sha = str(parsed_json.get("sha", "")).strip()
                        if returned_sha.lower() == commit_sha.lower():
                            is_success = True
                            cache_filename = f"{commit_sha}.json"
                            cache_filepath = os.path.join(cache_dir, cache_filename)
                            with open(cache_filepath, "wb") as cf:
                                cf.write(raw_body)
                            rel_cache_path = os.path.join("cache", cache_filename).replace("\\", "/")
                            cached_file_relative_paths[(repo, commit_sha)] = rel_cache_path
                            fetched_data_by_commit[(repo, commit_sha)] = parsed_json
                            available_responses += 1
                        else:
                            http_status_or_err = f"SHA_MISMATCH: got {returned_sha}"
                    except Exception as parse_err:
                        http_status_or_err = f"MALFORMED_JSON: {parse_err}"

        except urllib.error.HTTPError as he:
            http_status_or_err = f"HTTP_{he.code}"
            if he.code in (403, 429):
                rate_limited_count += 1
                stop_fetch_loop = True
        except urllib.error.URLError as ue:
            http_status_or_err = f"URL_ERROR_{ue.reason}"
        except Exception as ex:
            http_status_or_err = f"ERROR_{type(ex).__name__}: {str(ex)}"

        log_entry = {
            "url": url,
            "http_status": http_status_or_err,
            "sha256": response_sha256,
            "bytes": response_byte_count,
            "timestamp_utc": req_timestamp,
        }
        request_logs.append(log_entry)

    # Write request_log.jsonl
    with open(request_log_path, "w", encoding="utf-8", newline="\n") as f_log:
        for entry in request_logs:
            f_log.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # 7. Build source_checks.jsonl
    source_checks = []
    direct_parent_edges_count = 0

    for cand in selected_candidates:
        proj = cand["project"]
        repo = PROJECT_REPO_MAP[proj]
        v_sha = cand["vulnerable_commit"]
        p_sha = cand["patched_candidate_commit"]

        v_url = f"https://api.github.com/repos/{repo}/commits/{v_sha}"
        p_url = f"https://api.github.com/repos/{repo}/commits/{p_sha}"

        v_cache_rel = cached_file_relative_paths.get((repo, v_sha), None)
        p_cache_rel = cached_file_relative_paths.get((repo, p_sha), None)

        v_data = fetched_data_by_commit.get((repo, v_sha))
        p_data = fetched_data_by_commit.get((repo, p_sha))

        # Extract commit messages (truncate <= 1500 chars)
        def extract_msg(data):
            if not data or not isinstance(data, dict):
                return ""
            commit_obj = data.get("commit", {})
            msg = commit_obj.get("message", "") if isinstance(commit_obj, dict) else ""
            return (msg[:1500] if len(msg) > 1500 else msg) if isinstance(msg, str) else ""

        # Extract parent SHAs
        def extract_parents(data):
            if not data or not isinstance(data, dict):
                return []
            parents = data.get("parents", [])
            if not isinstance(parents, list):
                return []
            shas = []
            for parent in parents:
                if isinstance(parent, dict) and "sha" in parent:
                    shas.append(str(parent["sha"]))
            return shas

        # Extract changed filenames
        def extract_files(data):
            if not data or not isinstance(data, dict):
                return []
            files = data.get("files", [])
            if not isinstance(files, list):
                return []
            names = []
            for file_item in files:
                if isinstance(file_item, dict) and "filename" in file_item:
                    names.append(str(file_item["filename"]))
            return names

        v_msg = extract_msg(v_data)
        p_msg = extract_msg(p_data)
        v_parents = extract_parents(v_data)
        p_parents = extract_parents(p_data)
        v_files = extract_files(v_data)
        p_files = extract_files(p_data)

        # Check whether one candidate revision is DIRECT parent of the other
        is_direct_parent_edge = False
        if p_data and (v_sha.lower() in [s.lower() for s in p_parents]):
            is_direct_parent_edge = True
        elif v_data and (p_sha.lower() in [s.lower() for s in v_parents]):
            is_direct_parent_edge = True

        if is_direct_parent_edge:
            direct_parent_edges_count += 1

        check_record = {
            "vulnerable_id": cand["vulnerable_id"],
            "patched_candidate_id": cand["patched_candidate_id"],
            "project": cand["project"],
            "function_hint": cand["function_hint"],
            "vulnerable_commit": v_sha,
            "patched_candidate_commit": p_sha,
            "vulnerable_query_url": v_url,
            "patched_query_url": p_url,
            "vulnerable_cache_reference": v_cache_rel,
            "patched_cache_reference": p_cache_rel,
            "vulnerable_commit_message": v_msg,
            "patched_commit_message": p_msg,
            "vulnerable_parent_shas": v_parents,
            "patched_parent_shas": p_parents,
            "vulnerable_changed_filenames": v_files,
            "patched_changed_filenames": p_files,
            "is_direct_parent_edge": is_direct_parent_edge,
            "status": "UNVERIFIED_SOURCE_RECONNAISSANCE_ONLY",
            "limitations": EXPLICIT_LIMITATIONS,
        }
        source_checks.append(check_record)

    # Write source_checks.jsonl
    with open(source_checks_path, "w", encoding="utf-8", newline="\n") as f_sc:
        for record in source_checks:
            f_sc.write(json.dumps(record, ensure_ascii=False) + "\n")

    # 8. Compute output hashes
    output_hashes = {
        "request_log.jsonl": compute_file_sha256(request_log_path),
        "source_checks.jsonl": compute_file_sha256(source_checks_path),
    }
    for (repo, commit_sha), rel_path in cached_file_relative_paths.items():
        full_p = os.path.join(out_dir, rel_path)
        if os.path.isfile(full_p):
            output_hashes[rel_path] = compute_file_sha256(full_p)

    # 9. Write summary.json
    summary_data = {
        "candidates_read": candidates_read,
        "candidates_selected": len(selected_candidates),
        "unique_commits_planned": len(commits_to_fetch),
        "requests_attempted": requests_attempted,
        "available_responses": available_responses,
        "direct_parent_edge_count": direct_parent_edges_count,
        "rate_limited_count": rate_limited_count,
        "rate_limit_halt_triggered": stop_fetch_loop,
        "verified_pairs": 0,
        "reviewed_pairs": 0,
        "input_hashes": {
            "candidates_jsonl": input_sha256,
        },
        "output_hashes": output_hashes,
        "limitations": EXPLICIT_LIMITATIONS,
    }

    with open(summary_path, "w", encoding="utf-8", newline="\n") as f_sum:
        json.dump(summary_data, f_sum, indent=2, ensure_ascii=False)
        f_sum.write("\n")


if __name__ == "__main__":
    main()
