"""Read-only Kaggle CLI collection, using each account's local config privately.

Never starts, pushes, cancels, or updates a kernel. Credentials stay in child
environment variables and are redacted from captured console messages.
"""
import argparse
import concurrent.futures
import csv
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from datetime import datetime, timezone
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CONFIGS = ["kaggle_huuhieu_config", "kaggle_tomandjerry223_config", "kaggle_lznt123_config"]
KNOWN = {
    "huuhieu3333": ["grace-b1-full-test", "grace-b2-rep-test"],
    "tomandjerry223": ["grace-b2-labelonly-test", "grace-b2-nolabel-test", "grace-b1-shuf-validation"],
    "lznt123": ["grace-b3-validation", "grace-b1-shuf-test", "grace-b3-nodiff-validation"],
}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True)
    ap.add_argument("--download", action="store_true")
    ap.add_argument("--status-only", action="store_true")
    ap.add_argument("--osf-only", action="store_true")
    args = ap.parse_args()
    out = (ROOT / args.out).resolve()
    if (ROOT / "Runs-management").resolve() not in out.parents or out.exists():
        raise ValueError("Use a new evidence directory inside Runs-management")
    out.mkdir(parents=True)
    (out / ".gitignore").write_text("*\n!.gitignore\n!collection.json\n!osf_summary.json\n", encoding="utf-8")
    cli = shutil.which("kaggle")
    if not cli:
        raise RuntimeError("Kaggle CLI missing")
    secrets = []
    configs = []
    for folder in CONFIGS:
        path = ROOT / "Runs-management" / folder / "kaggle.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        secrets.append(value["key"])
        configs.append((path.parent, value))

    def clean(text):
        for secret in secrets:
            text = text.replace(secret, "[REDACTED]")
        return re.sub(r"KGAT_[A-Za-z0-9_]+", "[REDACTED]", text)

    def run(env, cmd, timeout=90):
        try:
            result = subprocess.run([cli] + cmd, cwd=ROOT, env=env, capture_output=True,
                                    text=True, encoding="utf-8", errors="replace", timeout=timeout)
            return {"args": cmd, "exit_code": result.returncode,
                    "stdout": clean(result.stdout), "stderr": clean(result.stderr),
                    "checked_at_utc": datetime.now(timezone.utc).isoformat()}
        except subprocess.TimeoutExpired:
            return {"args": cmd, "exit_code": None, "error": "timeout"}

    def account(config):
        folder, value = config
        user, key = value["username"], value["key"]
        env = os.environ.copy()
        for k in ["KAGGLE_API_TOKEN", "KAGGLE_USERNAME", "KAGGLE_KEY"]:
            env.pop(k, None)
        env.update(KAGGLE_CONFIG_DIR=str(folder), KAGGLE_USERNAME=user, KAGGLE_KEY=key,
                   PYTHONIOENCODING="utf-8")
        if key.startswith("KGAT_"):
            env["KAGGLE_API_TOKEN"] = key
        listing = run(env, ["kernels", "list", "--mine", "--csv", "--page-size", "100", "--sort-by", "dateRun"])
        refs = {user + "/" + slug for slug in KNOWN[user]}
        if listing["exit_code"] == 0:
            try:
                for row in csv.DictReader(io.StringIO(listing["stdout"])):
                    ref = row.get("ref", "")
                    if ref.startswith(user + "/") and re.search(r"/grace-b[123]-", ref.lower()):
                        refs.add(ref)
            except (ValueError, csv.Error):
                pass
        results = []
        if listing["exit_code"] != 0 and "10013" in str(listing):
            return {"user": user, "listing": listing, "kernels": [], "network_blocked": True}
        for ref in sorted(refs):
            status = run(env, ["kernels", "status", ref])
            item = {"ref": ref, "status": status}
            print(ref, clean(status["stdout"].strip())[:180], clean(status["stderr"].strip())[:180], flush=True)
            if status["exit_code"] == 0 and not args.status_only:
                dest = out / user / ref.split("/")[1]
                item["pull"] = run(env, ["kernels", "pull", ref, "--metadata", "-p", str(dest / "source")])
                if args.download:
                    item["output"] = run(env, ["kernels", "output", ref, "-p", str(dest / "output")], timeout=240)
            results.append(item)
        return {"user": user, "listing": listing, "kernels": results}

    if args.osf_only:
        accounts = []
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            accounts = list(pool.map(account, configs))
    osf = {}
    for label, url in [("registration", "https://api.osf.io/v2/registrations/fqgh2/"),
                       ("node", "https://api.osf.io/v2/nodes/fqgh2/"),
                       ("node_registrations", "https://api.osf.io/v2/nodes/fqgh2/registrations/"),
                       ("page", "https://osf.io/fqgh2/")]:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=25) as response:
                raw = response.read()
            (out / ("osf_" + label + ".txt")).write_bytes(raw)
            osf[label] = {"url": url, "success": True, "bytes": len(raw)}
        except Exception as exc:
            osf[label] = {"url": url, "success": False, "error": clean(str(exc))}
    report = {"collected_at_utc": datetime.now(timezone.utc).isoformat(), "read_only": True,
              "accounts": accounts, "osf": osf}
    (out / "collection.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for a in accounts:
        print(a["user"], "list_exit", a["listing"]["exit_code"], "kernels", len(a["kernels"]), flush=True)
        for k in a["kernels"]:
            print(k["ref"], k["status"]["stdout"].strip()[:250], k["status"]["stderr"].strip()[:150], flush=True)
    print("OSF", json.dumps(osf, ensure_ascii=False), flush=True)
    if accounts and all(a.get("network_blocked") for a in accounts):
        raise SystemExit(3)


if __name__ == "__main__":
    main()
