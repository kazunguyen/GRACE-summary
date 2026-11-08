"""Additional full-field checkpoint and score checks; no inference or remote I/O."""
import hashlib
import json
import math
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
HARVEST = ROOT / "Runs-management/kernel_outputs_harvest"


def rows(raw):
    return [json.loads(line) for line in raw.splitlines() if line.strip()]


def main():
    result = {"datasets": [], "archives": [], "repeat_vs_B2": []}
    targets = [("B2-labelonly", "tomandjerry223_grace-b2-labelonly-test", "b2_labelonly_test"),
               ("B2-nolabel", "tomandjerry223_grace-b2-nolabel-test", "b2_nolabel_test"),
               ("B2-rep", "huuhieu3333_grace-b2-rep-test", "b2_rep_test"),
               ("B1-full", "huuhieu3333_grace-b1-full-test", "b1_full_test"),
               ("B3", "lznt123_grace-b3-validation", "b3_validation")]
    for arm, slug, folder in targets:
        directory = HARVEST / slug
        for path in (directory / folder).rglob("records.jsonl"):
            records = rows(path.read_bytes())
            for r in records:
                assert r["token_ids"] == {"0": 15, "1": 16}
                assert r["pred_argmax"] == int(r["s"] >= .5)
                for p, lp in [("p0", "logprob_0"), ("p1", "logprob_1")]:
                    assert abs(r[p] - math.exp(r[lp])) < 1e-12
                if arm != "B3":
                    assert r["inference_seed"] == 4294967295
                assert math.isfinite(r["elapsed_s"]) and r["elapsed_s"] > 0
            result["datasets"].append({"path": str(path.relative_to(ROOT)), "n": len(records),
                                        "binary_token_ids_pred_argmax_probabilities_elapsed_and_recorded_inference_seed": "pass"})
        for archive in directory.glob("*.zip"):
            if not any(s in archive.name for s in ["checkpoint", "final_output"]):
                continue
            with ZipFile(archive) as z:
                for name in z.namelist():
                    if not name.endswith("records.jsonl"):
                        continue
                    loose = directory / folder / name
                    if not loose.exists():
                        raise AssertionError("No corresponding loose record file: " + str(loose))
                    archived = rows(z.read(name))
                    local = {r["id"]: r for r in rows(loose.read_bytes())}
                    assert len(archived) == len({r["id"] for r in archived})
                    assert all(r == local.get(r["id"]) for r in archived)
                    result["archives"].append({"archive": str(archive.relative_to(ROOT)), "member": name,
                                               "n": len(archived), "every_record_field_matches": True,
                                               "loose_rows_missing_in_archive": len(local) - len(archived)})
    for ds in ["devign", "reveal"]:
        path = ROOT / f"01_Author_Baseline_Unified/output/local_full/inference_qwen_q4_b2_20261101/grace_b2_four_split_8h/{ds}/test/records.jsonl"
        baseline = {r["id"]: r for r in rows(path.read_bytes())}
        if ds == "devign":
            changes = ROOT / "Runs-management/kaggle_outputs_20261107/b2_rand_latest/grace_b2_rand_three_seed_11h/b2_donor_rerun_66/devign/test/records.jsonl"
            replacement = rows(changes.read_bytes())
            assert len(replacement) == 38
            baseline.update({r["id"]: r for r in replacement})
        repeated = rows((HARVEST / f"huuhieu3333_grace-b2-rep-test/b2_rep_test/seed_42/{ds}/test/records.jsonl").read_bytes())
        assert set(baseline) == {r["id"] for r in repeated}
        assert all(r["prompt_sha256"] == baseline[r["id"]]["prompt_sha256"] for r in repeated)
        result["repeat_vs_B2"].append({"dataset": ds, "n": len(repeated), "all_prompt_hashes_match_frozen_donor_B2": True,
            "same_numeric_s": sum(r["s"] == baseline[r["id"]]["s"] for r in repeated),
            "different_timestamp": sum(r["timestamp"] != baseline[r["id"]]["timestamp"] for r in repeated),
            "all_positive_elapsed": all(r["elapsed_s"] > 0 for r in repeated),
            "interpretation": "Identical deterministic scores alone do not prove cache reuse. Actual exported runner calls reset/eval; independent timestamps/elapsed and process logs support fresh execution. No absolute external cache guarantee is inferred from repeat tags alone."})
    (HERE / "additional_integrity.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("PASS: additional score checks and every archived record field; repeat prompts match reconstructed frozen-donor B2")


if __name__ == "__main__":
    main()
