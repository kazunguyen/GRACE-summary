from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
from typing import Any

import numpy as np
from scipy.special import logit
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


DATASETS = ("devign", "reveal")
SPLITS = ("validation", "test")
SEED = 42
N_FOLDS = 3
N_BOOT = 5000
BOOTSTRAP_SEED = 20261117
DELTA_MCC_META = 0.02
BUDGETS = (0.05, 0.10, 0.25)
RANDOM_ROUTER_SEEDS = 20
RIDGE_ALPHA = 10.0
LOGISTIC_C = 1.0


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fingerprint(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, np.ndarray):
        return _jsonable(value.tolist())
    if isinstance(value, np.generic):
        return _jsonable(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(_jsonable(value), ensure_ascii=False,
                               sort_keys=True, indent=2, allow_nan=False) + "\n",
                     encoding="utf-8")
    os.replace(temp, path)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    with temp.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temp, path)


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def _safe_score(value: Any, valid: bool, context: str) -> float:
    if not valid:
        return 0.5
    score = float(value)
    if not math.isfinite(score) or not 0.0 <= score <= 1.0:
        raise ValueError(f"Invalid continuous expert score at {context}: {value}")
    return score


def _load_grace_stats(summary_root: Path):
    source = summary_root / "01_Author_Baseline_Unified" / "diagnostic_kit" / "src"
    import sys
    if str(source) not in sys.path:
        sys.path.insert(0, str(source))
    from grace_diag import stats
    return stats


