from __future__ import annotations

import argparse
import csv
import hashlib
import importlib
import json
import os
import sys
from pathlib import Path
from typing import Any

import joblib
import numpy as np


DATASETS = ("devign", "reveal")
SPLITS = ("train", "validation", "test")
SEED = 42


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def fingerprint(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True,
                     separators=(",", ":")).encode("utf-8")
    return sha256_bytes(raw)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True,
                               indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temp, path)


def row_identity(rows: list[dict[str, Any]]) -> str:
    pairs = [(row["record_id"], row["code_sha256"]) for row in rows]
    return fingerprint(pairs)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSONL at {path}:{line_number}") from exc
    return rows


def _load_h3b_source(h3b_root: Path):
    h3b_root = h3b_root.resolve()
    if not (h3b_root / "grace_h3v2" / "features.py").is_file():
        raise FileNotFoundError(f"H3-B source not found at {h3b_root}")
    sys.path.insert(0, str(h3b_root))
    common = importlib.import_module("grace_h3v2.common")
    features = importlib.import_module("grace_h3v2.features")
    meta = importlib.import_module("grace_h3v2.meta")
    for module in (common, features, meta):
        if not Path(module.__file__).resolve().is_relative_to(h3b_root):
            raise RuntimeError(f"Imported H3-B module outside requested source: {module.__file__}")
    return common, features, meta


def _source_hashes(h3b_root: Path) -> dict[str, str]:
    files: list[Path] = []
    for package in ("grace_h1", "grace_h3v2"):
        files.extend(sorted((h3b_root / package).glob("*.py")))
    files.append(h3b_root / "configs" / "benchmark_v2.json")
    return {path.relative_to(h3b_root).as_posix(): sha256_file(path)
            for path in files if path.is_file()}


