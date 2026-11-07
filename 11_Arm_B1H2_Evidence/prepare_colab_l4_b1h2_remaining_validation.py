from __future__ import annotations

import hashlib
import json
import runpy
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARM = ROOT / "11_Arm_B1H2_Evidence"
PILOT = ARM / "colab_l4_pilot_20261106"
SOURCE_ZIP = ROOT.parent / "grace_15arms_prompts_and_clean_specs (1).zip"
OUTPUT_ZIP = PILOT / "downloaded_output" / "l4_pilot_output.zip"
OUT_DIR = ARM / "colab_l4_b1h2_remaining_validation_20261106"
BUNDLE_DIR = OUT_DIR / "bundles"
NOTEBOOK_DIR = ARM / "notebooks"
OLD_NOTEBOOK = NOTEBOOK_DIR / "colab_l4_b1h2_100_sample_pilot_20261106.ipynb"
ARCHIVE_MEMBERS = {
    "devign": "prompts/dry_run_validation_20261102/devign/validation/B1-H2/42/prompts.jsonl",
    "reveal": "prompts/dry_run_validation_20261102/reveal/validation/B1-H2/42/prompts.jsonl",
}
MODEL_SHA256 = "f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335"
DRIVE_BUNDLE_URL = "https://drive.google.com/file/d/1FuYcMkEuMBAFYexmg0c1HL5BxPB_L_Vg/view?usp=drivesdk"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(data: bytes) -> list[dict]:
    return [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]


