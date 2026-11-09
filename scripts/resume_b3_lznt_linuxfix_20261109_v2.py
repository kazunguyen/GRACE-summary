"""Resume the verified B3 Devign/REVEAL validation checkpoints on lznt123."""
import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import b3_delivery_runtime as io
import deploy_b3_lznt_linuxfix_20261109 as parent
import launch_huuhieu_b1shuf_b3_20261108 as transport

PARENT = ROOT / "Runs-management/b3_lznt_linuxfix_20261109/b3_dual"
BASE = ROOT / "Runs-management/b3_lznt_resume_v2_20261109"
OWNER = "lznt123"
KIND = "b3-new-dual-resume-v2-20261109"
STAGE = BASE / KIND
CHECKPOINT_NAMES = {
    "devign": "B3_devign_validation_checkpoint.zip",
    "reveal": "B3_reveal_validation_checkpoint.zip",
}


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(io.encoded(value))


def prepare():
    transport.OWNER = OWNER
    if STAGE.exists():
        raise FileExistsError("Preserve prior resume stages; this stage already exists")
    delivery = read(PARENT / "delivery.json")
    dual_status = read(PARENT / "remote_output/b3_new_dual_validation_20261109/dual_status.json")
    assert dual_status["state"] == "checkpointed"
    assert dual_status["datasets"]["devign"]["state"] == "complete"
    assert dual_status["datasets"]["reveal"]["state"] == "checkpointed"
    assert dual_status["datasets"]["devign"]["records"] == 2732
    assert dual_status["datasets"]["reveal"]["records"] == 1713

    checkpoints = {}
    checkpoint_members = {}
    counts = {}
    for ds, name in CHECKPOINT_NAMES.items():
        archive = PARENT / "remote_output/b3_new_dual_validation_20261109" / name
        assert archive.is_file()
        with ZipFile(archive) as zf:
            assert zf.testzip() is None
        members = io.read_members(archive)
        checkpoint_members[ds] = {name: hashlib.sha256(raw).hexdigest()
                                  for name, raw in members.items()}
        root = read(PARENT / "roots" / f"{ds}.json")
        assert root["seal_sha256"] == io.seal(root)
        with tempfile.TemporaryDirectory(prefix=f"b3_{ds}_resume_audit_") as tmp:
            restored = Path(tmp) / ds
            io.restore_checkpoint(archive, restored, root,
                                  io.validate_bundle(
                                      io.discover_bundle(PARENT.parent / "datasets" / ds, root), root
                                  )[1])
            rows = io.validate_bundle(
                io.discover_bundle(PARENT.parent / "datasets" / ds, root), root
            )[1]
            count = io.checked_records(restored, root, rows)
            expected = root["scope"]["count"]
            assert count == dual_status["datasets"][ds]["records"]
            assert count == (expected if ds == "devign" else 1713)
            counts[ds] = {"records": count, "expected": expected, "remaining": expected - count}
        checkpoints[ds] = {"path": archive, "sha256": hashlib.sha256(archive.read_bytes()).hexdigest()}

    checkpoint_data = STAGE / "dataset"
    checkpoint_data.mkdir(parents=True)
    for ds, entry in checkpoints.items():
        shutil.copyfile(entry["path"], checkpoint_data / CHECKPOINT_NAMES[ds])
        assert hashlib.sha256((checkpoint_data / CHECKPOINT_NAMES[ds]).read_bytes()).hexdigest() == entry["sha256"]
    dataset = OWNER + "/grace-b3-new-dual-checkpoints-20261109"
    dump(checkpoint_data / "dataset-metadata.json", {
        "id": dataset,
        "title": "GRACE B3 verified dual validation checkpoints 20261109",
        "licenses": [{"name": "other"}],
        "isPrivate": True,
    })

    notebook = read(PARENT / "kernel/notebook.ipynb")
    notebook["cells"][0]["source"] = [
        "# B3 new algorithm: verified checkpoint continuation\n",
        "Continue the original Devign -> REVEAL validation run; fixed prompts, roots, model and runtime contract.\n",
    ]
    notebook["cells"][3]["source"] = (
        f"DEFINITIONS={read(PARENT / 'delivery.json')['datasets']!r}\n"
        f"EXPECTED_CHECKPOINT_SHA256={{{', '.join(repr(k)+': '+repr(v['sha256']) for k,v in checkpoints.items())}}}\n"
        f"EXPECTED_CHECKPOINT_MEMBERS={checkpoint_members!r}\n" + '''
KAGGLE_INPUT_ROOT=Path('/kaggle/input')
OUT_ROOT=Path('/kaggle/working/b3_new_dual_validation_resume_v2_20261109')
MAX_RUNTIME_HOURS=9
if OUT_ROOT.exists():raise ValueError('Resume output unexpectedly exists; refuse overwrite')
from b3_delivery_runtime import load_input_root, run_identity, read_members, verify_inventory
for ds, name in {'devign':'B3_devign_validation_checkpoint.zip','reveal':'B3_reveal_validation_checkpoint.zip'}.items():
    root=load_input_root(DEFINITIONS[ds]['path'],DEFINITIONS[ds]['sha256'])
    expected_identity=run_identity(root)
    expected_members=EXPECTED_CHECKPOINT_MEMBERS[ds]
    matches=[]
    for candidate in KAGGLE_INPUT_ROOT.rglob(name):
        if candidate.is_file() and hashlib.sha256(candidate.read_bytes()).hexdigest()==EXPECTED_CHECKPOINT_SHA256[ds]:
            files=read_members(candidate)
            verify_inventory(files,expected_members)
            matches.append(candidate)
    for marker in KAGGLE_INPUT_ROOT.rglob('checkpoint_manifest.json'):
        candidate=marker.parent
        manifest=json.loads(marker.read_text(encoding='utf-8'))
        if manifest.get('identity')!=expected_identity:
            continue
        files=read_members(candidate)
        verify_inventory(files,expected_members)
        matches.append(candidate)
    unique={str(p.resolve()):p for p in matches}
    if len(unique)!=1:raise ValueError('Need exactly one externally pinned checkpoint archive/member directory for '+ds)
    DEFINITIONS[ds]['checkpoint']=str(next(iter(unique.values())))
''').splitlines(keepends=True)
    notebook["cells"][8]["source"] = ''.join(notebook["cells"][8]["source"]).replace(
        "/kaggle/working/b3_new_dual_validation_20261109_checkpoint",
        "/kaggle/working/b3_new_dual_validation_resume_v2_20261109_checkpoint",
    ).splitlines(keepends=True)

    meta = read(PARENT / "kernel/kernel-metadata.json")
    meta.update(
        id=OWNER + "/grace-b3-new-algorithm-checkpoint-resume-v2",
        title="GRACE B3 checkpoint resume v2",
        dataset_sources=[
            OWNER + "/grace-b3-devign-v6-inputs-20261109",
            OWNER + "/grace-b3-reveal-v7-inputs-20261109",
            dataset,
        ],
        session_timeout_seconds=32400,
        machine_shape="NvidiaTeslaT4",
    )
    transport.finalize(STAGE, notebook, meta, {
        "execution_revision": delivery["execution_revision"],
        "resume_parent": delivery["ref"],
        "resume_parent_version": read(PARENT / "launch.json")["version"],
        "datasets": delivery["datasets"],
        "checkpoint_dataset": dataset,
        "checkpoints": {ds: {"sha256": item["sha256"], **counts[ds]} for ds, item in checkpoints.items()},
        "fixed_order": ["devign", "reveal"],
        "runtime_contract_sha256": delivery["runtime_contract_sha256"],
        "scope": "B3 new algorithm validation seed42 only; resume checkpointed records; no test or threshold fitting",
    })
    dump(STAGE / "checkpoint_acceptance.json", {
        "parent_kernel": delivery["ref"],
        "parent_status": dual_status,
        "checkpoints": {ds: {"sha256": item["sha256"], **counts[ds]} for ds, item in checkpoints.items()},
        "runtime_contract_sha256": delivery["runtime_contract_sha256"],
        "verified_checkpoint_restore": True,
    })
    print(json.dumps(read(STAGE / "checkpoint_acceptance.json"), ensure_ascii=False, indent=2))


