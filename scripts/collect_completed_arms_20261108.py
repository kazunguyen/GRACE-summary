"""Read-only six-kernel harvest verification with isolated per-account credentials.

Downloads current evidence into a NEW directory and compares bytes with the local
harvest. Never changes a remote kernel, dataset, or historical local output.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    "huuhieu3333": ("kaggle_huuhieu_config", ["grace-b1-full-test", "grace-b2-rep-test"]),
    "tomandjerry223": ("kaggle_tomandjerry223_config", ["grace-b2-labelonly-test", "grace-b2-nolabel-test"]),
    "lznt123": ("kaggle_lznt123_config", ["grace-b3-validation", "grace-b1-shuf-test"]),
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def worker(user, out):
    folder, slugs = TARGETS[user]
    config = ROOT / "Runs-management" / folder / "kaggle.json"
    auth = json.loads(config.read_text(encoding="utf-8"))
    for name in ["KAGGLE_API_TOKEN", "KAGGLE_USERNAME", "KAGGLE_KEY"]:
        os.environ.pop(name, None)
    os.environ.update(KAGGLE_CONFIG_DIR=str(config.parent), KAGGLE_USERNAME=auth["username"], KAGGLE_KEY=auth["key"], PYTHONIOENCODING="utf-8")
    if auth["key"].startswith("KGAT_"):
        os.environ["KAGGLE_API_TOKEN"] = auth["key"]
    from kaggle.api.kaggle_api_extended import KaggleApi
    from kagglesdk.kernels.types.kernels_api_service import ApiListKernelSessionOutputRequest
    import requests
    api = KaggleApi()
    api.authenticate()
    result = []

    def clean(value):
        return str(value).replace(auth["key"], "[REDACTED]")

    for slug in slugs:
        ref = user + "/" + slug
        dest = out / user / slug
        dest.mkdir(parents=True)
        entry = {"ref": ref, "checked_at_utc": datetime.now(timezone.utc).isoformat(), "files": []}
        try:
            state = api.kernels_status(ref)
            entry["status"] = str(getattr(state, "status", state))
            pull = subprocess.run(["kaggle", "kernels", "pull", ref, "--metadata", "-p", str(dest / "source")],
                                  capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90)
            entry["pull_exit"] = pull.returncode
            if pull.returncode:
                entry["pull_error"] = clean(pull.stderr + pull.stdout)[:1000]
            with api.build_kaggle_client() as client:
                req = ApiListKernelSessionOutputRequest()
                req.user_name, req.kernel_slug = user, slug
                response = client.kernels.kernels_api_client.list_kernel_session_output(req)
            if response.log:
                (dest / "session.log").write_text(clean(response.log), encoding="utf-8")
            entry["remote_file_count"] = len(response.files)
            for item in response.files:
                name = item.file_name
                relative = Path(name)
                if relative.is_absolute() or ".." in relative.parts:
                    raise ValueError("Unsafe remote output path")
                selected = (name.endswith(("records.jsonl", "run_manifest.json", "evaluation.json", "runtime_provenance.json", "model_load_offload.log", "events.log", "exceptions.log", "batch_summary.json", "status.json"))
                            or relative.name in ["kaggle_inference.py", "kaggle_test_inference.py", "grace_runtime_contract.py", "inference_runtime_lock.json"]
                            or name.endswith(".zip") and "grace_" in relative.name and not name.endswith("grace_diagnostics.zip"))
                if not selected:
                    continue
                downloaded = requests.get(item.url, timeout=(15, 90))
                downloaded.raise_for_status()
                raw = downloaded.content
                target = dest / "output" / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
                prior = ROOT / "Runs-management/kernel_outputs_harvest" / (user + "_" + slug) / relative
                match = prior.exists() and digest(prior.read_bytes()) == digest(raw)
                entry["files"].append({"name": name, "bytes": len(raw), "sha256": digest(raw),
                                       "already_local": prior.exists(), "same_local_bytes": match})
        except Exception as exc:
            entry["error"] = clean(exc)[:1500]
        result.append(entry)
        (out / (user + ".json")).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(ref, entry.get("status"), "verified/downloaded", len(entry["files"]), "error", entry.get("error", ""), flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True)
    ap.add_argument("--worker", choices=list(TARGETS))
    args = ap.parse_args()
    out = (ROOT / args.out).resolve()
    if (ROOT / "Runs-management").resolve() not in out.parents:
        raise ValueError("Output must remain inside Runs-management")
    if args.worker:
        worker(args.worker, out)
        return
    if out.exists():
        raise FileExistsError("Preserve evidence: choose a new directory")
    out.mkdir(parents=True)
    (out / ".gitignore").write_text("*\n!.gitignore\n!*.json\n", encoding="utf-8")

    def run(user):
        p = subprocess.run([sys.executable, "-B", "-X", "utf8", str(Path(__file__).resolve()), "--out", str(out), "--worker", user],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
        print(p.stdout, end="", flush=True)
        if p.returncode:
            print(user, "collector_exit", p.returncode, flush=True)

    with ThreadPoolExecutor(max_workers=3) as pool:
        list(pool.map(run, TARGETS))
    entries = []
    for user in TARGETS:
        p = out / (user + ".json")
        if p.exists():
            entries.extend(json.loads(p.read_text(encoding="utf-8")))
    (out / "collection.json").write_text(json.dumps({"collected_at_utc": datetime.now(timezone.utc).isoformat(), "read_only": True, "kernels": entries}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if entries and all("10013" in e.get("error", "") for e in entries):
        raise SystemExit(3)


if __name__ == "__main__":
    main()