def _load_locked_rows(summary_root: Path, lock: dict[str, Any],
                      dataset: str, split: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    entry = lock["frozen_data"]["datasets"][dataset]
    raw_spec = entry["raw"][split]
    raw_path = summary_root / raw_spec["path"]
    if not raw_path.is_file() or sha256_file(raw_path) != raw_spec["sha256"]:
        raise ValueError(f"Locked raw input missing or hash mismatch: {raw_path}")

    rows = []
    for raw in read_jsonl(raw_path):
        if raw.get("dataset") != dataset or raw.get("split") != split:
            raise ValueError(f"Dataset/split tag mismatch in {raw_path}")
        if "id" not in raw or "func" not in raw or "target" not in raw:
            raise ValueError(f"Expected id/func/target fields in {raw_path}")
        try:
            label = int(raw["target"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Non-binary label in {raw_path}: {raw.get('id')}") from exc
        if label not in (0, 1):
            raise ValueError(f"Non-binary label in {raw_path}: {raw.get('id')}")
        code = raw["func"]
        code_hash = sha256_bytes(code.encode("utf-8"))
        rows.append({
            "record_id": str(raw["id"]),
            "dataset": dataset,
            "split": split,
            "code": code,
            "code_sha256": code_hash,
            "label": label,
            "project": raw.get("project"),
            "commit": raw.get("commit_id"),
        })

    if not rows or len({row["record_id"] for row in rows}) != len(rows):
        raise ValueError(f"Empty split or duplicate IDs: {raw_path}")

    manifest_spec = entry["manifests"][split]
    manifest_path = summary_root / manifest_spec["path"]
    if not manifest_path.is_file() or sha256_file(manifest_path) != manifest_spec["sha256"]:
        raise ValueError(f"Locked row manifest missing or hash mismatch: {manifest_path}")
    manifest_rows = read_jsonl(manifest_path)
    if len(rows) != len(manifest_rows):
        raise ValueError(f"Locked raw/manifest row count differs: {dataset}/{split}")
    for row, frozen in zip(rows, manifest_rows):
        if row["record_id"] != frozen["id"] or row["code_sha256"] != frozen["code_sha256"]:
            raise ValueError(f"Locked raw/manifest ID or code hash differs: {dataset}/{split}/{row['record_id']}")
        if row["label"] != int(frozen["label"]):
            raise ValueError(f"Locked raw/manifest label differs: {dataset}/{split}/{row['record_id']}")

    return rows, {"path": raw_spec["path"], "sha256": raw_spec["sha256"],
                  "count": len(rows), "row_identity": row_identity(rows),
                  "manifest_path": manifest_spec["path"],
                  "manifest_sha256": manifest_spec["sha256"]}


def _load_embeddings(step6_root: Path, dataset: str, split: str,
                     rows: list[dict[str, Any]], adapter: dict[str, Any]) -> tuple[np.ndarray, dict[str, Any]]:
    npz_path = step6_root / "cache" / "anchor_npz" / dataset / f"{split}.npz"
    expected = next((item for item in adapter["exports"]
                     if item["dataset"] == dataset and item["split"] == split), None)
    if expected is None:
        raise ValueError(f"No locked CodeT5 export in adapter manifest: {dataset}/{split}")
    if not npz_path.is_file() or sha256_file(npz_path) != expected["npz_sha256"]:
        raise ValueError(f"Locked CodeT5 NPZ missing or hash mismatch: {npz_path}")
    with np.load(npz_path, allow_pickle=False) as archive:
        if set(archive.files) != {"ids", "X"}:
            raise ValueError(f"Unexpected NPZ schema: {npz_path}")
        ids = archive["ids"].astype(str)
        x = np.asarray(archive["X"], dtype=np.float32)
    row_ids = np.asarray([row["record_id"] for row in rows], dtype=str)
    if not np.array_equal(ids, row_ids):
        raise ValueError(f"CodeT5 IDs/order do not match the locked {dataset}/{split} split")
    if x.shape != (len(rows), 768) or not np.isfinite(x).all():
        raise ValueError(f"Invalid CodeT5 matrix shape/content: {npz_path}: {x.shape}")
    return x, {"path": str(npz_path.relative_to(step6_root).as_posix()),
               "sha256": expected["npz_sha256"], "rows": len(rows),
               "shape": list(x.shape), "ids_match_locked_split": True}


def _verify_donor_banks(summary_root: Path, lock: dict[str, Any]) -> dict[str, Any]:
    result = {}
    for dataset in DATASETS:
        donor = lock["frozen_data"]["datasets"][dataset]["frozen_donor_bank"]
        path = summary_root / donor["path"]
        if not path.is_file() or sha256_file(path) != donor["sha256"]:
            raise ValueError(f"Frozen donor bank missing or hash mismatch: {path}")
        result[dataset] = {"path": donor["path"], "sha256": donor["sha256"],
                           "count": donor["count"],
                           "role": "LLM demonstration retrieval only; not used to fit H3-B gate"}
    return result


def _preflight_inputs(step6_root: Path, summary_root: Path, lock: dict[str, Any],
                     adapter: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Validate every locked split before spending time fitting either dataset."""
    result = {}
    for dataset in DATASETS:
        rows_by_split, data_by_split, embeddings_by_split = {}, {}, {}
        for split in SPLITS:
            rows_by_split[split], data_by_split[split] = _load_locked_rows(
                summary_root, lock, dataset, split)
            embeddings_by_split[split], data_by_split[split]["codet5"] = _load_embeddings(
                step6_root, dataset, split, rows_by_split[split], adapter)
        result[dataset] = {"rows": rows_by_split, "data": data_by_split,
                           "embeddings": embeddings_by_split}
        print(f"Preflight PASS: {dataset} frozen raw/manifests, IDs and CodeT5 NPZ",
              flush=True)
    return result


def _fit_view_cached(cache_dir: Path, run_key: str, dataset: str, name: str,
                     seed: int, rows: list[dict[str, Any]], x: np.ndarray,
                     y: np.ndarray, cfg: dict[str, Any], View) -> Any:
    key = fingerprint({
        "run_key": run_key, "dataset": dataset, "view": name, "seed": seed,
        "rows": row_identity(rows), "labels": y.tolist(),
        "embedding_shape": list(x.shape), "embedding_dtype": str(x.dtype),
    })
    model_path = cache_dir / "fit_models" / dataset / f"{key[:24]}.joblib"
    manifest_path = model_path.with_suffix(".json")
    if model_path.is_file() and manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("fingerprint") != key or manifest.get("sha256") != sha256_file(model_path):
            raise ValueError(f"H3-B fit cache checksum/fingerprint mismatch: {model_path}")
        print(f"{dataset}: reuse {name} fit cache ({len(rows)} rows, seed={seed})", flush=True)
        return joblib.load(model_path)

    model_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"{dataset}: fit {name} ({len(rows)} rows, seed={seed})", flush=True)
    model = View(name, cfg, seed).fit(rows, x, y)
    temp = model_path.with_name(model_path.name + ".tmp")
    joblib.dump(model, temp, compress=3)
    os.replace(temp, model_path)
    write_json(manifest_path, {"schema": "step6_h3b_view_fit_cache_v1",
                               "fingerprint": key, "sha256": sha256_file(model_path),
                               "dataset": dataset, "view": name, "seed": seed,
                               "rows": len(rows), "row_identity": row_identity(rows)})
    return model


def _score_views(cache_dir: Path, run_key: str, dataset: str, seed: int,
                 train_rows: list[dict[str, Any]], train_x: np.ndarray, train_y: np.ndarray,
                 query_rows: list[dict[str, Any]], query_x: np.ndarray,
                 cfg: dict[str, Any], View, view_names: tuple[str, ...]) -> np.ndarray:
    scores = np.empty((len(query_rows), len(view_names)), dtype=np.float64)
    for column, name in enumerate(view_names):
        model = _fit_view_cached(cache_dir, run_key, dataset, name, seed,
                                 train_rows, train_x, train_y, cfg, View)
        scores[:, column] = model.score(query_rows, query_x)
    if not np.isfinite(scores).all():
        raise FloatingPointError(f"Non-finite base view scores for {dataset}")
    return scores


def _save_fold_checkpoint(path: Path, key: str, held: np.ndarray,
                          view_scores: np.ndarray, arm_scores: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.stem + ".tmp.npz")
    np.savez_compressed(temp, held=held, view_scores=view_scores, arm_scores=arm_scores)
    os.replace(temp, path)
    write_json(path.with_suffix(".json"), {"fingerprint": key, "sha256": sha256_file(path)})


def _load_or_fit_outer_fold(path: Path, key: str, fold_index: int,
                            rows, x, y, cfg, seed, dataset, cache_dir,
                            View, folds, view_names, arm_names, fusion_input,
                            fusion_model):
    manifest_path = path.with_suffix(".json")
    if path.is_file() and manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("fingerprint") == key and manifest.get("sha256") == sha256_file(path):
            with np.load(path, allow_pickle=False) as archive:
                return archive["held"], archive["view_scores"], archive["arm_scores"]

    outer_splits = folds(rows, y, cfg["folds"], seed, cfg["group_key"])
    fit_indices, held_indices = outer_splits[fold_index]
    fit_rows = [rows[i] for i in fit_indices]
    held_rows = [rows[i] for i in held_indices]
    held_views = _score_views(cache_dir, key, dataset, seed + fold_index * 1009,
                              fit_rows, x[fit_indices], y[fit_indices], held_rows,
                              x[held_indices], cfg, View, view_names)

    inner_scores = np.empty((len(fit_indices), len(view_names)), dtype=np.float64)
    inner_splits = folds(fit_rows, y[fit_indices], cfg["inner_folds"],
                         seed + 30001 + fold_index * 1009, cfg["group_key"])
    for inner_index, (inner_fit, inner_held) in enumerate(inner_splits):
        inner_train_rows = [fit_rows[i] for i in inner_fit]
        inner_held_rows = [fit_rows[i] for i in inner_held]
        inner_scores[inner_held] = _score_views(
            cache_dir, key, dataset,
            seed + 30001 + fold_index * 1009 + inner_index * 1009,
            inner_train_rows, x[fit_indices][inner_fit], y[fit_indices][inner_fit],
            inner_held_rows, x[fit_indices][inner_held], cfg, View, view_names)

    arms = np.empty((len(held_indices), len(arm_names)), dtype=np.float64)
    for column, arm in enumerate(arm_names):
        if arm in view_names:
            arms[:, column] = held_views[:, view_names.index(arm)]
        else:
            fusion = fusion_model()
            fusion.fit(fusion_input(inner_scores, arm), y[fit_indices])
            arms[:, column] = fusion.predict_proba(fusion_input(held_views, arm))[:, 1]
    _save_fold_checkpoint(path, key, held_indices, held_views, arms)
    return held_indices, held_views, arms


def _export_dataset(step6_root: Path, output_root: Path, lock_sha: str,
                    adapter_sha: str, h3b_root: Path, source_hashes: dict[str, str],
                    runtime_versions: dict[str, str], donor_banks: dict[str, Any],
                    preflight: dict[str, Any], dataset: str,
                    cfg: dict[str, Any], common, features, meta) -> dict[str, Any]:
    View, VIEWS, ARMS = features.View, features.VIEWS, features.ARMS
    folds, metrics, best_threshold, choose, eligible = (
        common.folds, common.metrics, common.best_threshold, common.choose, common.eligible)
    pre_features = meta.pre_features

    split_rows = preflight["rows"]
    split_data = preflight["data"]
    split_embeddings = preflight["embeddings"]

    train_all = split_rows["train"]
    train_x_all = split_embeddings["train"]
    train_idx = eligible(train_all)
    if not len(train_idx):
        raise ValueError(f"H3-B eligibility filtering removed all train rows for {dataset}")
    train_rows = [train_all[i] for i in train_idx]
    train_x = np.asarray(train_x_all[train_idx], dtype=np.float32)
    train_y = np.asarray([row["label"] for row in train_rows], dtype=np.int64)
    if len(np.unique(train_y)) != 2:
        raise ValueError(f"Eligible train rows lack one class: {dataset}")

    run_spec = {
        "schema": "step6_locked_h3b_export_run_v1", "dataset": dataset, "seed": SEED,
        "step6_lock_sha256": lock_sha, "adapter_manifest_sha256": adapter_sha,
        "raw_splits": {split: {k: v for k, v in split_data[split].items()
                               if k != "codet5"} for split in SPLITS},
        "codet5_npz_sha256": {split: split_data[split]["codet5"]["sha256"]
                               for split in SPLITS},
        "h3b_source_hashes": source_hashes, "h3b_config": cfg,
        "runtime_versions": runtime_versions,
        "eligible_train_identity": row_identity(train_rows),
        "eligible_train_count": len(train_rows),
    }
    run_key = fingerprint(run_spec)
    cache_dir = output_root / "cache"
    fold_dir = cache_dir / "outer_folds" / dataset / run_key[:20]
    y = train_y
    base_oof = np.empty((len(train_rows), len(VIEWS)), dtype=np.float64)
    outer_scores = np.empty((len(train_rows), len(ARMS)), dtype=np.float64)

    for fold_index in range(cfg["folds"]):
        fold_key = fingerprint({"run_key": run_key, "fold": fold_index,
                                "folds": cfg["folds"], "group_key": cfg["group_key"]})
        path = fold_dir / f"fold_{fold_index}.npz"
        held, view_values, arm_values = _load_or_fit_outer_fold(
            path, fold_key, fold_index, train_rows, train_x, y, cfg, SEED, dataset,
            cache_dir, View, folds, VIEWS, ARMS, features.fusion_input,
            features.fusion_model)
        base_oof[held] = view_values
        outer_scores[held] = arm_values
        print(f"{dataset}: completed H3-B outer fold {fold_index + 1}/{cfg['folds']}", flush=True)

    candidates = []
    for column, arm in enumerate(ARMS):
        selected = best_threshold(y, outer_scores[:, column], cfg, arm)
        candidates.append({"name": arm, "threshold": float(selected["threshold"]),
                           "metrics": selected["metrics"], "cost_rank": column})
    winner = choose(candidates, cfg)

    # Match the H3-B source recipe: refit the five base views on eligible official train,
    # and fit fusion views only on the outer-fold OOF train scores.
    final_val_scores = _score_views(
        cache_dir, run_key, dataset, SEED, train_rows, train_x, y,
        split_rows["validation"], split_embeddings["validation"], cfg, View, VIEWS)
    final_test_scores = _score_views(
        cache_dir, run_key, dataset, SEED, train_rows, train_x, y,
        split_rows["test"], split_embeddings["test"], cfg, View, VIEWS)
    final_models = {}
    for arm in ARMS:
        if arm not in VIEWS:
            model = features.fusion_model()
            model.fit(features.fusion_input(base_oof, arm), y)
            final_models[arm] = model

    def arm_probabilities(view_scores):
        result = {}
        for arm in ARMS:
            if arm in VIEWS:
                result[arm] = view_scores[:, VIEWS.index(arm)]
            else:
                result[arm] = final_models[arm].predict_proba(
                    features.fusion_input(view_scores, arm))[:, 1]
        return result

    gate_name = winner["name"]
    tau = float(winner["threshold"])
    scored = {
        "validation": (final_val_scores, arm_probabilities(final_val_scores)),
        "test": (final_test_scores, arm_probabilities(final_test_scores)),
    }
    feature_names = ([f"logit_{name}" for name in VIEWS]
                     + ["p_gate", "abs_p_gate_minus_half", "abs_semantic_mlp_minus_lexical"]
                     + list(features.NUMERIC_NAMES))
    if len(feature_names) != 34:
        raise ValueError(f"Expected 34 H3-B pre-feature names, got {len(feature_names)}")

    dataset_out = output_root / dataset
    dataset_out.mkdir(parents=True, exist_ok=True)
    exports = {}
    for split in ("validation", "test"):
        view_scores, probabilities = scored[split]
        p_gate = np.asarray(probabilities[gate_name], dtype=np.float64)
        Xpre = np.asarray(pre_features(split_rows[split], view_scores, p_gate), dtype=np.float32)
        ids = np.asarray([row["record_id"] for row in split_rows[split]], dtype=str)
        labels = np.asarray([row["label"] for row in split_rows[split]], dtype=np.int64)
        if Xpre.shape != (len(ids), 34) or not np.isfinite(Xpre).all():
            raise ValueError(f"Invalid xpre output for {dataset}/{split}: {Xpre.shape}")
        if p_gate.shape != labels.shape or not np.isfinite(p_gate).all():
            raise ValueError(f"Invalid gate score output for {dataset}/{split}")

        xpre_path = dataset_out / f"xpre_{split}.npz"
        temp_npz = xpre_path.with_name(xpre_path.stem + ".tmp.npz")
        np.savez_compressed(temp_npz, X=Xpre, ids=ids,
                            feature_names=np.asarray(feature_names, dtype=str))
        os.replace(temp_npz, xpre_path)
        gate_path = dataset_out / f"gate_{split}.csv"
        with gate_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["id", "y", "p_gate"])
            writer.writerows((rid, int(label), format(float(prob), ".17g"))
                             for rid, label, prob in zip(ids, labels, p_gate))

        exports[split] = {
            "xpre": {"path": xpre_path.relative_to(output_root).as_posix(),
                     "sha256": sha256_file(xpre_path), "shape": list(Xpre.shape),
                     "ids_match_locked_split": bool(np.array_equal(ids,
                         np.asarray([row["record_id"] for row in split_rows[split]], dtype=str))),
                     "feature_names": feature_names},
            "gate": {"path": gate_path.relative_to(output_root).as_posix(),
                     "sha256": sha256_file(gate_path), "rows": len(ids),
                     "columns": ["id", "y", "p_gate"],
                     "labels_used_for_feature_generation": False},
            "split_identity": split_data[split]["row_identity"],
        }

    manifest = {
        "schema": "step6_locked_h3b_feature_export_v1",
        "dataset": dataset,
        "seed": SEED,
        "step6_lock_sha256": lock_sha,
        "adapter_manifest_sha256": adapter_sha,
        "h3b_source_root": str(h3b_root),
        "h3b_source_hashes": source_hashes,
        "runtime_versions": runtime_versions,
        "h3b_config": cfg,
        "h3b_source_algorithm": {
            "base_views": list(VIEWS), "candidate_arms": list(ARMS),
            "pre_feature_function": "grace_h3v2.meta.pre_features",
            "selection": "H3-B source nested train OOF; MCC then F1 then cost; threshold selected on train OOF",
            "eligible_train_count": len(train_rows),
            "full_train_count": len(train_all),
            "eligible_train_identity": row_identity(train_rows),
            "group_key": cfg["group_key"],
            "winner": gate_name, "tau_train_oof": tau,
            "winner_metrics_train_oof": winner["metrics"],
            "candidates": candidates,
        },
        "input_splits": split_data,
        "donor_banks": donor_banks,
        "donor_use": "The frozen donor banks are recorded and verified but are not H3-B classifier fit data; H3-B uses the locked official train split. Donor banks remain for LLM demonstration retrieval.",
        "label_use": {"train": "used for fitting and train-OOF gate selection",
                       "validation": "written to gate CSV for evaluation only; not used for fitting or threshold selection",
                       "test": "written to gate CSV for evaluation only; not used for fitting or threshold selection"},
        "outputs": exports,
        "run_fingerprint": run_key,
        "run_spec": run_spec,
    }
    manifest_path = dataset_out / "h3b_export_manifest.json"
    write_json(manifest_path, manifest)
    print(f"{dataset}: exported {gate_name} (tau={tau:.4f}) to {dataset_out}", flush=True)
    return manifest


def run_locked_export(step6_root: Path, h3b_root: Path) -> list[dict[str, Any]]:
    step6_root = step6_root.resolve()
    summary_root = step6_root.parent
    lock_path = step6_root / "step6_lock.json"
    adapter_path = step6_root / "cache" / "anchor_npz" / "adapter_manifest.json"
    if not lock_path.is_file() or not adapter_path.is_file():
        raise FileNotFoundError("Step 6 lock or CodeT5 adapter manifest is missing")
    lock_sha, adapter_sha = sha256_file(lock_path), sha256_file(adapter_path)
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    adapter = json.loads(adapter_path.read_text(encoding="utf-8"))
    if adapter.get("lock_sha256") != lock_sha:
        raise ValueError("CodeT5 adapter was exported against a different Step 6 lock")
    if adapter.get("encoder_rerun") is not False:
        raise ValueError("Expected use of the already locked CodeT5 cache, without re-encoding")

    common, features, meta = _load_h3b_source(h3b_root)
    h3b_root = h3b_root.resolve()
    runtime_versions = common.versions()
    cfg_path = h3b_root / "configs" / "benchmark_v2.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    if cfg["seeds"] != [SEED] or cfg["group_key"] != "code_sha256":
        raise ValueError("H3-B benchmark_v2 config differs from the source run being reproduced")
    if cfg["selection"]["primary"] != "mcc" or cfg["selection"]["secondary"] != "f1":
        raise ValueError("H3-B winner selection config differs from the registered source recipe")
    source_hashes = _source_hashes(h3b_root)
    donor_banks = _verify_donor_banks(summary_root, lock)
    preflight = _preflight_inputs(step6_root, summary_root, lock, adapter)
    output_root = step6_root / "runs" / "h3b_locked" / f"step6_lock_{lock_sha[:12]}"
    output_root.mkdir(parents=True, exist_ok=True)
    run_manifest = {
        "schema": "step6_locked_h3b_export_campaign_v1",
        "step6_lock_sha256": lock_sha,
        "adapter_manifest_sha256": adapter_sha,
        "h3b_source_root": str(h3b_root),
        "h3b_source_hashes": source_hashes,
        "runtime_versions": runtime_versions,
        "datasets": list(DATASETS), "seed": SEED,
        "output_root": output_root.relative_to(step6_root).as_posix(),
    }
    campaign_path = output_root / "campaign_manifest.json"
    if campaign_path.exists():
        previous = json.loads(campaign_path.read_text(encoding="utf-8"))
        if previous != run_manifest:
            raise ValueError("Existing H3-B export folder has a different lock/source fingerprint")
    else:
        write_json(campaign_path, run_manifest)

    results = []
    for dataset in DATASETS:
        results.append(_export_dataset(step6_root, output_root, lock_sha, adapter_sha,
                                       h3b_root,
                                       source_hashes, runtime_versions, donor_banks,
                                       preflight[dataset], dataset, cfg,
                                       common, features, meta))
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Export locked H3-B features for Step 6")
    parser.add_argument("--step6-root", type=Path, required=True)
    parser.add_argument("--h3b-root", type=Path, required=True)
    args = parser.parse_args()
    results = run_locked_export(args.step6_root, args.h3b_root)
    for result in results:
        for split, files in result["outputs"].items():
            print(result["dataset"], split, files["xpre"]["path"], files["gate"]["path"])


if __name__ == "__main__":
    main()