def api_client():
    return parent.api_client()


def upload():
    stage = STAGE
    marker = stage / "dataset_upload.json"
    if marker.exists():
        raise ValueError("Dataset upload already recorded; inspect its receipt")
    api = api_client()
    meta = read(stage / "dataset/dataset-metadata.json")
    response = api.dataset_create_new(str(stage / "dataset"), public=False, quiet=True, convert_to_csv=False)
    result = {"dataset": meta["id"], "private_requested": True,
              "status": str(getattr(response, "status", "")), "error": str(getattr(response, "error", ""))}
    dump(marker, result)
    print(json.dumps(result))
    if result["error"]:
        raise ValueError("Private checkpoint dataset creation failed")


def remote(action):
    transport.BASE = BASE
    transport.OWNER = OWNER
    transport.api_client = api_client
    if action == "launch":
        assert read(PARENT / "status.json")["status"].endswith(("COMPLETE", "ERROR", "CANCEL_ACKNOWLEDGED"))
        for ds in ("devign", "reveal"):
            assert str(api_client().dataset_status(OWNER + f"/grace-b3-{ds}-{'v6' if ds == 'devign' else 'v7'}-inputs-20261109")).lower() == "ready"
        checkpoint_dataset = read(STAGE / "dataset/dataset-metadata.json")["id"]
        assert str(api_client().dataset_status(checkpoint_dataset)).lower() == "ready"
        assert hashlib.sha256((STAGE / "kernel/notebook.ipynb").read_bytes()).hexdigest() == read(STAGE / "delivery.json")["notebook_sha256"]
    transport.remote(KIND, action)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "upload", "dataset-status", "launch", "verify", "status", "output"])
    action = parser.parse_args().action
    if action == "prepare":
        prepare()
    elif action == "upload":
        upload()
    elif action == "dataset-status":
        api = api_client()
        dataset = read(STAGE / "dataset/dataset-metadata.json")["id"]
        result = {"dataset": dataset, "status": str(api.dataset_status(dataset))}
        dump(STAGE / "dataset_status.json", result)
        print(json.dumps(result))
    else:
        remote(action)


if __name__ == "__main__":
    main()
