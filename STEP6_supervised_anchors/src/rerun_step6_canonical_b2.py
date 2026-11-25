"""Rerun the Step 6 analyses with canonical B2 scores.

Why: lock step6_lock_64fb2c99d904_44f00d19 joined B2 records from run3, i.e.
before the 66-row donor change (Devign validation 28 rows, Devign test 38 rows).
Tables A/B use the canonical B2 records. ReVeal is unaffected.

How: the joined CSVs of that lock already hold the locked y, p_gate, group and
SUP-LR scores; X_pre comes from the locked H3-B export (hashes checked against
the lock manifest). Only s_llm/valid are replaced. The analysis functions are
imported unchanged from step6_complementarity.py.

Modes:
  control    keep the run3 B2 scores; output must equal the 44f00d19 results
  canonical  B2 scores from inputs/b2_canonical_frozen_donor_20261102

Also reports the H5.3 repair criterion at the 95th percentile of the 20
random experts (registered wording), next to the 97.5th used by the lock.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import importlib.util
import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
STEP6 = HERE.parent
SUMMARY = STEP6.parent
LOCK_RUN = STEP6 / "runs" / "complementarity_step6" / "step6_lock_64fb2c99d904_44f00d19"
H3B_ROOT = STEP6 / "runs" / "h3b_locked" / "step6_lock_64fb2c99d904"
B2_CANONICAL = STEP6 / "inputs" / "b2_canonical_frozen_donor_20261102"
OUT_ROOT = STEP6 / "runs" / "complementarity_step6"


def load_module():
    spec = importlib.util.spec_from_file_location("step6c", HERE / "step6_complementarity.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_joined(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return [{"id": r["id"], "y": int(r["y"]), "p_gate": float(r["p_gate"]),
                 "s_llm": float(r["s_llm"]), "valid": r["valid"] == "1",
                 "group": r["group"], "s_sup_lr": float(r["s_sup_lr"]),
                 "code_sha256": r["code_sha256"]} for r in csv.DictReader(f)]


def load_x(mod, manifest: dict, dataset: str, split: str, ids: list[str]) -> np.ndarray:
    info = manifest["inputs"][f"{dataset}/{split}"]["h3b"]
    path = H3B_ROOT / info["xpre_path"]
    if mod.sha256_file(path) != info["xpre_sha256"]:
        raise SystemExit(f"FAIL xpre hash {dataset}/{split}")
    with np.load(path, allow_pickle=False) as a:
        X = np.asarray(a["X"], dtype=np.float64)
        xids = a["ids"].astype(str).tolist()
    index = {rid: i for i, rid in enumerate(xids)}
    if set(index) != set(ids):
        raise SystemExit(f"FAIL xpre ID coverage {dataset}/{split}")
    return X[[index[rid] for rid in ids]]


def apply_canonical_b2(mod, rows: list[dict], dataset: str, split: str) -> dict:
    recs = mod.read_jsonl(B2_CANONICAL / dataset / split / "records.jsonl")
    by_id = {r["id"]: r for r in recs}
    if set(by_id) != {r["id"] for r in rows}:
        raise SystemExit(f"FAIL canonical B2 ID coverage {dataset}/{split}")
    changed = 0
    for r in rows:
        b = by_id[r["id"]]
        if int(b["label"]) != r["y"]:
            raise SystemExit(f"FAIL label mismatch {r['id']}")
        valid = mod._bool(b.get("valid", False))
        s = mod._safe_score(b.get("s"), valid, r["id"])
        if s != r["s_llm"] or valid != r["valid"]:
            changed += 1
        r["s_llm"], r["valid"] = s, valid
    return {"records_sha256": mod.sha256_file(B2_CANONICAL / dataset / split / "records.jsonl"),
            "rows_with_changed_s_or_valid": changed}


def repair_p95(mod, rows_t: list[dict], tau: float, baseline: str) -> dict:
    """Same random-expert draws as _reference_experts (seed 42, 20 draws)."""
    y = np.asarray([r["y"] for r in rows_t], dtype=int)
    valid = np.asarray([r["valid"] for r in rows_t], dtype=bool)
    s = np.asarray([r["s_llm"] for r in rows_t], dtype=float)
    g = (s >= 0.5).astype(int)
    p = np.asarray([r["p_gate"] if baseline == "H3B_GATE" else r["s_sup_lr"] for r in rows_t], dtype=float)
    h = (p >= tau).astype(int)
    rate = float(g[valid].mean()) if valid.any() else 0.0
    rng = np.random.default_rng(mod.SEED)
    for _ in ("ALL-0", "ALL-1"):
        pass  # _reference_experts draws nothing for these; rng order unchanged
    reps = []
    for _ in range(20):
        draw = (rng.random(len(y)) < rate).astype(int)
        reps.append(mod._repair_harm(y, h, draw, np.ones_like(valid))["total"]["repair"])
    llm = mod._repair_harm(y, h, g, valid)["total"]["repair"]
    p95 = float(np.percentile(reps, 95))
    p975 = float(np.percentile(reps, 97.5))
    return {"baseline": baseline, "random_expert_repairs_20": reps,
            "llm_correct_repairs": int(llm), "p95": p95, "p97_5": p975,
            "criterion_registered_p95_met": bool(llm <= p95),
            "criterion_lock_p97_5_met": bool(llm <= p975)}


def diff_json(a, b, path="", tol=1e-12, out=None):
    out = [] if out is None else out
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append(f"{path}/{k}: key only in one side")
            else:
                diff_json(a[k], b[k], f"{path}/{k}", tol, out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path}: list length {len(a)} vs {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            diff_json(x, y, f"{path}[{i}]", tol, out)
    elif isinstance(a, float) or isinstance(b, float):
        if a is None or b is None or not math.isclose(float(a), float(b), rel_tol=0, abs_tol=tol):
            out.append(f"{path}: {a} vs {b}")
    elif a != b:
        out.append(f"{path}: {a!r} vs {b!r}")
    return out


def count_leaves(v) -> int:
    if isinstance(v, dict):
        return sum(count_leaves(x) for x in v.values())
    if isinstance(v, list):
        return sum(count_leaves(x) for x in v)
    return 1


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--mode", choices=("control", "canonical"), required=True)
    args = ap.parse_args()

    mod = load_module()
    stats = mod._load_grace_stats(SUMMARY)
    manifest = mod.read_json(LOCK_RUN / "analysis_manifest.json")
    out_dir = OUT_ROOT / f"step6_lock_64fb2c99d904_rerun_{args.mode}_b2_20261125"
    summary = {"schema": "step6_rerun_v1", "mode": args.mode,
               "base_lock_run": LOCK_RUN.relative_to(SUMMARY).as_posix(),
               "base_lock_b2_source_root": manifest["b2_source_root"],
               "b2_source_root": (B2_CANONICAL.relative_to(SUMMARY).as_posix()
                                  if args.mode == "canonical" else manifest["b2_source_root"]),
               "analysis_script_sha256": mod.sha256_file(HERE / "step6_complementarity.py"),
               "rerun_script_sha256": mod.sha256_file(Path(__file__).resolve()),
               "runtime_versions": {n: importlib.metadata.version(n)
                                    for n in ("numpy", "scipy", "scikit-learn")},
               "datasets": {}}

    for dataset in mod.DATASETS:
        rows = {}
        for split in mod.SPLITS:
            path = LOCK_RUN / dataset / f"joined_{split}.csv"
            want = manifest["join_outputs"][f"{dataset}/{split}"]["sha256"]
            if mod.sha256_file(path) != want:
                # Windows checkout may hold CRLF; the lock hashed the LF file.
                lf = path.read_bytes().replace(b"\r\n", b"\n")
                if hashlib.sha256(lf).hexdigest() != want:
                    raise SystemExit(f"FAIL joined CSV hash {dataset}/{split}")
            rows[split] = read_joined(path)
        val, test = rows["validation"], rows["test"]
        info = {}
        if args.mode == "canonical":
            info = {s: apply_canonical_b2(mod, rows[s], dataset, s) for s in mod.SPLITS}
        Xv = load_x(mod, manifest, dataset, "validation", [r["id"] for r in val])
        Xt = load_x(mod, manifest, dataset, "test", [r["id"] for r in test])
        arr = lambda rs, k, t: np.asarray([r[k] for r in rs], dtype=t)
        tau_gate = manifest["inputs"][f"{dataset}/validation"]["h3b"]["tau_gate_train_oof"]
        tau_sup = manifest["inputs"][f"{dataset}/validation"]["tau_sup_lr_validation"]
        meta = mod._fit_paired_meta(
            stats, Xv, arr(val, "y", int), arr(val, "s_llm", float), arr(val, "valid", bool),
            arr(val, "p_gate", float), arr(val, "group", object),
            Xt, arr(test, "y", int), arr(test, "s_llm", float), arr(test, "valid", bool),
            arr(test, "p_gate", float), arr(test, "group", object))
        # Table D (paper): shared threshold = P_pre validation-OOF tau applied to both.
        scores: dict = {}
        sel = mod._fit_paired_meta(
            stats, Xv, arr(val, "y", int), arr(val, "s_llm", float), arr(val, "valid", bool),
            arr(val, "p_gate", float), arr(val, "group", object),
            Xt, arr(test, "y", int), arr(test, "s_llm", float), arr(test, "valid", bool),
            arr(test, "p_gate", float), arr(test, "group", object), test_scores=scores)
        tau_shared = sel["thresholds_selected_on_validation_oof"]["P_pre"]
        yt_ = arr(test, "y", int)
        pre_pred = (scores["P-PRE"] >= tau_shared).astype(int)
        post_pred = (scores["P-POST"] >= tau_shared).astype(int)
        shared_ci = stats.paired_bootstrap(yt_, pre_pred, post_pred, stats.mcc, n_boot=mod.N_BOOT,
                                           seed=mod.BOOTSTRAP_SEED, groups=arr(test, "group", object))
        shared = {"tau_shared": tau_shared, "mcc_pre": stats.mcc(yt_, pre_pred),
                  "mcc_post": stats.mcc(yt_, post_pred), "delta_mcc_ci95": shared_ci.to_dict(),
                  "margin": mod.DELTA_MCC_META,
                  "passes_h52_margin": bool(shared_ci.hi < mod.DELTA_MCC_META)}
        old = mod.read_json(LOCK_RUN / dataset / "complementarity_step6.json")
        result = {
            "n_validation": len(val), "n_test": len(test),
            "n_validation_groups": old["n_validation_groups"], "n_test_groups": old["n_test_groups"],
            "group_unit": old["group_unit"],
            "gate_tau_train_oof": tau_gate, "sup_lr_tau_validation": tau_sup,
            "p_pre_vs_p_post": meta,
            "h3b_gate_vs_b2": mod._repair_and_route(stats, val, Xv, test, Xt, "H3B_GATE", tau_gate, primary=True),
            "sup_lr_vs_b2": mod._repair_and_route(stats, val, Xv, test, Xt, "SUP-LR", tau_sup, primary=False),
            "b2_valid_n_test": int(sum(r["valid"] for r in test)),
            "b2_invalid_n_test": int(sum(not r["valid"] for r in test)),
        }
        mod.write_json(out_dir / dataset / "complementarity_step6.json", result)
        mod._write_join(out_dir / dataset, "validation", val)
        mod._write_join(out_dir / dataset, "test", test)
        written = mod.read_json(out_dir / dataset / "complementarity_step6.json")
        diffs = diff_json(old, written)
        p95 = {"H3B_GATE": repair_p95(mod, test, tau_gate, "H3B_GATE"),
               "SUP-LR": repair_p95(mod, test, tau_sup, "SUP-LR")}
        lock_hi = written["h3b_gate_vs_b2"]["h5_3_registered_checks"]["random_expert_repair_reference"]["repair_hi_97_5"]
        if not math.isclose(p95["H3B_GATE"]["p97_5"], lock_hi, abs_tol=1e-9):
            raise SystemExit(f"FAIL p97.5 replication {dataset}: {p95['H3B_GATE']['p97_5']} vs {lock_hi}")
        summary["datasets"][dataset] = {
            "b2_inputs": info, "leaves_total": count_leaves(old),
            "leaves_differing_vs_base_lock": len(diffs), "differences_vs_base_lock": diffs,
            "h5_3_repair_percentiles": p95,
            "table_d_shared_threshold": shared,
            "output_sha256": mod.sha256_file(out_dir / dataset / "complementarity_step6.json")}
        print(f"{args.mode} {dataset}: {len(diffs)} differing leaves of {count_leaves(old)}; "
              f"repairs={p95['H3B_GATE']['llm_correct_repairs']} p95={p95['H3B_GATE']['p95']} "
              f"p97.5={p95['H3B_GATE']['p97_5']}; shared tau={tau_shared} "
              f"dMCC={shared_ci.delta:+.6f} [{shared_ci.lo:+.6f}; {shared_ci.hi:+.6f}]", flush=True)

    mod.write_json(out_dir / "rerun_summary.json", summary)
    print(f"Wrote {out_dir.relative_to(SUMMARY).as_posix()}")


if __name__ == "__main__":
    main()