def make_notebook(source_archive_sha: str, prompts_sha: str) -> dict:
    nb = json.loads(OLD_NOTEBOOK.read_text(encoding="utf-8"))
    replacements = {
        "# B1-H2 L4 pilot — 100 validation prompts": "# B1-H2 L4 — Remaining validation inference",
        "This is an **exploratory hardware and scoring pilot**, not a confirmatory result and not for threshold fitting. It samples 50 Devign and 50 ReVeal prompts from Hiếu's original B1-H2 validation packet (seed 42), preserving the prompts byte-for-byte.": "This notebook continues inference on every original B1-H2 validation prompt except the exact 100 already run in the L4 pilot. It does not modify the frozen prompt set. Results are validation-only; freeze the threshold only after the full validation set is complete and reviewed.",
        "colab_l4_b1h2_100_sample_pilot_20261106.ipynb": "colab_l4_b1h2_remaining_validation_20261106.ipynb",
        "GRACE_B1H2_COLAB_L4_PILOT_20261106": "GRACE_B1H2_COLAB_L4_REMAINING_20261106",
        "b1h2_l4_100_sample_bundle.zip": "b1h2_l4_remaining_validation_bundle.zip",
        "[b1h2_l4_100_sample_bundle.zip](https://drive.google.com/file/d/1LWGkH3tmNgWml8s_JTR7A-0ynYb0__L_/view?usp=drivesdk)": "[b1h2_l4_remaining_validation_bundle.zip](BUNDLE_URL_PLACEHOLDER)",
        "l4_pilot_output": "l4_remaining_validation_output",
        "b1h2_l4_pilot": "b1h2_l4_remaining_validation",
        "n_prompts':100": "n_prompts':len(rows)",
        "'n_prompts':100": "'n_prompts':len(rows)",
        "len(rows) != 100": "len(rows) != bundle_manifest['count']",
        "len({r['id'] for r in rows}) != 100": "len({r['id'] for r in rows}) != bundle_manifest['count']",
        "{'devign':50,'reveal':50}": "bundle_manifest['dataset_counts']",
        "'expected':100": "'expected':len(rows)",
        "== 100 else 'incomplete_or_timed_out'": "== len(rows) else 'incomplete_or_timed_out'",
        "[{ix}/100]": "[{ix}/{len(rows)}]",
        "'pilot_only':True": "'pilot_only':True,'validation_only':True",
        "('id','dataset','split','arm','seed','prompt_variant','prompt_sha256')": "('id','dataset','split','arm','seed','label','prompt_variant','prompt_sha256')",
        "'sample_seed':20261106,'pilot_only':True,'validation_only':True": "'validation_continuation':True,'pilot_only':False,'validation_only':True",
        "pilot_only=True)": "pilot_only=False, validation_only=True)",
        "runtime_cap_seconds':MAX_RUNTIME_SECONDS": "runtime_cap_seconds':MAX_RUNTIME_SECONDS,'expected_records':len(rows)",
        "PILOT_START = time.monotonic()\nMAX_RUNTIME_SECONDS = 10 * 60 * 60": "PILOT_START = time.monotonic()\nMAX_RUNTIME_SECONDS = 9 * 60 * 60",
        "# Score 100 prompts with the canonical unconstrained first-token logprob method.": "# Resume-safe inference over all remaining validation prompts; one record is fsynced after each completed prompt.",
    }
    for cell in nb["cells"]:
        src = "".join(cell.get("source", []))
        for old, new in replacements.items():
            src = src.replace(old, new)
        if "if len(rows) != bundle_manifest['count']" in src:
            src = src.replace(
                "if len(rows) != bundle_manifest['count'] or len({r['id'] for r in rows}) != bundle_manifest['count']:",
                "if len(rows) != bundle_manifest['count'] or len({r['id'] for r in rows}) != bundle_manifest['count']:",
            )
        if "bundle_manifest['dataset_counts']" in src and "if {d:" in src:
            src = src.replace(
                "if {d: sum(r['dataset'] == d for r in rows) for d in ('devign','reveal')} != bundle_manifest['dataset_counts']:",
                "if {d: sum(r['dataset'] == d for r in rows) for d in bundle_manifest['dataset_counts']} != bundle_manifest['dataset_counts']:",
            )
        if "MAX_RUNTIME_SECONDS = 9 * 60 * 60" in src:
            src = src.replace(
                "records_path = OUT / 'records.jsonl'\ndone = {}",
                "PILOT_START = time.monotonic()  # The 9-hour cap applies to inference, not setup/model download.\nrecords_path = OUT / 'records.jsonl'\ndone = {}",
            )
        # Ensure source and bundle identity are embedded in the executable notebook.
        if "SOURCE_ARCHIVE_SHA256" in src:
            src = src.replace("SOURCE_ARCHIVE_SHA256", source_archive_sha)
        if "BUNDLE_DRIVE_URL =" in src:
            src = src.replace("BUNDLE_DRIVE_URL = 'https://drive.google.com/file/d/1LWGkH3tmNgWml8s_JTR7A-0ynYb0__L_/view?usp=drivesdk'", "BUNDLE_DRIVE_URL = 'BUNDLE_URL_PLACEHOLDER'")
            src = src.replace("BUNDLE_URL_PLACEHOLDER", DRIVE_BUNDLE_URL)
        src = src.replace("BUNDLE_URL_PLACEHOLDER", DRIVE_BUNDLE_URL)
        if "if not BUNDLE_PATH.is_file():" in src:
            src = src.replace(
                "if not BUNDLE_PATH.is_file():\n    raise FileNotFoundError(f'Upload the bundle to Drive first: {BUNDLE_PATH}')",
                "if not BUNDLE_PATH.is_file():\n    raise FileNotFoundError(f'Download the bundle from {BUNDLE_DRIVE_URL} into {BUNDLE_PATH}')",
            )
        if "bundle_manifest = json.loads" in src:
            src = src.replace(
                "if bundle_manifest['source_archive_sha256'] != '" + source_archive_sha + "':\n    raise ValueError('Unexpected source archive hash')",
                "if bundle_manifest['source_archive_sha256'] != '" + source_archive_sha + "':\n    raise ValueError('Unexpected source archive hash')\nif bundle_manifest['prompts_sha256'] != '" + prompts_sha + "':\n    raise ValueError('Unexpected prompt hash')",
            )
        cell["source"] = src.splitlines(keepends=True)
        if cell.get("cell_type") == "code":
            cell["execution_count"] = None
            cell["outputs"] = []
    nb["metadata"]["colab"]["name"] = "colab_l4_b1h2_remaining_validation_20261106.ipynb"
    return nb


