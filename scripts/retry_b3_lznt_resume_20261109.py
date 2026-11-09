"""Retry the corrected B3 checkpoint-resume notebook after Kaggle queue cancellation."""
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import deploy_b3_lznt_linuxfix_20261109 as deploy
import launch_huuhieu_b1shuf_b3_20261108 as transport

OWNER = "lznt123"
KIND = "b3-new-dual-resume-v2-retry1"
BASE = ROOT / "Runs-management/b3_lznt_resume_retry_20261109"
STAGE = BASE / KIND
SOURCE = ROOT / "Runs-management/b3_lznt_resume_v2_20261109/b3-new-dual-resume-v2-20261109"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def api_client():
    return deploy.api_client()


def prepare():
    if STAGE.exists():
        raise FileExistsError("Retry stage already exists; preserve it and use a new retry index")
    previous_status = read(SOURCE / "status.json")
    if not previous_status["status"].endswith("CANCEL_ACKNOWLEDGED"):
        raise ValueError("Previous queued session is not confirmed cancelled")
    shutil.copytree(SOURCE / "kernel", STAGE / "kernel")
    metadata_path = STAGE / "kernel/kernel-metadata.json"
    metadata = read(metadata_path)
    metadata["id"] = previous_status["ref"]
    write(metadata_path, metadata)
    delivery = read(SOURCE / "delivery.json")
    delivery["ref"] = previous_status["ref"]
    assert hashlib.sha256((STAGE / "kernel/notebook.ipynb").read_bytes()).hexdigest() == delivery["notebook_sha256"]
    delivery["retry_of_status"] = previous_status
    delivery["retry_reason"] = "Kaggle acknowledged cancellation while the initial v2 kernel was queued"
    write(STAGE / "delivery.json", delivery)
    retry_receipt = {
        "previous_kernel": previous_status["ref"],
        "previous_status": previous_status["status"],
        "new_version_expected": 2,
        "notebook_sha256": delivery["notebook_sha256"],
        "dataset_sources": read(STAGE / "kernel/kernel-metadata.json")["dataset_sources"],
        "checkpoint_dataset_reused": True,
    }
    write(STAGE / "retry_receipt.json", retry_receipt)
    preflight = read(ROOT / "Runs-management/b3_lznt_resume_v2_20261109/cpu_preflight.json")
    write(BASE / "cpu_preflight.json", preflight)
    print(json.dumps(retry_receipt, indent=2))


def remote(action):
    transport.BASE = BASE
    transport.OWNER = OWNER
    transport.api_client = api_client
    transport.remote(KIND, action)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "launch", "verify", "status", "output"])
    action = parser.parse_args().action
    if action == "prepare":
        prepare()
    else:
        remote(action)
