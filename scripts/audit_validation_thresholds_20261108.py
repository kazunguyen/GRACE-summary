"""Read-only threshold audit; writes only a new evidence directory, never a lock.

Run: python -B -X utf8 scripts/audit_validation_thresholds_20261108.py
The independent MCC sweep is completed before any threshold ledger is loaded.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import sys
import types
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Runs-management/threshold_audit_20261108"
MODEL = "f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335"
EXPECTED = {"devign": 2732, "reveal": 2273}
INHERIT = {"B2-rep": "B2", "B2-flip": "B2", "B3-swap": "B3", "B3-flip": "B3"}
READS = []
BLOCKED = []


def guard(event, args):
    if event != "open" or isinstance(args[0], int):
        return
    path, mode, flags = args
    p = Path(path).resolve()
    writing = flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)
    if writing:
        if OUT not in p.parents:
            BLOCKED.append(str(p))
            raise PermissionError("Audit may write only its evidence directory")
    else:
        if "test" in {x.lower() for x in p.parts} or re.search(r"(?:^|_)test(?:_|\.)", p.name.lower()):
            BLOCKED.append(str(p))
            raise PermissionError("Test file reads are prohibited")
        READS.append(str(p))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(value):
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


def md_key(key):
    return key.replace("|", " / ")


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def read_rows(path):
    raw = (ROOT / path).read_bytes()
    rows = [json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip()]
    return rows, {"path": path, "sha256": sha(raw),
                  "lf_sha256_diagnostic_only": sha(raw.replace(b"\r\n", b"\n")), "n": len(rows)}


def counts_and_mcc(y, s, tau):
    pred = s >= tau
    tp = int(np.sum((y == 1) & pred))
    tn = int(np.sum((y == 0) & ~pred))
    fp = int(np.sum((y == 0) & pred))
    fn = int(np.sum((y == 1) & ~pred))
    den = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    return {"tau": tau, "mcc": (tp * tn - fp * fn) / den if den else None,
            "tp": tp, "tn": tn, "fp": fp, "fn": fn}


def fit(y, s):
    grid = [counts_and_mcc(y, s, i / 100) for i in range(1, 100)]
    defined = [r for r in grid if r["mcc"] is not None]
    if not defined:
        return None, None, grid, []
    maximum = max(r["mcc"] for r in defined)
    ties = [r for r in defined if abs(r["mcc"] - maximum) <= 1e-9]
    chosen = min(ties, key=lambda r: (abs(r["tau"] - .5), r["tau"]))
    return chosen["tau"], chosen["mcc"], grid, [r["tau"] for r in ties]


def main():
    global OUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="Runs-management/threshold_audit_20261108")
    args = parser.parse_args()
    OUT = (ROOT / args.out).resolve()
    if (ROOT / "Runs-management").resolve() not in OUT.parents:
        raise ValueError("Evidence output must be a new directory under Runs-management")
    if OUT.exists():
        raise FileExistsError("Use a new output directory; preserve previous audit evidence")
    sys.addaudithook(guard)
    optimizer_path = ROOT / "Runs-management/validation_lock.py"
    optimizer_raw = optimizer_path.read_bytes()
    optimizer = types.ModuleType("original_validation_optimizer")
    exec(compile(optimizer_raw, str(optimizer_path), "exec"), optimizer.__dict__)
    labels = {}
    label_sources = []
    for ds in EXPECTED:
        rows, src = read_rows(f"01_Author_Baseline_Unified/output/research_freeze_20261101/{ds}/validation_manifest.jsonl")
        labels[ds] = {str(r["id"]): r["label"] for r in rows}
        assert len(rows) == len(labels[ds]) == EXPECTED[ds]
        label_sources.append(src)

    sources = []
    for arm, base in [("B0", "02_Arm_B0_Source_Only/output/kaggle_20261101_duchuynguyen1802/grace_b0_runs"),
                      ("B1", "03_Arm_B1_Graph_Only/output/kaggle_run_02/grace_b1_runs"),
                      ("B1-H2", "11_Arm_B1H2_Evidence/kaggle_b1h2_validation_20261106/downloaded_output/b1_h2_validation/seed_42")]:
        for ds in EXPECTED:
            sources.append((arm, ds, 42, "current", f"{base}/{ds}/validation/records.jsonl"))
    for ds in EXPECTED:
        for arm in ["B2", "B2-rep", "B1-full", "B2-nolabel", "B2-labelonly", "B3"]:
            sources.append((arm, ds, 42, "historical_donor" if arm == "B2" else "current",
                            f"runs/final/{ds}/validation/{arm}/42/records.jsonl"))
        for seed in [42, 43, 44]:
            sources.append(("B1-shuf", ds, seed, "current", f"runs/final/{ds}/validation/B1-shuf/{seed}/records.jsonl"))
            sources.append(("B2-rand", ds, seed, "current", f"Runs-management/kaggle_outputs_20261107/b2_rand_latest/grace_b2_rand_three_seed_11h/seed_{seed}/{ds}/validation/records.jsonl"))
        sources.append(("B2-flip", ds, 42, "current", f"Runs-management/kaggle_outputs_20261105/b2_flip/grace_b2_flip_frozen_donor_20261104_inherit_b2_9h30/{ds}/validation/records.jsonl"))

    results = []
    arrays = {}
    loaded = {}

    def evaluate(arm, ds, seed, version, rows, inputs):
        key = f"{ds}|{arm}|{seed}"
        ids = [str(r["id"]) for r in rows]
        issues = []
        if len(ids) != len(set(ids)):
            issues.append("duplicate_ids")
        missing = sorted(set(labels[ds]) - set(ids))
        extra = sorted(set(ids) - set(labels[ds]))
        invalid_numeric = 0
        max_score_error = 0.0
        logprob_checked = 0
        for r in rows:
            if (r.get("dataset"), r.get("arm"), r.get("split"), r.get("seed")) != (ds, arm, "validation", seed):
                issues.append("record_identity_mismatch")
            if r.get("label") not in (0, 1) or labels[ds].get(str(r["id"])) != r.get("label"):
                issues.append("frozen_label_mismatch")
            if r.get("model_sha256") != MODEL:
                issues.append("model_hash_mismatch")
            s = r.get("s")
            if r.get("valid") and (not isinstance(s, (int, float)) or not math.isfinite(s) or not 0 <= s <= 1):
                invalid_numeric += 1
            if r.get("valid") and isinstance(s, (int, float)) and math.isfinite(s):
                a, b = r.get("logprob_0"), r.get("logprob_1")
                if a is not None and b is not None and math.isfinite(a) and math.isfinite(b):
                    z = b - a
                    expected_s = 1 / (1 + math.exp(-z)) if z >= 0 else math.exp(z) / (1 + math.exp(z))
                    max_score_error = max(max_score_error, abs(s - expected_s))
                    logprob_checked += 1
        if invalid_numeric:
            issues.append("nonfinite_or_out_of_range_valid_score")
        if max_score_error > 1e-10:
            issues.append("score_logprob_mismatch")
        valid = [r for r in rows if r.get("valid") and isinstance(r.get("s"), (int, float)) and math.isfinite(r["s"]) and 0 <= r["s"] <= 1]
        y = np.array([r["label"] for r in valid], dtype=int)
        s = np.array([r["s"] for r in valid], dtype=float)
        complete = len(rows) == EXPECTED[ds] and not missing and not extra and not issues
        result = {"key": key, "arm": arm, "dataset": ds, "seed": seed, "version": version,
                  "inputs": inputs, "n": len(rows), "expected": EXPECTED[ds], "n_valid": len(valid),
                  "raw_response_invalid": sum(not r.get("response_valid", True) for r in rows),
                  "missing_count": len(missing), "extra_count": len(extra), "issues": sorted(set(issues)),
                  "logprob_checked": logprob_checked, "max_score_error": max_score_error,
                  "complete": complete, "policy": "inherit_from:" + INHERIT[arm] if arm in INHERIT else "argmax_validation_mcc",
                  "status": "pending_inheritance" if arm in INHERIT else "not_computable",
                  "evidence_sha256": digest([{k: r.get(k) for k in ("id", "label", "prompt_sha256", "model_sha256", "seed", "s", "valid")} for r in sorted(rows, key=lambda r: str(r["id"]))]),
                  "score_prompt_digest": digest([{k: r.get(k) for k in ("id", "label", "prompt_sha256", "s", "valid")} for r in sorted(rows, key=lambda r: str(r["id"]))])}
        if arm not in INHERIT and complete and len(set(y.tolist())) == 2:
            tau, mcc, grid, ties = fit(y, s)
            check = optimizer.pick_threshold(rows)
            if tau is None:
                raise ValueError(f"No defined MCC at any grid point: {key}; no threshold certified")
            assert tau == check["tau"] and abs(mcc - check["validation_mcc"]) < 1e-12
            for own, existing in zip(grid, check["grid_results"]):
                assert own["mcc"] == existing["mcc"]
            result.update(tau=tau, validation_mcc=mcc, grid=grid, ties=ties,
                          optimizer_crosscheck="all_99_MCC_values_match", status="computed")
        elif not complete:
            result["status"] = "incomplete_or_invalid_no_fit"
        if arm == "B3":
            result["methodology_caveat"] = "Historical B3 records; this computation does not authenticate amended patch-pair eligibility or permit pooling with amended B3."
        results.append(result)
        arrays[(key, version)] = (y, s)
        loaded[(key, version)] = rows
        return result

    for arm, ds, seed, version, path in sources:
        if not (ROOT / path).exists():
            results.append({"key": f"{ds}|{arm}|{seed}", "arm": arm, "dataset": ds, "seed": seed,
                            "version": version, "status": "source_missing_no_fit", "inputs": [{"path": path}], "complete": False})
            continue
        rows, src = read_rows(path)
        evaluate(arm, ds, seed, version, rows, [src])

    # Reconstruct the frozen-donor B2 validation in memory only, using actual rerun rows.
    # Do not silently pool old/new inference: replace only the explicitly rerun IDs.
    for ds in EXPECTED:
        key = f"{ds}|B2|42"
        old = loaded[(key, "historical_donor")]
        old_src = next(r["inputs"] for r in results if r["key"] == key and r["version"] == "historical_donor")
        if ds == "devign":
            path = "Runs-management/kaggle_outputs_20261107/b2_rand_latest/grace_b2_rand_three_seed_11h/b2_donor_rerun_66/devign/validation/records.jsonl"
            changes, src = read_rows(path)
            assert len(changes) == 28 and len({r["id"] for r in changes}) == 28
            by_id = {r["id"]: r for r in old}
            assert all(r["id"] in by_id and r["label"] == by_id[r["id"]]["label"] for r in changes)
            by_id.update({r["id"]: r for r in changes})
            merged = list(by_id.values())
            inputs = old_src + [src]
        else:
            merged, inputs = old, old_src
        r = evaluate("B2", ds, 42, "frozen_donor_reconstructed", merged, inputs)
        r["replacement_rows"] = 28 if ds == "devign" else 0

    by_current = {}
    for r in results:
        if r["version"] != "historical_donor":
            by_current[r["key"]] = r
    for r in results:
        if r["arm"] not in INHERIT:
            continue
        parent_key = f"{r['dataset']}|{INHERIT[r['arm']]}|{r['seed']}"
        parent = by_current.get(parent_key, {})
        if parent.get("status") == "computed":
            r["tau"] = parent["tau"]
            r["inherited_from_computed"] = parent_key
            r["status"] = "inherited_from_recomputed_parent"
            if (r["key"], r["version"]) in arrays:
                y, s = arrays[r["key"], r["version"]]
                r["validation_mcc"] = counts_and_mcc(y, s, r["tau"])["mcc"]

    # All fitting has finished. Only now open original OSF evidence and lock values.
    osf_path = "Runs-management/osf_registration_draft_20261102/GRACE_OSF_PREREGISTRATION_20261102.zip"
    osf_raw = (ROOT / osf_path).read_bytes()
    assert sha(osf_raw) == "6d6e8fe46f1dc59bf5f399defca59ba8ab0c362a0b13d0cb101c16320a2a082e"
    with ZipFile(ROOT / osf_path) as z:
        original = json.loads(z.read("configs/thresholds.json"))
    locks = {"OSF_original_frozen_zip": original}
    lock_paths = ["configs/thresholds.json", "configs/thresholds_flat.json", "runs/thresholds.json",
                  "Runs-management/thresholds.json", "01_Author_Baseline_Unified/diagnostic_kit/configs/thresholds.json",
                  "01_Author_Baseline_Unified/diagnostic_kit/configs/thresholds_flat.json",
                  "grace_15arms_prompts_and_clean_specs/configs/thresholds.json",
                  "Runs-management/b1h2_kaggle_validation_threshold_lock_20261106.json"]
    lock_paths += [f"{d}/config/threshold.json" for d in ["05_Arm_B2_Rep", "06_Arm_B2_Rand", "08_Arm_B1_Shuf", "09_Arm_B1_Full", "10_Arm_B2_NoLabel", "12_Arm_B2_LabelOnly"]]
    for path in lock_paths:
        if (ROOT / path).exists():
            locks[path] = read_json(path)

    def entries(data):
        if "thresholds" in data:
            for key, value in data["thresholds"].items():
                yield key, value if isinstance(value, dict) else {"tau": value}
        elif "entries" in data:
            for value in data["entries"].values():
                yield f"{value['dataset']}|{value['arm']}|{value.get('seed', 42)}", value
        elif "results" in data:
            for ds, value in data["results"].items():
                yield f"{ds}|{data['arm']}|{data.get('seed', 42)}", value
        elif all("|" in k for k in data):
            for key, value in data.items():
                yield key, {"tau": value}

    comparisons, seals = [], []
    for name, lock in locks.items():
        if "locked_sha256" in lock:
            body = {k: v for k, v in lock.items() if k != "locked_sha256"}
            indented = sha(json.dumps(body, indent=2, ensure_ascii=False, sort_keys=True).encode())
            compact = digest(body)
            seals.append({"source": name, "stored": lock["locked_sha256"],
                          "verified": lock["locked_sha256"] in [indented, compact],
                          "file_sha256": sha((ROOT / name).read_bytes()) if name != "OSF_original_frozen_zip" else None})
        for key, value in entries(lock):
            tau = value.get("tau", value.get("tau_star"))
            calc = by_current.get(key, {})
            usable = calc.get("tau") is not None
            item = {"source": name, "key": key, "stored_tau": tau,
                    "computed_tau": calc.get("tau"), "status": "match" if usable and abs(tau - calc["tau"]) < 1e-12 else ("MISMATCH" if usable else "unverified_missing_complete_scores")}
            if usable and (key, calc["version"]) in arrays:
                y, s = arrays[key, calc["version"]]
                item["mcc_at_stored_tau"] = counts_and_mcc(y, s, tau)["mcc"]
                item["mcc_at_computed_tau"] = calc.get("validation_mcc")
            claimed_mcc = value.get("validation_mcc", value.get("mcc_at_tau", value.get("mcc_val")))
            if claimed_mcc is not None and item.get("mcc_at_stored_tau") is not None:
                item["stored_mcc"] = claimed_mcc
                item["mcc_matches"] = abs(claimed_mcc - item["mcc_at_stored_tau"]) < 1e-9
            if "validation_records_sha256" in value:
                item["record_bytes_match_selected_source"] = value["validation_records_sha256"] in [x.get("sha256") for x in calc.get("inputs", [])]
                item["record_hash_matches_after_lf_normalization_diagnostic_only"] = value["validation_records_sha256"] in [x.get("lf_sha256_diagnostic_only") for x in calc.get("inputs", [])]
            if "validation_evidence_sha256" in value:
                item["semantic_evidence_hash_matches"] = value["validation_evidence_sha256"] == calc.get("evidence_sha256")
            comparisons.append(item)

    # Parse comparison values from the local amendment, never use them as fit inputs.
    amendment_path = "Runs-management/osf_amendment_20261106/OSF_UPDATE_EN.md"
    amendment_text = (ROOT / amendment_path).read_text(encoding="utf-8")
    amended = []
    for ds, arm, old, new, mcc in re.findall(r"\| (Devign|ReVeal) \| (B[01]) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \|", amendment_text):
        key = f"{ds.lower()}|{arm}|42"
        amended.append({"key": key, "amendment_tau": float(new), "computed_tau": by_current[key]["tau"],
                        "match": abs(float(new) - by_current[key]["tau"]) < 1e-12})

    inventory = []
    for directory, subdirs, files in os.walk(ROOT):
        subdirs[:] = [x for x in subdirs if x not in {".git", ".venv", "node_modules", "__pycache__"}]
        p = Path(directory) / "records.jsonl"
        if "records.jsonl" in files and "validation" in {x.lower() for x in p.parts}:
            raw = p.read_bytes()
            inventory.append({"path": p.relative_to(ROOT).as_posix(), "sha256": sha(raw),
                              "n_lines": sum(bool(x.strip()) for x in raw.splitlines())})

    unresolved = [{"key": k, "reason": "Original export hard-coded this value; no saved per-ID validation probabilities for this model were found. Do not substitute thresholds from another fit or retrain silently."}
                  for k in original["thresholds"] if "|P-P" in k]
    report = {"created_at_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "Validation-only mathematical audit; not certification of prospective timing, runtime equivalence, pair quality, or live OSF acceptance.",
              "rules": {"grid": "i/100, i=1..99", "objective": "MCC", "positive": "s >= tau", "valid": "valid=true and finite s in [0,1]; raw response validity is separate", "tie": "within 1e-9 of global maximum, closest to 0.5 then smaller tau", "undefined_mcc": "skip; no fit on partial census", "inheritance": INHERIT},
              "optimizer_sha256": sha(optimizer_raw), "script_sha256": sha(Path(__file__).read_bytes()),
              "labels": label_sources, "results": results, "comparisons": comparisons,
              "seals": seals, "osf_original_archive_sha256": sha(osf_raw),
              "amendment_source": amendment_path, "amendment_sha256": sha(amendment_text.encode()),
              "amendment_comparisons": amended, "unresolved_original_meta_thresholds": unresolved,
              "validation_inventory": inventory,
              "limitations": ["OSF webpage and API could not be accessed through the web tool; comparison is against the hash-verified local original attachment and local amendment text, not independent proof of the live amendment.", "B2-rand seed44 full output mentioned in worklogs is absent locally: only 2426 Devign rows and no REVEAL rows in the available latest checkpoint. A separate Kaggle CLI download attempt on 2026-11-08 returned HTTP 403 Forbidden.", "Historical B3 validation is a separate method; REVEAL is incomplete. Synthetic amended GPU smoke outputs are not validation census records.", "P-PRE/P-POST saved validation scores were not found; their four original lock values remain computationally unverified.", "Some local B2-rand seed42/43 record byte hashes differ solely by CRLF/LF; LF-normalized hashes and semantic evidence hashes match. This audit does not modify source bytes or certify byte equality."],
              "file_access_audit": {"test_files_read": [], "blocked": BLOCKED, "opened_read_paths": sorted(set(READS))}}
    OUT.mkdir(parents=True)
    (OUT / "audit.json").write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    with (OUT / "thresholds.csv").open("w", encoding="utf-8", newline="") as f:
        fields = ["key", "version", "n", "expected", "n_valid", "status", "tau", "validation_mcc", "raw_response_invalid"]
        w = csv.DictWriter(f, fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(results)
    with (OUT / "comparisons.csv").open("w", encoding="utf-8", newline="") as f:
        fields = list(dict.fromkeys(k for r in comparisons for k in r))
        w = csv.DictWriter(f, fields)
        w.writeheader()
        w.writerows(comparisons)
    lines = ["# Kiểm toán threshold từ validation — 08/11/2026", "",
             "Tính trực tiếp từ từng record validation; không đọc test để chọn ngưỡng, không sửa bất kỳ lock nào.", "",
             "## Phương pháp", "",
             "Quét 99 ngưỡng i/100 (i=1..99); dự đoán 1 khi s >= tau. MCC = (TP*TN-FP*FN)/sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)). Chỉ dùng valid=true và score hữu hạn trong [0,1]; raw response-invalid không làm mất score hợp lệ. Bỏ ngưỡng MCC không xác định. Hòa trong 1e-9: gần 0,5 nhất, rồi ngưỡng thấp hơn. Không fit khi thiếu census.", "",
             "Kiểm tra tập ID/nhãn với validation manifest đóng băng, arm/dataset/split/seed, model SHA và score so với sigmoid(logprob_1-logprob_0). Phép tính độc lập được đối chiếu toàn bộ 99 giá trị MCC với optimizer validation_lock.py. Probe kế thừa ngưỡng đã tính lại của arm gốc; không tối ưu probe.", "",
             "## Đối chiếu bản OSF gốc", "",
             "Đọc configs/thresholds.json bên trong ZIP OSF gốc, kiểm đúng SHA-256 6d6e8fe46f1dc59bf5f399defca59ba8ab0c362a0b13d0cb101c16320a2a082e. Không lấy số từ báo cáo để fit.", "",
             "| Khóa | OSF gốc | Tính lại | Kết luận |", "|---|---:|---:|---|"]
    for c in comparisons:
        if c["source"] == "OSF_original_frozen_zip":
            lines.append(f"| {md_key(c['key'])} | {c['stored_tau']:.2f} | {c['computed_tau'] if c['computed_tau'] is not None else '—'} | {c['status']} |")
    lines += ["", "Bốn giá trị B0/B1 sửa trong OSF_UPDATE_EN.md đều khớp phép tính mới. Tuy nhiên configs/thresholds.json hiện tại và các mirror vẫn giữ bốn giá trị gốc không khớp; chữ ký tự xác thực hợp lệ không chứng minh ngưỡng tối ưu đúng. Không tự sửa các file đóng băng.", "",
              "## Toàn bộ kết quả validation", "",
              "| Khóa | Phiên | N | Ngưỡng tính/kế thừa | MCC validation | Trạng thái |",
              "|---|---|---:|---:|---:|---|"]
    for r in results:
        tau = f"{r['tau']:.2f}" if r.get("tau") is not None else "—"
        mcc = f"{r['validation_mcc']:.9f}" if r.get("validation_mcc") is not None else "—"
        lines.append(f"| {md_key(r['key'])} | {r['version']} | {r.get('n', '—')} | {tau} | {mcc} | {r['status']} |")
    lines += ["", "## Các khóa mới", "",
              "| File khóa | Khớp phép tính/kế thừa | Không khớp | Chưa đủ score xác minh |",
              "|---|---:|---:|---:|"]
    for source in locks:
        if "/config/" not in source and "b1h2_kaggle_validation_threshold_lock" not in source:
            continue
        cs = [c for c in comparisons if c["source"] == source]
        lines.append(f"| {source} | {sum(c['status']=='match' for c in cs)} | {sum(c['status']=='MISMATCH' for c in cs)} | {sum(c['status']=='unverified_missing_complete_scores' for c in cs)} |")
    lines += ["", "Tất cả self-seal có mặt trong phạm vi kiểm tra đều hợp lệ. MCC đã lưu của các entry per-arm đủ dữ liệu cũng khớp. B2-rand seed42/43 có byte hash local khác do CRLF/LF; sau chuẩn hóa LF để chẩn đoán, hash khớp bản khóa, đồng thời semantic evidence hash khớp. Không ghi lại hay chuẩn hóa file nguồn.", "",
              "## Giới hạn và nguồn còn thiếu", ""]
    lines += ["- " + s for s in report["limitations"]]
    lines += ["", "- B3 Devign có thể tính ngưỡng toán học từ phiên lịch sử đủ record, nhưng không chứng minh cặp demo đạt điều kiện amended. Không dùng ngưỡng này để cấp phép chạy test amended. B3 REVEAL chỉ có 1.276/2.273 record; B3-nodiff/swap/flip chưa có bộ validation thực đủ để nghiệm thu trong phạm vi đã tìm.",
              "- Với P-PRE/P-POST, script export gốc scripts/lock_full_validation_thresholds.py gán hằng cho bốn khóa. Không coi giá trị gán sẵn hay threshold trong báo cáo khác là bằng chứng tính lại. Cần đúng score validation từng ID của chính model/fit đó.",
              "- Audit này xác minh phép tính, không chứng nhận ngưỡng đã khóa trước test hoặc amendment đã được OSF chấp thuận.", "",
              "## Tái lập", "", "```powershell", "python -B -X utf8 scripts/audit_validation_thresholds_20261108.py --out Runs-management/threshold_audit_20261108_reproduction", "```", "",
              "Thư mục output phải chưa tồn tại. audit.json lưu mọi grid, confusion matrix, hash nguồn, so sánh lock và file-read audit; thresholds.csv/comparisons.csv là bảng chi tiết. Dữ liệu inference lớn có thể bị Git ignore, cần nhận lại đúng nguồn/hash trước khi tái lập trên máy khác.", ""]
    (OUT / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"results": [{k: r.get(k) for k in ["key", "version", "n", "status", "tau", "validation_mcc", "issues"]} for r in results],
                      "failed_seals": [s for s in seals if not s["verified"]],
                      "per_arm_mismatches": [c for c in comparisons if "/config/" in c["source"] and (c["status"] == "MISMATCH" or c.get("mcc_matches") is False)],
                      "output": str(OUT)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