def main() -> None:
    for path in (SOURCE_ZIP, OUTPUT_ZIP, OLD_NOTEBOOK):
        if not path.is_file():
            raise FileNotFoundError(path)
    source_bytes = SOURCE_ZIP.read_bytes()
    source_archive_sha = sha256(source_bytes)

    with zipfile.ZipFile(OUTPUT_ZIP) as output:
        records_entry = next((e for e in output.namelist() if e.endswith("records.jsonl")), None)
        if records_entry is None:
            raise ValueError("Pilot output archive has no records.jsonl")
        pilot_rows = read_jsonl(output.read(records_entry))
    if len(pilot_rows) != 100 or len({r["id"] for r in pilot_rows}) != 100:
        raise ValueError(f"Expected 100 unique completed pilot rows, got {len(pilot_rows)}")
    pilot_by_id = {r["id"]: r["prompt_sha256"] for r in pilot_rows}
    if any(r.get("arm") != "B1-H2" or r.get("split") != "validation" for r in pilot_rows):
        raise ValueError("The completed pilot output is not exclusively B1-H2 validation")

    selected: list[dict] = []
    source_info: dict[str, dict] = {}
    excluded_source_hashes: dict[str, str] = {}
    with zipfile.ZipFile(SOURCE_ZIP) as source:
        for dataset, member in ARCHIVE_MEMBERS.items():
            raw = source.read(member)
            records = read_jsonl(raw)
            for row in records:
                if (row.get("dataset"), row.get("split"), row.get("arm"), row.get("seed")) != (dataset, "validation", "B1-H2", 42):
                    raise ValueError(f"Unexpected provenance in {member}: {row.get('id')}")
                if hashlib.sha256(row["prompt"].encode("utf-8")).hexdigest() != row.get("prompt_sha256"):
                    raise ValueError(f"Frozen prompt hash mismatch: {row.get('id')}")
                if row["id"] in pilot_by_id:
                    if pilot_by_id[row["id"]] != row["prompt_sha256"]:
                        raise ValueError(f"Pilot row prompt hash does not match frozen source: {row['id']}")
                    excluded_source_hashes[row["id"]] = row["prompt_sha256"]
                else:
                    selected.append(row)
            source_info[dataset] = {
                "zip_member": member,
                "source_jsonl_sha256": sha256(raw),
                "source_count": len(records),
                "already_run_excluded": sum(r["id"] in pilot_by_id for r in records),
                "remaining_count": sum(r["id"] not in pilot_by_id for r in records),
            }

    if len(excluded_source_hashes) != 100:
        raise ValueError(f"Only {len(excluded_source_hashes)} pilot rows were found in the frozen validation prompts")
    selected.sort(key=lambda r: (r["dataset"], r["id"]))
    counts = {dataset: sum(r["dataset"] == dataset for r in selected) for dataset in ARCHIVE_MEMBERS}
    if len(selected) != 4905 or counts != {"devign": 2682, "reveal": 2223}:
        raise ValueError(f"Unexpected remaining validation counts: total={len(selected)}, datasets={counts}")

    prompts_bytes = ("\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in selected) + "\n").encode("utf-8")
    prompts_sha = sha256(prompts_bytes)
    excluded_bytes = ("\n".join(f"{sid}\t{pilot_by_id[sid]}" for sid in sorted(pilot_by_id)) + "\n").encode("utf-8")
    manifest = {
        "schema": "grace_colab_b1h2_remaining_validation_v1",
        "purpose": "Resume B1-H2 validation inference on all original frozen prompts except the exact 100 already completed in the Colab L4 pilot; validation only, threshold frozen after full validation.",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_archive": SOURCE_ZIP.name,
        "source_archive_sha256": source_archive_sha,
        "source_prompt_members": source_info,
        "excluded_completed_pilot": {
            "output_archive": OUTPUT_ZIP.name,
            "output_archive_sha256": sha256(OUTPUT_ZIP.read_bytes()),
            "count": len(pilot_by_id),
            "id_prompt_sha256_tsv_sha256": sha256(excluded_bytes),
        },
        "dataset": "validation",
        "arm": "B1-H2",
        "prompt_variant": "Hiếu original ZIP, dry_run_validation_20261102, seed 42",
        "dataset_counts": counts,
        "count": len(selected),
        "model_repo": "ggml-org/Qwen3-Coder-30B-A3B-Instruct-GGUF",
        "model_file": "Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf",
        "quantization": "Q4_K_M",
        "model_sha256": MODEL_SHA256,
        "model_repo_revision": "local-sha256:" + MODEL_SHA256,
        "tokenizer": "Qwen/Qwen3-Coder-30B-A3B-Instruct",
        "tokenizer_revision": "b2cff646eb4bb1d68355c01b18ae02e7cf42d120",
        "backend": "llama-cpp-python 0.3.16",
        "context_tokens": 8192,
        "n_batch": 256,
        "seed": 42,
        "scoring": "unconstrained_first_token_logits_v1",
        "prompts_sha256": prompts_sha,
    }
    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)
    NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    bundle_path = BUNDLE_DIR / "b1h2_l4_remaining_validation_bundle.zip"
    with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        z.writestr("bundle_manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
        z.writestr("prompts.jsonl", prompts_bytes)
        z.writestr("excluded_pilot_ids_prompt_hashes.tsv", excluded_bytes)
    bundle_sha = sha256(bundle_path.read_bytes())

    notebook = make_notebook(source_archive_sha, prompts_sha)
    notebook_path = NOTEBOOK_DIR / "colab_l4_b1h2_remaining_validation_20261106.ipynb"
    notebook_path.write_text(json.dumps(notebook, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    runpy.run_path(str(ARM / "patch_remaining_validation_notebook.py"))
    (OUT_DIR / "bundle_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "source_archive_sha256": source_archive_sha,
        "pilot_output_sha256": sha256(OUTPUT_ZIP.read_bytes()),
        "bundle": str(bundle_path),
        "bundle_sha256": bundle_sha,
        "prompts_sha256": prompts_sha,
        "total_remaining": len(selected),
        "counts": counts,
        "excluded_pilot_rows": len(excluded_source_hashes),
        "notebook": str(notebook_path),
    }, indent=2))


if __name__ == "__main__":
    main()