def _locked_rows(summary_root: Path, lock: dict[str, Any], dataset: str,
                 split: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    entry = lock["frozen_data"]["datasets"][dataset]
    raw_spec = entry["raw"][split]
    raw_path = summary_root / raw_spec["path"]
    if not raw_path.is_file() or sha256_file(raw_path) != raw_spec["sha256"]:
        raise ValueError(f"Locked raw split hash mismatch: {raw_path}")
    rows = read_jsonl(raw_path)
    manifest_spec = entry["manifests"][split]
    manifest_path = summary_root / manifest_spec["path"]
    if not manifest_path.is_file() or sha256_file(manifest_path) != manifest_spec["sha256"]:
        raise ValueError(f"Frozen row manifest hash mismatch: {manifest_path}")
    manifest_rows = read_jsonl(manifest_path)
    if len(rows) != len(manifest_rows):
        raise ValueError(f"Raw/manifest row count mismatch for {dataset}/{split}")

    ids: set[str] = set()
    joined = {}
    for raw, frozen in zip(rows, manifest_rows):
        rid = str(raw["id"])
        if rid in ids:
            raise ValueError(f"Duplicate locked ID: {dataset}/{split}/{rid}")
        ids.add(rid)
        label = int(raw["target"])
        code = str(raw["func"])
        code_hash = hashlib.sha256(code.encode("utf-8")).hexdigest()
        if (rid != frozen["id"] or code_hash != frozen["code_sha256"]
                or label != int(frozen["label"])):
            raise ValueError(f"Frozen ID/code/label mismatch: {dataset}/{split}/{rid}")
        if dataset == "devign":
            group = raw.get("commit_id")
            group_unit = "commit_id"
        else:
            # In the locked ReVeal source, code_sha256 is the function/file identity.
            group = raw.get("file_hash") or code_hash
            group_unit = "file_hash (code_sha256 fallback)"
        if group in (None, ""):
            raise ValueError(f"Missing preregistered cluster ID: {dataset}/{split}/{rid}")
        joined[rid] = {"id": rid, "y": label, "group": str(group),
                       "code_sha256": code_hash, "raw": raw}
    if not rows:
        raise ValueError(f"Empty locked split: {dataset}/{split}")
    return list(joined.values()), {"path": raw_spec["path"], "sha256": raw_spec["sha256"],
                                   "manifest_path": manifest_spec["path"],
                                   "manifest_sha256": manifest_spec["sha256"],
                                   "rows": len(rows), "group_unit": group_unit}


def _read_b2(b2_root: Path, dataset: str, split: str) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    records_path = b2_root / dataset / split / "records.jsonl"
    run_manifest_path = b2_root / dataset / split / "run_manifest.json"
    if not records_path.is_file() or not run_manifest_path.is_file():
        raise FileNotFoundError(f"B2 records/manifest missing: {records_path}")
    rows = read_jsonl(records_path)
    manifest = read_json(run_manifest_path)
    if not rows:
        raise ValueError(f"Empty B2 output: {records_path}")
    by_id = {}
    for row in rows:
        rid = str(row.get("id", ""))
        if not rid or rid in by_id:
            raise ValueError(f"Missing or duplicate B2 ID in {records_path}: {rid}")
        if row.get("arm") != "B2" or str(row.get("seed")) != str(SEED):
            raise ValueError(f"Unexpected B2 arm/seed in {records_path}: {rid}")
        if row.get("dataset") != dataset or row.get("split") != split:
            raise ValueError(f"B2 dataset/split tag mismatch: {records_path}/{rid}")
        valid = _bool(row.get("valid", False))
        by_id[rid] = {"s_llm": _safe_score(row.get("s"), valid, rid),
                      "valid": valid, "label": int(row["label"]),
                      "prompt_sha256": row.get("prompt_sha256"),
                      "seed": str(row.get("seed")),
                      "arm": row.get("arm")}
    if len({r["model_repo"] for r in rows}) > 1 or len({r["quantization"] for r in rows}) > 1:
        raise ValueError(f"B2 output mixes model or quantization: {records_path}")
    return by_id, {"records_path": records_path.as_posix(),
                   "records_sha256": sha256_file(records_path),
                   "run_manifest_path": run_manifest_path.as_posix(),
                   "run_manifest_sha256": sha256_file(run_manifest_path),
                   "rows": len(rows), "arm": "B2", "seed": SEED,
                   "valid_n": sum(x["valid"] for x in by_id.values()),
                   "model_repo": rows[0].get("model_repo"),
                   "quantization": rows[0].get("quantization"),
                   "scoring": manifest.get("scoring"),
                   "prompt_set_sha256": manifest.get("prompt_set_sha256")}


def _load_h3b(step6_root: Path, output_root: Path, lock_sha: str,
              dataset: str, split: str) -> tuple[dict[str, dict[str, Any]], np.ndarray, dict[str, Any]]:
    dataset_root = output_root / dataset
    manifest_path = dataset_root / "h3b_export_manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"H3-B export manifest missing: {manifest_path}")
    manifest = read_json(manifest_path)
    if manifest.get("step6_lock_sha256") != lock_sha:
        raise ValueError(f"H3-B export tied to different lock: {manifest_path}")
    xinfo, ginfo = manifest["outputs"][split]["xpre"], manifest["outputs"][split]["gate"]
    xpath, gpath = output_root / xinfo["path"], output_root / ginfo["path"]
    if sha256_file(xpath) != xinfo["sha256"] or sha256_file(gpath) != ginfo["sha256"]:
        raise ValueError(f"H3-B file hash mismatch for {dataset}/{split}")
    with np.load(xpath, allow_pickle=False) as archive:
        if not {"X", "ids", "feature_names"} <= set(archive.files):
            raise ValueError(f"H3-B xpre schema mismatch: {xpath}")
        X = np.asarray(archive["X"], dtype=np.float64)
        ids = archive["ids"].astype(str).tolist()
        feature_names = archive["feature_names"].astype(str).tolist()
    if X.shape != (len(ids), 34) or len(feature_names) != 34 or not np.isfinite(X).all():
        raise ValueError(f"H3-B xpre dimensions/content mismatch: {xpath}")
    with gpath.open(encoding="utf-8", newline="") as stream:
        gate_rows = list(csv.DictReader(stream))
    if [r["id"] for r in gate_rows] != ids:
        raise ValueError(f"H3-B gate/xpre ID order mismatch: {dataset}/{split}")
    gate_by_id = {}
    for row in gate_rows:
        rid = row["id"]
        if rid in gate_by_id:
            raise ValueError(f"Duplicate H3-B gate ID: {rid}")
        p = float(row["p_gate"])
        if not math.isfinite(p) or not 0 <= p <= 1:
            raise ValueError(f"Invalid p_gate: {dataset}/{split}/{rid}")
        gate_by_id[rid] = {"p_gate": p, "label": int(row["y"])}
    info = {"manifest_path": manifest_path.as_posix(),
            "manifest_sha256": sha256_file(manifest_path),
            "xpre_path": xinfo["path"], "xpre_sha256": xinfo["sha256"],
            "gate_path": ginfo["path"], "gate_sha256": ginfo["sha256"],
            "rows": len(ids), "shape": list(X.shape),
            "gate_winner": manifest["h3b_source_algorithm"]["winner"],
            "tau_gate_train_oof": float(manifest["h3b_source_algorithm"]["tau_train_oof"]),
            "feature_names": feature_names}
    return gate_by_id, X, {"info": info, "ids": ids}


def _load_sup_lr(step6_root: Path, dataset: str, split: str) -> tuple[dict[str, float], float, dict[str, Any]]:
    base = step6_root / "runs" / "anchor" / "locked_step6_20261108" / dataset
    scores_path = base / "anchor_scores.csv"
    summary_path = base / "anchor_summary.json"
    run_manifest_path = base / "anchor_run_manifest.json"
    if not all(p.is_file() for p in (scores_path, summary_path, run_manifest_path)):
        raise FileNotFoundError(f"SUP-LR score artifacts missing for {dataset}")
    run_manifest = read_json(run_manifest_path)
    if run_manifest.get("dataset") != dataset:
        raise ValueError(f"SUP-LR manifest dataset mismatch: {run_manifest_path}")
    if run_manifest.get("anchor_scores_sha256") != sha256_file(scores_path):
        raise ValueError(f"SUP-LR score hash mismatch: {scores_path}")
    with scores_path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    selected = [r for r in rows if r["split"] == split and r["arm"] == "SUP-LR"
                and int(r["seed"]) == SEED]
    by_id = {r["id"]: float(r["score"]) for r in selected}
    if len(by_id) != len(selected) or any(not math.isfinite(v) or not 0 <= v <= 1 for v in by_id.values()):
        raise ValueError(f"Invalid/duplicate SUP-LR scores for {dataset}/{split}")
    summary = read_json(summary_path)
    matches = [r for r in summary if r["arm"] == "SUP-LR" and int(r["seed"]) == SEED]
    if len(matches) != 1:
        raise ValueError(f"Expected one SUP-LR seed-42 threshold for {dataset}")
    tau = float(matches[0]["tau"])
    return by_id, tau, {"scores_path": scores_path.as_posix(),
                        "scores_sha256": sha256_file(scores_path),
                        "summary_path": summary_path.as_posix(),
                        "summary_sha256": sha256_file(summary_path),
                        "run_manifest_path": run_manifest_path.as_posix(),
                        "run_manifest_sha256": sha256_file(run_manifest_path),
                        "rows": len(selected), "tau_validation_mcc": tau}


def _join_split(step6_root: Path, summary_root: Path, lock: dict[str, Any],
                lock_sha: str, b2_root: Path, h3b_root: Path,
                dataset: str, split: str) -> tuple[list[dict[str, Any]], np.ndarray, dict[str, Any]]:
    frozen_rows, frozen_info = _locked_rows(summary_root, lock, dataset, split)
    ids = [r["id"] for r in frozen_rows]
    b2, b2_info = _read_b2(b2_root, dataset, split)
    h3b, X_pre, h3b_loaded = _load_h3b(step6_root, h3b_root, lock_sha, dataset, split)
    sup, tau_sup, sup_info = _load_sup_lr(step6_root, dataset, split)
    sets = {"frozen": set(ids), "B2": set(b2), "H3-B": set(h3b), "SUP-LR": set(sup)}
    if any(value != sets["frozen"] for value in sets.values()):
        detail = {key: {"n": len(value), "missing": len(sets["frozen"] - value),
                        "extra": len(value - sets["frozen"])} for key, value in sets.items()}
        raise ValueError(f"ID coverage mismatch for {dataset}/{split}: {detail}")
    if len(h3b_loaded["ids"]) != len(ids) or set(h3b_loaded["ids"]) != sets["frozen"]:
        raise ValueError(f"H3-B xpre IDs do not cover locked split: {dataset}/{split}")
    x_index = {rid: i for i, rid in enumerate(h3b_loaded["ids"])}
    joined, ordered_X = [], np.empty_like(X_pre)
    for i, frozen in enumerate(frozen_rows):
        rid = frozen["id"]
        if b2[rid]["label"] != frozen["y"] or h3b[rid]["label"] != frozen["y"]:
            raise ValueError(f"Label mismatch across locked/B2/H3-B at {dataset}/{split}/{rid}")
        ordered_X[i] = X_pre[x_index[rid]]
        joined.append({"id": rid, "y": frozen["y"], "p_gate": h3b[rid]["p_gate"],
                       "s_llm": b2[rid]["s_llm"], "valid": b2[rid]["valid"],
                       "group": frozen["group"], "s_sup_lr": sup[rid],
                       "code_sha256": frozen["code_sha256"]})
    info = {"locked_split": frozen_info, "b2": b2_info,
            "h3b": h3b_loaded["info"], "sup_lr": sup_info,
            "tau_sup_lr_validation": tau_sup,
            "join": {"rows": len(joined), "all_ids_exact": True,
                     "labels_exact": True, "order": "frozen raw split order"}}
    return joined, ordered_X, info


def _repair_harm(y: np.ndarray, h: np.ndarray, expert: np.ndarray,
                 valid: np.ndarray) -> dict[str, Any]:
    result = {}
    for cls in (0, 1):
        mask = y == cls
        ok = mask & valid
        result[f"y={cls}"] = {
            "n_all": int(mask.sum()), "n_expert_valid": int(ok.sum()),
            "repair": int((ok & (h != y) & (expert == y)).sum()),
            "harm": int((ok & (h == y) & (expert != y)).sum()),
            "both_right": int((ok & (h == y) & (expert == y)).sum()),
            "both_wrong": int((ok & (h != y) & (expert != y)).sum()),
        }
    result["total"] = {key: sum(result[f"y={c}"][key] for c in (0, 1))
                       for key in ("n_all", "n_expert_valid", "repair", "harm",
                                   "both_right", "both_wrong")}
    result["total"]["invalid_expert"] = int((~valid).sum())
    result["total"]["coverage"] = float(valid.mean()) if len(valid) else 0.0
    return result


def _reference_experts(y: np.ndarray, h: np.ndarray, expert: np.ndarray,
                       valid: np.ndarray, seed: int = SEED) -> dict[str, Any]:
    valid_rate = float(expert[valid].mean()) if valid.any() else 0.0
    result = {}
    for name, output in (("ALL-0", np.zeros_like(y)), ("ALL-1", np.ones_like(y))):
        result[name] = _repair_harm(y, h, output, np.ones_like(valid))
    rng = np.random.default_rng(seed)
    reps = []
    for _ in range(20):
        draw = (rng.random(len(y)) < valid_rate).astype(int)
        reps.append(_repair_harm(y, h, draw, np.ones_like(valid))["total"])
    result[f"RANDOM(rate={valid_rate:.6f})"] = {
        "n_random": 20,
        **{key: {"mean": float(np.mean([row[key] for row in reps])),
                 "lo": float(np.percentile([row[key] for row in reps], 2.5)),
                 "hi": float(np.percentile([row[key] for row in reps], 97.5))}
           for key in ("repair", "harm", "both_right", "both_wrong")},
    }
    return result


def _oracle_accuracy(y: np.ndarray, h: np.ndarray, expert: np.ndarray,
                     valid: np.ndarray) -> dict[str, float]:
    return {"oracle_accuracy": float(((h == y) | ((expert == y) & valid)).mean()),
            "classifier_accuracy": float((h == y).mean()),
            "expert_accuracy_valid": float((expert[valid] == y[valid]).mean()) if valid.any() else 0.0}


def _cluster_bootstrap_benefit_vs_random_ba(
        stats, y: np.ndarray, benefit: np.ndarray, random_predictions: list[np.ndarray],
        groups: np.ndarray, n_boot: int = N_BOOT,
        seed: int = BOOTSTRAP_SEED) -> dict[str, Any]:
    """Paired cluster-bootstrap CI for benefit BA minus mean random-router BA.

    Each replicate resamples test clusters and, independently, the 20 random-router
    seeds with replacement. The point estimate uses all observed random seeds.
    """
    y = np.asarray(y, dtype=int)
    benefit = np.asarray(benefit, dtype=int)
    random_predictions = [np.asarray(pred, dtype=int) for pred in random_predictions]
    groups = np.asarray(groups)
    if not random_predictions:
        raise ValueError("At least one random-router prediction is required")
    if not (len(y) == len(benefit) == len(groups)
            and all(len(pred) == len(y) for pred in random_predictions)):
        raise ValueError("H5.3 bootstrap inputs must have identical row counts")

    unique, inverse = np.unique(groups, return_inverse=True)
    members = [np.flatnonzero(inverse == group_index) for group_index in range(len(unique))]
    rng = np.random.default_rng(seed)
    deltas = []
    degenerate = 0
    for _ in range(n_boot):
        picked_groups = rng.integers(0, len(unique), len(unique))
        indices = np.concatenate([members[group_index] for group_index in picked_groups])
        picked_seeds = rng.integers(0, len(random_predictions), len(random_predictions))
        benefit_ba = stats.balanced_accuracy(y[indices], benefit[indices])
        random_ba = [stats.balanced_accuracy(y[indices], random_predictions[i][indices])
                     for i in picked_seeds]
        if benefit_ba is None or not np.isfinite(benefit_ba) or not np.all(np.isfinite(random_ba)):
            degenerate += 1
            continue
        deltas.append(float(benefit_ba - np.mean(random_ba)))

    point_benefit = stats.balanced_accuracy(y, benefit)
    point_random = float(np.mean([stats.balanced_accuracy(y, pred)
                                  for pred in random_predictions]))
    if not deltas:
        lo = hi = float("nan")
    else:
        lo, hi = (float(value) for value in np.percentile(deltas, [2.5, 97.5]))
    return {"delta": float(point_benefit - point_random), "lo": lo, "hi": hi,
            "n_boot": n_boot, "n_degenerate": degenerate, "seed": seed,
            "unit": "cluster", "random_router_seeds": len(random_predictions),
            "random_seed_resampling": "with replacement per cluster-bootstrap replicate"}


def _threshold_metrics(stats, y: np.ndarray, score: np.ndarray, tau: float) -> dict[str, Any]:
    pred = (score >= tau).astype(int)
    return {"tau": float(tau), "metrics": stats.thresholded_metrics(y, pred),
            "auroc": stats.auroc(y, score), "auprc": stats.auprc(y, score),
            "prediction": pred}


def _expert_features(s: np.ndarray, valid: np.ndarray, p: np.ndarray) -> np.ndarray:
    safe = np.where(valid, s, 0.5)
    return np.column_stack([safe, valid.astype(float), safe * p, safe - p])


def _fit_paired_meta(stats, Xv, yv, sv, vv, pv, gv,
                     Xt, yt, st, vt, pt, gt) -> dict[str, Any]:
    folds = list(StratifiedGroupKFold(n_splits=N_FOLDS, shuffle=True,
                                      random_state=SEED).split(Xv, yv, gv))
    if len(folds) != N_FOLDS:
        raise ValueError("P_pre/P_post did not produce the preregistered 3 folds")
    for train_idx, held_idx in folds:
        if set(np.asarray(gv)[train_idx]) & set(np.asarray(gv)[held_idx]):
            raise ValueError("Group leakage across P_pre/P_post folds")
        if len(np.unique(yv[train_idx])) != 2 or len(np.unique(yv[held_idx])) != 2:
            raise ValueError("A P_pre/P_post fold lacks a class")

    Xpost_v = np.column_stack([Xv, _expert_features(sv, vv, pv)])
    oof_pre, oof_post = np.full(len(yv), np.nan), np.full(len(yv), np.nan)
    fold_manifest = []
    for fold_idx, (train_idx, held_idx) in enumerate(folds):
        pre = make_pipeline(StandardScaler(), LogisticRegression(
            C=LOGISTIC_C, max_iter=2000, random_state=SEED))
        post = make_pipeline(StandardScaler(), LogisticRegression(
            C=LOGISTIC_C, max_iter=2000, random_state=SEED))
        pre.fit(Xv[train_idx], yv[train_idx])
        post.fit(Xpost_v[train_idx], yv[train_idx])
        oof_pre[held_idx] = pre.predict_proba(Xv[held_idx])[:, 1]
        oof_post[held_idx] = post.predict_proba(Xpost_v[held_idx])[:, 1]
        fold_manifest.append({"fold": fold_idx,
                              "train_groups_sha256": fingerprint(sorted(np.asarray(gv)[train_idx].tolist())),
                              "held_groups_sha256": fingerprint(sorted(np.asarray(gv)[held_idx].tolist())),
                              "n_train": int(len(train_idx)), "n_held": int(len(held_idx))})
    # Registered fallback: invalid expert cases receive exactly P_pre's prediction/score.
    oof_post[~vv] = oof_pre[~vv]
    tau_pre, mcc_pre = stats.pick_threshold(yv, oof_pre)
    tau_post, mcc_post = stats.pick_threshold(yv, oof_post)
    pred_pre_oof = (oof_pre >= tau_pre).astype(int)
    pred_post_oof = (oof_post >= tau_post).astype(int)
    ci_val_mcc = stats.paired_bootstrap(yv, pred_pre_oof, pred_post_oof, stats.mcc,
                                        n_boot=N_BOOT, seed=BOOTSTRAP_SEED, groups=gv)
    ci_val_auc = stats.paired_bootstrap(yv, oof_pre, oof_post, stats.auroc,
                                        n_boot=N_BOOT, seed=BOOTSTRAP_SEED, groups=gv)

    model_pre = make_pipeline(StandardScaler(), LogisticRegression(
        C=LOGISTIC_C, max_iter=2000, random_state=SEED)).fit(Xv, yv)
    model_post = make_pipeline(StandardScaler(), LogisticRegression(
        C=LOGISTIC_C, max_iter=2000, random_state=SEED)).fit(Xpost_v, yv)
    Xpost_t = np.column_stack([Xt, _expert_features(st, vt, pt)])
    score_pre_test = model_pre.predict_proba(Xt)[:, 1]
    score_post_test = model_post.predict_proba(Xpost_t)[:, 1]
    score_post_test[~vt] = score_pre_test[~vt]
    pred_pre_test = (score_pre_test >= tau_pre).astype(int)
    pred_post_test = (score_post_test >= tau_post).astype(int)
    ci_test_mcc = stats.paired_bootstrap(yt, pred_pre_test, pred_post_test, stats.mcc,
                                         n_boot=N_BOOT, seed=BOOTSTRAP_SEED, groups=gt)
    ci_test_auc = stats.paired_bootstrap(yt, score_pre_test, score_post_test, stats.auroc,
                                         n_boot=N_BOOT, seed=BOOTSTRAP_SEED, groups=gt)
    return {
        "protocol": {"model": "LogisticRegression", "C": LOGISTIC_C,
                     "folds": N_FOLDS, "fold_strategy": "StratifiedGroupKFold",
                     "scaler": "StandardScaler", "same_fold_assignments": True,
                     "threshold_grid": "0.01..0.99 step 0.01; MCC; tie closest to 0.5",
                     "invalid_fallback": "P_post score and prediction set to P_pre"},
        "thresholds_selected_on_validation_oof": {"P_pre": float(tau_pre),
                                                   "P_post": float(tau_post),
                                                   "P_pre_mcc_oof": mcc_pre,
                                                   "P_post_mcc_oof": mcc_post},
        "validation_oof": {
            "P_pre": {"metrics": stats.thresholded_metrics(yv, pred_pre_oof),
                      "auroc": stats.auroc(yv, oof_pre), "auprc": stats.auprc(yv, oof_pre)},
            "P_post": {"metrics": stats.thresholded_metrics(yv, pred_post_oof),
                       "auroc": stats.auroc(yv, oof_post), "auprc": stats.auprc(yv, oof_post)},
            "delta_mcc_post_minus_pre_ci": ci_val_mcc.to_dict(),
            "delta_auroc_post_minus_pre_ci": ci_val_auc.to_dict(),
            "folds": fold_manifest},
        "test": {
            "P_pre": {"metrics": stats.thresholded_metrics(yt, pred_pre_test),
                      "auroc": stats.auroc(yt, score_pre_test), "auprc": stats.auprc(yt, score_pre_test)},
            "P_post": {"metrics": stats.thresholded_metrics(yt, pred_post_test),
                       "auroc": stats.auroc(yt, score_post_test), "auprc": stats.auprc(yt, score_post_test)},
            "delta_mcc_post_minus_pre_ci": ci_test_mcc.to_dict(),
            "delta_auroc_post_minus_pre_ci": ci_test_auc.to_dict(),
            "verdict_mcc_delta_0_02": stats.verdict(ci_test_mcc, DELTA_MCC_META)},
    }


def _repair_and_route(stats, joined_v, Xv, joined_t, Xt,
                      baseline: str, tau: float, primary: bool) -> dict[str, Any]:
    yv = np.asarray([r["y"] for r in joined_v], dtype=int)
    yt = np.asarray([r["y"] for r in joined_t], dtype=int)
    valid_v = np.asarray([r["valid"] for r in joined_v], dtype=bool)
    valid_t = np.asarray([r["valid"] for r in joined_t], dtype=bool)
    s_v = np.asarray([r["s_llm"] for r in joined_v], dtype=float)
    s_t = np.asarray([r["s_llm"] for r in joined_t], dtype=float)
    g_v, g_t = (s_v >= 0.5).astype(int), (s_t >= 0.5).astype(int)
    p_v = np.asarray([r["p_gate"] if baseline == "H3B_GATE" else r["s_sup_lr"]
                      for r in joined_v], dtype=float)
    p_t = np.asarray([r["p_gate"] if baseline == "H3B_GATE" else r["s_sup_lr"]
                      for r in joined_t], dtype=float)
    h_v, h_t = (p_v >= tau).astype(int), (p_t >= tau).astype(int)
    groups_t = np.asarray([r["group"] for r in joined_t])
    ids_t = [r["id"] for r in joined_t]

    # The benefit router is trained only on validation labels/predictions.
    target = ((h_v != yv) & (g_v == yv)).astype(float) - ((h_v == yv) & (g_v != yv)).astype(float)
    benefit_model = make_pipeline(StandardScaler(), Ridge(alpha=RIDGE_ALPHA))
    benefit_model.fit(Xv[valid_v], target[valid_v])
    benefit_t = benefit_model.predict(Xt)
    confidence_t = -np.abs(logit(np.clip(p_t, 1e-6, 1 - 1e-6))
                           - logit(np.full(len(p_t), tau)))
    oracle_rank = ((h_t != yt) & (g_t == yt) & valid_t).astype(float)

    def route(rank_score: np.ndarray, q: float, oracle: bool = False):
        k = int(math.ceil(q * len(h_t)))
        ties = np.asarray([int(hashlib.sha256(rid.encode()).hexdigest()[:8], 16)
                           for rid in ids_t], dtype=np.uint64)
        order = np.lexsort((ties, -np.asarray(rank_score, dtype=float)))
        mask = np.zeros(len(h_t), dtype=bool)
        mask[order[:k]] = True
        use = mask & valid_t
        if oracle:
            use &= oracle_rank.astype(bool)
        pred = h_t.copy()
        pred[use] = g_t[use]
        return pred, mask

    policies = {}
    random_predictions_by_budget = {}
    rng = np.random.default_rng(SEED)
    for q in BUDGETS:
        q_rows = {}
        for name, rank, is_oracle in (("confidence", confidence_t, False),
                                      ("benefit", benefit_t, False),
                                      ("oracle", oracle_rank, True)):
            pred, mask = route(rank, q, oracle=is_oracle)
            q_rows[name] = {"metrics": stats.thresholded_metrics(yt, pred),
                            "requested_queries": int(mask.sum()),
                            "effective_valid_queries": int((mask & valid_t).sum()),
                            "repair_harm": _repair_harm(yt, h_t, pred, np.ones_like(valid_t))["total"]}
        random_metrics = {key: [] for key in ("mcc", "balanced_accuracy", "f1")}
        random_queries = []
        random_predictions = []
        for _ in range(RANDOM_ROUTER_SEEDS):
            pred, mask = route(rng.random(len(yt)), q)
            random_predictions.append(pred)
            m = stats.thresholded_metrics(yt, pred)
            random_queries.append(int(mask.sum()))
            for key in random_metrics:
                random_metrics[key].append(float("nan") if m[key] is None else float(m[key]))
        random_predictions_by_budget[q] = random_predictions
        q_rows["random_20_seed"] = {
            "n_random": RANDOM_ROUTER_SEEDS, "requested_queries_each": random_queries,
            "metrics": {key: {"mean": float(np.nanmean(vals)),
                               "lo": float(np.nanpercentile(vals, 2.5)),
                               "hi": float(np.nanpercentile(vals, 97.5))}
                        for key, vals in random_metrics.items()}}
        policies[f"q={q:.2f}"] = q_rows

    pred_benefit_10, _ = route(benefit_t, 0.10)
    pred_confidence_10, _ = route(confidence_t, 0.10)
    ci_benefit_confidence_ba = stats.paired_bootstrap(
        yt, pred_confidence_10, pred_benefit_10, stats.balanced_accuracy,
        n_boot=N_BOOT, seed=BOOTSTRAP_SEED, groups=groups_t)
    ci_benefit_confidence = stats.paired_bootstrap(
        yt, pred_confidence_10, pred_benefit_10, stats.mcc,
        n_boot=N_BOOT, seed=BOOTSTRAP_SEED, groups=groups_t)
    ci_benefit_random_ba = _cluster_bootstrap_benefit_vs_random_ba(
        stats, yt, pred_benefit_10, random_predictions_by_budget[0.10], groups_t,
        n_boot=N_BOOT, seed=BOOTSTRAP_SEED)

    p_base_test = _threshold_metrics(stats, yt, p_t, tau)
    h_base = p_base_test.pop("prediction")
    repair_harm_llm = _repair_harm(yt, h_t, g_t, valid_t)
    reference_experts = _reference_experts(yt, h_t, g_t, valid_t)
    random_expert_key = next(key for key in reference_experts if key.startswith("RANDOM("))
    random_expert_repair_hi = reference_experts[random_expert_key]["repair"]["hi"]
    llm_correct_repairs = repair_harm_llm["total"]["repair"]
    h5_3_checks = {
        "primary_baseline": "H3B_GATE" if primary else "SUP-LR supplementary",
        "budget": 0.10,
        "benefit_minus_confidence_delta_balanced_accuracy_ci": ci_benefit_confidence_ba.to_dict(),
        "benefit_minus_confidence_delta_mcc_ci": ci_benefit_confidence.to_dict(),
        "benefit_minus_random_delta_balanced_accuracy_ci": ci_benefit_random_ba,
        "llm_correct_repairs": llm_correct_repairs,
        "random_expert_repair_reference": {
            "name": random_expert_key,
            "n_random": reference_experts[random_expert_key]["n_random"],
            "repair_mean": reference_experts[random_expert_key]["repair"]["mean"],
            "repair_lo_2_5": reference_experts[random_expert_key]["repair"]["lo"],
            "repair_hi_97_5": random_expert_repair_hi,
        },
        "criteria": {
            "benefit_vs_confidence_ba_upper_ci_lt_0_02":
                bool(ci_benefit_confidence_ba.hi < 0.02),
            "benefit_vs_confidence_mcc_upper_ci_lt_0_02":
                bool(ci_benefit_confidence.hi < 0.02),
            "benefit_vs_random_ba_upper_ci_lt_0_01":
                bool(ci_benefit_random_ba["hi"] < 0.01),
            "llm_repairs_not_above_random_expert_97_5_percentile":
                bool(llm_correct_repairs <= random_expert_repair_hi),
        },
    }
    h5_3_checks["all_routing_criteria_met"] = all(h5_3_checks["criteria"].values())
    return {
        "baseline": baseline,
        "tau": float(tau),
        "test_baseline": p_base_test,
        "test_repair_harm_llm_by_class": repair_harm_llm,
        "test_oracle_ceiling": _oracle_accuracy(yt, h_base, g_t, valid_t),
        "test_reference_experts": reference_experts,
        "routing_test": policies,
        "h5_3_registered_checks": h5_3_checks,
        "q10_benefit_minus_confidence_delta_balanced_accuracy_ci":
            ci_benefit_confidence_ba.to_dict(),
        "q10_benefit_minus_confidence_delta_mcc_ci": ci_benefit_confidence.to_dict(),
        "q10_benefit_minus_confidence_verdict_delta_0_02": stats.verdict(
            ci_benefit_confidence, 0.02) if primary else "supplementary; H5.3 primary is H3B_GATE",
    }


def _write_join(out_dir: Path, split: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    path = out_dir / f"joined_{split}.csv"
    fields = ["id", "y", "p_gate", "s_llm", "valid", "group", "s_sup_lr", "code_sha256"]
    serialized = [{**r, "valid": int(r["valid"]),
                   **{k: format(float(r[k]), ".17g") for k in ("p_gate", "s_llm", "s_sup_lr")}}
                  for r in rows]
    write_csv(path, fields, serialized)
    return {"path": path.name, "sha256": sha256_file(path), "rows": len(rows),
            "columns": fields}


def run_analysis(step6_root: Path, summary_root: Path, b2_root: Path) -> Path:
    step6_root, summary_root, b2_root = (p.resolve() for p in (step6_root, summary_root, b2_root))
    lock_path = step6_root / "step6_lock.json"
    adapter_path = step6_root / "cache" / "anchor_npz" / "adapter_manifest.json"
    protocol_path = summary_root / "configs" / "protocol.yaml"
    if not all(p.is_file() for p in (lock_path, adapter_path, protocol_path)):
        raise FileNotFoundError("Step 6 lock, adapter manifest, or protocol file is missing")
    lock_sha, protocol_sha = sha256_file(lock_path), sha256_file(protocol_path)
    lock = read_json(lock_path)
    if lock["protocol"]["protocol_sha256"] != protocol_sha:
        raise ValueError("The preregistered protocol hash changed; stop before analysis")
    adapter = read_json(adapter_path)
    if adapter.get("lock_sha256") != lock_sha:
        raise ValueError("CodeT5 adapter does not belong to current Step 6 lock")
    h3b_root = step6_root / "runs" / "h3b_locked" / f"step6_lock_{lock_sha[:12]}"
    if not (h3b_root / "campaign_manifest.json").is_file():
        raise FileNotFoundError(f"Locked H3-B export campaign missing: {h3b_root}")
    stats = _load_grace_stats(summary_root)

    inputs, joins, X_by_dataset = {}, {}, {}
    for dataset in DATASETS:
        joined = {}
        X_by_dataset[dataset] = {}
        for split in SPLITS:
            joined[split], X_by_dataset[dataset][split], info = _join_split(
                step6_root, summary_root, lock, lock_sha, b2_root, h3b_root, dataset, split)
            inputs[f"{dataset}/{split}"] = info
            if len(joined[split]) != len({r["id"] for r in joined[split]}):
                raise ValueError(f"Duplicate ID after join: {dataset}/{split}")
        joins[dataset] = joined
        print(f"Join PASS: {dataset}: validation={len(joined['validation'])}, test={len(joined['test'])}",
              flush=True)

    script_sha = sha256_file(Path(__file__).resolve())
    run_key = fingerprint({"lock_sha256": lock_sha, "protocol_sha256": protocol_sha,
                           "script_sha256": script_sha,
                           "b2_root": str(b2_root), "inputs": inputs,
                           "analysis": {"seed": SEED, "folds": N_FOLDS,
                                        "n_boot": N_BOOT, "bootstrap_seed": BOOTSTRAP_SEED,
                                        "budgets": BUDGETS}})
    out_dir = step6_root / "runs" / "complementarity_step6" / f"step6_lock_{lock_sha[:12]}_{run_key[:8]}"
    out_dir.mkdir(parents=True, exist_ok=True)

    results, join_files = {}, {}
    for dataset in DATASETS:
        val, test = joins[dataset]["validation"], joins[dataset]["test"]
        Xv, Xt = X_by_dataset[dataset]["validation"], X_by_dataset[dataset]["test"]
        yv = np.asarray([r["y"] for r in val], dtype=int)
        yt = np.asarray([r["y"] for r in test], dtype=int)
        pgv = np.asarray([r["p_gate"] for r in val], dtype=float)
        pgt = np.asarray([r["p_gate"] for r in test], dtype=float)
        sv = np.asarray([r["s_llm"] for r in val], dtype=float)
        st = np.asarray([r["s_llm"] for r in test], dtype=float)
        vv = np.asarray([r["valid"] for r in val], dtype=bool)
        vt = np.asarray([r["valid"] for r in test], dtype=bool)
        gv = np.asarray([r["group"] for r in val])
        gt = np.asarray([r["group"] for r in test])
        supv = np.asarray([r["s_sup_lr"] for r in val], dtype=float)
        supt = np.asarray([r["s_sup_lr"] for r in test], dtype=float)
        tau_gate = inputs[f"{dataset}/validation"]["h3b"]["tau_gate_train_oof"]
        tau_sup = inputs[f"{dataset}/validation"]["tau_sup_lr_validation"]

        meta = _fit_paired_meta(stats, Xv, yv, sv, vv, pgv, gv,
                                Xt, yt, st, vt, pgt, gt)
        gate_analysis = _repair_and_route(stats, val, Xv, test, Xt,
                                          "H3B_GATE", tau_gate, primary=True)
        sup_analysis = _repair_and_route(stats, val, Xv, test, Xt,
                                         "SUP-LR", tau_sup, primary=False)
        results[dataset] = {
            "n_validation": len(val), "n_test": len(test),
            "group_unit": inputs[f"{dataset}/validation"]["locked_split"]["group_unit"],
            "gate_tau_train_oof": tau_gate, "sup_lr_tau_validation": tau_sup,
            "p_pre_vs_p_post": meta,
            "h3b_gate_vs_b2": gate_analysis,
            "sup_lr_vs_b2": sup_analysis,
            "b2_valid_n_test": int(vt.sum()),
            "b2_invalid_n_test": int((~vt).sum()),
        }
        join_files[f"{dataset}/validation"] = _write_join(out_dir / dataset, "validation", val)
        join_files[f"{dataset}/test"] = _write_join(out_dir / dataset, "test", test)
        write_json(out_dir / dataset / "complementarity_step6.json", results[dataset])
        print(f"Analysis complete: {dataset}", flush=True)

    output_hashes = {}
    for path in sorted(out_dir.rglob("*")):
        if path.is_file() and path.name != "analysis_manifest.json":
            output_hashes[path.relative_to(out_dir).as_posix()] = sha256_file(path)
    manifest = {
        "schema": "step6_complementarity_analysis_v1",
        "run_fingerprint": run_key,
        "step6_lock_sha256": lock_sha,
        "protocol_sha256": protocol_sha,
        "adapter_manifest_sha256": sha256_file(adapter_path),
        "h3b_export_root": h3b_root.relative_to(step6_root).as_posix(),
        "b2_source_root": b2_root.relative_to(summary_root).as_posix(),
        "b2_selection": "registered main B2, seed 42; continuous s and valid; no rerun/inference",
        "group_units": {"devign": "commit_id", "reveal": "file_hash (locked code_sha256)"},
        "analysis_config": {"seed": SEED, "folds": N_FOLDS,
                            "n_boot": N_BOOT, "bootstrap_seed": BOOTSTRAP_SEED,
                            "delta_mcc_meta": DELTA_MCC_META,
                            "budgets": list(BUDGETS),
                            "random_router_seeds": RANDOM_ROUTER_SEEDS,
                            "h5_3": {"q": 0.10,
                                     "benefit_vs_confidence_metrics": ["balanced_accuracy", "mcc"],
                                     "benefit_vs_random_metric": "balanced_accuracy",
                                     "benefit_vs_random_upper_ci_margin": 0.01,
                                     "benefit_vs_confidence_upper_ci_margin": 0.02,
                                     "random_expert_reference_seeds": 20,
                                     "random_expert_repair_limit": "97.5th percentile"},
                            "ridge_alpha": RIDGE_ALPHA, "logistic_C": LOGISTIC_C,
                            "test_labels_used_for_fit_or_threshold_selection": False},
        "inputs": inputs,
        "join_outputs": join_files,
        "result_outputs": {f"{ds}/complementarity_step6.json":
                            sha256_file(out_dir / ds / "complementarity_step6.json")
                            for ds in DATASETS},
        "output_hashes": output_hashes,
        "runtime_versions": {name: importlib.metadata.version(name)
                             for name in ("numpy", "scipy", "scikit-learn")},
        "analysis_script_sha256": script_sha,
    }
    write_json(out_dir / "analysis_manifest.json", manifest)
    print(f"Wrote Step 6 analysis to {out_dir}", flush=True)
    return out_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Join locked B2/H3-B/SUP-LR results and run Step 6 offline analyses")
    parser.add_argument("--step6-root", type=Path, required=True)
    parser.add_argument("--summary-root", type=Path, required=True)
    parser.add_argument("--b2-root", type=Path, required=True)
    args = parser.parse_args()
    run_analysis(args.step6_root, args.summary_root, args.b2_root)


if __name__ == "__main__":
    main()
