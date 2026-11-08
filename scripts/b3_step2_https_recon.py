#!/usr/bin/env python3
"""Step 2: HTTPS Reconnaissance with valid trusted CA bundle (certifi).

Fixes the Windows Python OpenSSL trusted store issue by using certifi.where(),
maintaining strict certificate verification and hostname checking.
Fetches and audits commit records for Devign prioritized candidates into the target release.
Separates cache hits from live network requests in logging (addressing audit finding F06).
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import certifi

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RELEASE_DIR = ROOT / "Runs-management" / "b3_verified_patch_v1" / "release_20261108_v3"
CANDIDATES_FILE = (
    ROOT
    / "Runs-management"
    / "agy_b3_safe_codegen_20261108"
    / "local_discovery"
    / "devign"
    / "prioritized_candidates.json"
)
PRIOR_CACHE_DIR = (
    ROOT
    / "Runs-management"
    / "b3_verified_patch_v1"
    / "release_20261108"
    / "discovery"
    / "devign"
    / "source_recon"
    / "cache"
)

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


class StrictNoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(
            req.full_url,
            code,
            f"Redirect to '{newurl}' is strictly forbidden by network security policy.",
            headers,
            fp,
        )


def compute_file_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def compute_bytes_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_40hex_commit(sha_str: str) -> bool:
    return bool(sha_str and isinstance(sha_str, str) and HEX40_PATTERN.match(sha_str.strip()))


def run_step2(release_dir: Path = DEFAULT_RELEASE_DIR):
    print(f"=== Step 2: HTTPS Source Reconnaissance (Target: {release_dir.name}) ===")
    out_dir = release_dir / "discovery" / "devign" / "source_recon"
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = out_dir / "cache"
    cache_dir.mkdir(exist_ok=True)

    # Pre-populate cache from prior verified cache if available
    if PRIOR_CACHE_DIR.is_dir():
        for cf in PRIOR_CACHE_DIR.glob("*.json"):
            target_cf = cache_dir / cf.name
            if not target_cf.exists():
                shutil.copy2(cf, target_cf)

    # 1. SSL Diagnosis
    ca_bundle = certifi.where()
    print(f"Using Trusted CA Bundle (certifi): {ca_bundle}")

    ssl_ctx = ssl.create_default_context(cafile=ca_bundle)
    ssl_ctx.verify_mode = ssl.CERT_REQUIRED
    ssl_ctx.check_hostname = True

    # 2. Read prioritized candidates
    with open(CANDIDATES_FILE, "r", encoding="utf-8") as f:
        candidates = json.load(f)

    print(f"Loaded {len(candidates)} prioritized candidates.")

    # 3. Build deduplicated list of commits to fetch (covering all candidates)
    commits_to_fetch = []
    seen = set()
    for cand in candidates:
        proj = cand["project"].lower()
        if proj not in PROJECT_REPO_MAP:
            continue
        repo = PROJECT_REPO_MAP[proj]
        for commit_key in ["vulnerable_commit", "patched_candidate_commit"]:
            c_sha = cand.get(commit_key, "").strip()
            if validate_40hex_commit(c_sha) and (repo, c_sha) not in seen:
                seen.add((repo, c_sha))
                commits_to_fetch.append((repo, c_sha))

    print(f"Total unique commits to cover: {len(commits_to_fetch)}")

    # 4. Build Opener with Trusted SSL Context
    https_handler = urllib.request.HTTPSHandler(context=ssl_ctx)
    opener = urllib.request.build_opener(StrictNoRedirectHandler(), https_handler)

    request_logs = []
    fetched_data = {}  # (repo, commit_sha) -> parsed dict or None
    last_req_time = 0.0

    cache_hit_count = 0
    network_attempt_count = 0
    network_success_count = 0
    network_fail_count = 0

    for idx, (repo, c_sha) in enumerate(commits_to_fetch, start=1):
        url = f"https://api.github.com/repos/{repo}/commits/{c_sha}"
        cache_file = cache_dir / f"{c_sha}.json"
        now_utc = datetime.now(timezone.utc).isoformat()

        if cache_file.is_file() and cache_file.stat().st_size > 0:
            raw_bytes = cache_file.read_bytes()
            resp_bytes_len = len(raw_bytes)
            resp_sha256 = compute_bytes_sha256(raw_bytes)
            try:
                parsed_payload = json.loads(raw_bytes.decode("utf-8"))
            except Exception:
                parsed_payload = None

            cache_hit_count += 1
            print(f"[{idx}/{len(commits_to_fetch)}] Cache hit: {repo} commit {c_sha[:8]}")
            request_logs.append({
                "url": url,
                "source": "cache",
                "http_status": "HTTP_200",
                "sha256": resp_sha256,
                "bytes": resp_bytes_len,
                "timestamp_utc": now_utc,
            })
            fetched_data[(repo, c_sha)] = parsed_payload
        else:
            elapsed = time.time() - last_req_time
            if elapsed < MIN_INTER_REQUEST_DELAY:
                time.sleep(MIN_INTER_REQUEST_DELAY - elapsed)

            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": ACCEPT_HEADER,
                },
            )

            http_status_str = "UNKNOWN"
            resp_sha256 = ""
            resp_bytes_len = 0
            parsed_payload = None
            network_attempt_count += 1

            print(f"[{idx}/{len(commits_to_fetch)}] Network fetch: {repo} commit {c_sha[:8]}...")
            try:
                with opener.open(req, timeout=TIMEOUT_SECONDS) as response:
                    last_req_time = time.time()
                    status_code = response.getcode()
                    http_status_str = f"HTTP_{status_code}"
                    raw_bytes = response.read(MAX_RESPONSE_BYTES + 1)
                    if len(raw_bytes) > MAX_RESPONSE_BYTES:
                        http_status_str = "RESPONSE_SIZE_EXCEEDED"
                        network_fail_count += 1
                    else:
                        resp_bytes_len = len(raw_bytes)
                        resp_sha256 = compute_bytes_sha256(raw_bytes)
                        with open(cache_file, "wb") as cf:
                            cf.write(raw_bytes)
                        parsed_payload = json.loads(raw_bytes.decode("utf-8"))
                        network_success_count += 1
            except urllib.error.HTTPError as he:
                last_req_time = time.time()
                http_status_str = f"HTTP_ERROR_{he.code}"
                network_fail_count += 1
                print(f"  HTTP error {he.code}: {he.reason}")
                if he.code in (403, 429):
                    print("  Rate limit encountered! Halting fetch loop.")
                    request_logs.append({
                        "url": url,
                        "source": "network",
                        "http_status": http_status_str,
                        "sha256": "",
                        "bytes": 0,
                        "timestamp_utc": now_utc,
                    })
                    break
            except Exception as exc:
                last_req_time = time.time()
                http_status_str = f"URL_ERROR_{exc}"
                network_fail_count += 1
                print(f"  Request error: {exc}")

            request_logs.append({
                "url": url,
                "source": "network",
                "http_status": http_status_str,
                "sha256": resp_sha256,
                "bytes": resp_bytes_len,
                "timestamp_utc": now_utc,
            })
            fetched_data[(repo, c_sha)] = parsed_payload

    # Write request log
    with open(out_dir / "request_log.jsonl", "w", encoding="utf-8") as f:
        for rlog in request_logs:
            f.write(json.dumps(rlog) + "\n")

    # 5. Build source_checks.jsonl
    source_checks = []
    cases_with_missing_responses = 0

    for cand in candidates:
        proj = cand["project"].lower()
        if proj not in PROJECT_REPO_MAP:
            continue
        repo = PROJECT_REPO_MAP[proj]
        v_sha = cand.get("vulnerable_commit", "")
        p_sha = cand.get("patched_candidate_commit", "")

        v_data = fetched_data.get((repo, v_sha))
        p_data = fetched_data.get((repo, p_sha))

        has_v = v_data is not None
        has_p = p_data is not None
        if not (has_v and has_p):
            cases_with_missing_responses += 1

        v_msg = v_data.get("commit", {}).get("message", "") if v_data else ""
        p_msg = p_data.get("commit", {}).get("message", "") if p_data else ""

        v_parents = [p.get("sha") for p in v_data.get("parents", [])] if v_data else []
        p_parents = [p.get("sha") for p in p_data.get("parents", [])] if p_data else []

        v_files = [f.get("filename") for f in v_data.get("files", [])] if v_data else []
        p_files = [f.get("filename") for f in p_data.get("files", [])] if p_data else []

        shared_files = list(set(v_files) & set(p_files))

        # Check if direct parent edge
        is_direct_parent = (v_sha in p_parents) or (p_sha in v_parents) if (has_v and has_p) else False

        status = (
            "UNVERIFIED_SOURCE_RECONNAISSANCE_ONLY"
            if (has_v and has_p)
            else "UNRESOLVED_SOURCE_FETCH"
        )

        check_record = {
            "vulnerable_id": cand["vulnerable_id"],
            "patched_candidate_id": cand["patched_candidate_id"],
            "project": proj,
            "function_hint": cand["function_hint"],
            "vulnerable_commit": v_sha,
            "patched_candidate_commit": p_sha,
            "vulnerable_query_url": f"https://api.github.com/repos/{repo}/commits/{v_sha}",
            "patched_query_url": f"https://api.github.com/repos/{repo}/commits/{p_sha}",
            "vulnerable_cache_reference": f"cache/{v_sha}.json" if has_v else None,
            "patched_cache_reference": f"cache/{p_sha}.json" if has_p else None,
            "vulnerable_commit_message": v_msg[:200],
            "patched_commit_message": p_msg[:200],
            "vulnerable_parent_shas": v_parents,
            "patched_parent_shas": p_parents,
            "vulnerable_changed_filenames": v_files,
            "patched_changed_filenames": p_files,
            "shared_files": shared_files,
            "is_direct_parent_edge": is_direct_parent,
            "status": status,
            "limitations": (
                "Dataset revision can be unrelated; function bytes, file paths, security relations, "
                "and dual reviews are not authenticated. Never infer a fix relationship from "
                "security words or direct ancestry alone."
            ),
        }
        source_checks.append(check_record)

    with open(out_dir / "source_checks.jsonl", "w", encoding="utf-8") as f:
        for sc in source_checks:
            f.write(json.dumps(sc, ensure_ascii=False) + "\n")

    summary = {
        "dataset": "devign",
        "total_commits_requested": len(commits_to_fetch),
        "cache_hits": cache_hit_count,
        "network_requests_attempted": network_attempt_count,
        "network_requests_successful": network_success_count,
        "network_requests_failed": network_fail_count,
        "ssl_ca_bundle_used": ca_bundle,
        "trusted_verification": True,
        "source_checks_count": len(source_checks),
        "cases_with_both_responses": len(source_checks) - cases_with_missing_responses,
        "cases_with_missing_responses": cases_with_missing_responses,
        "direct_parent_edges_found": sum(1 for sc in source_checks if sc["is_direct_parent_edge"]),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": "STEP2_RECON_COMPLETED",
    }
    with open(out_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("Step 2 Summary:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Step 2: HTTPS reconnaissance")
    parser.add_argument("--release-dir", type=Path, default=DEFAULT_RELEASE_DIR, help="Output release directory")
    args = parser.parse_args()
    run_step2(args.release_dir)
