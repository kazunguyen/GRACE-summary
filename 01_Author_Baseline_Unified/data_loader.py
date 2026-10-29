"""
GRACE Unified Data Loader Module
Loads vulnerability datasets (Devign, Reveal, BigVul) from local JSON/JSONL,
Hugging Face Hub, or built-in Mock dataset for instant local testing.
Standardizes schema and prepares the contract candidate pool (top 50 from train).
"""

from __future__ import annotations

import gzip
import json
import logging
import random
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


def standardize_sample(raw_item: Dict[str, Any], idx: int, dataset_name: str = "dataset") -> Dict[str, Any]:
    """Standardizes heterogeneous data rows into a canonical dictionary format."""
    code = (
        raw_item.get("func") or
        raw_item.get("function") or
        raw_item.get("code") or
        raw_item.get("processed_func") or ""
    )

    raw_target = raw_item.get("target", raw_item.get("label", raw_item.get("sealed_label", 0)))
    try:
        target = int(raw_target)
    except (ValueError, TypeError):
        target = 0

    raw_id = raw_item.get("record_id", raw_item.get("id", raw_item.get("idx")))
    if raw_id is not None and str(raw_id).strip():
        sample_id = str(raw_id)
    else:
        sample_id = f"{dataset_name}_{idx}"

    nodes = raw_item.get("nodes", raw_item.get("node", []))
    edges = raw_item.get("edges", raw_item.get("edge", []))

    return {
        "id": sample_id,
        "func": str(code).strip(),
        "target": target,
        "nodes": nodes if isinstance(nodes, list) else [],
        "edges": edges if isinstance(edges, list) else [],
    }


def generate_mock_dataset(num_samples: int = 50, prefix: str = "mock") -> List[Dict[str, Any]]:
    """Generates synthetic C code samples with CPG nodes and edges for immediate offline testing."""
    samples = []
    for i in range(num_samples):
        is_vuln = 1 if i % 2 == 0 else 0
        if is_vuln:
            func = (
                f"int process_buffer_{i}(char *input, int len) {{\n"
                f"    char buf[128];\n"
                f"    if (len > 0) {{\n"
                f"        strcpy(buf, input); /* Vulnerability: unsafe buffer copy */\n"
                f"    }}\n"
                f"    return 0;\n"
                f"}}"
            )
            nodes = [
                {"id": 1, "type": "METHOD", "code": f"process_buffer_{i}"},
                {"id": 2, "type": "PARAM", "code": "char *input"},
                {"id": 3, "type": "BLOCK", "code": "{"},
                {"id": 4, "type": "CALL", "code": "strcpy(buf, input)"},
            ]
            edges = [
                {"src": 1, "dst": 2, "type": "AST"},
                {"src": 1, "dst": 3, "type": "AST"},
                {"src": 3, "dst": 4, "type": "CFG"},
            ]
        else:
            func = (
                f"int process_buffer_{i}(char *input, int len) {{\n"
                f"    char buf[128];\n"
                f"    if (len > 0 && len < sizeof(buf)) {{\n"
                f"        strncpy(buf, input, sizeof(buf) - 1);\n"
                f"        buf[sizeof(buf) - 1] = '\\0';\n"
                f"    }}\n"
                f"    return 0;\n"
                f"}}"
            )
            nodes = [
                {"id": 1, "type": "METHOD", "code": f"process_buffer_{i}"},
                {"id": 2, "type": "PARAM", "code": "char *input"},
                {"id": 3, "type": "BLOCK", "code": "{"},
                {"id": 4, "type": "CALL", "code": "strncpy(buf, input, sizeof(buf)-1)"},
            ]
            edges = [
                {"src": 1, "dst": 2, "type": "AST"},
                {"src": 1, "dst": 3, "type": "AST"},
                {"src": 3, "dst": 4, "type": "CFG"},
            ]

        samples.append({
            "id": f"{prefix}_{i}",
            "func": func,
            "target": is_vuln,
            "nodes": nodes,
            "edges": edges,
        })
    return samples


def slice_dataset_stratified(
    dataset: List[Dict[str, Any]],
    sample_ratio: float = 1.0,
    max_samples: Optional[int] = None,
    seed: int = 42,
) -> List[Dict[str, Any]]:
    """Performs stratified sampling preserving positive/negative ratio."""
    if sample_ratio >= 1.0 and max_samples is None:
        return dataset

    vulns = [s for s in dataset if s["target"] == 1]
    safes = [s for s in dataset if s["target"] == 0]

    rng = random.Random(seed)

    if max_samples is not None:
        target_count = min(max_samples, len(dataset))
        vuln_prop = len(vulns) / len(dataset) if dataset else 0.5
        n_vuln = int(target_count * vuln_prop)
        n_safe = target_count - n_vuln
    else:
        n_vuln = max(1, int(len(vulns) * sample_ratio)) if vulns else 0
        n_safe = max(1, int(len(safes) * sample_ratio)) if safes else 0

    sampled_v = rng.sample(vulns, min(n_vuln, len(vulns)))
    sampled_s = rng.sample(safes, min(n_safe, len(safes)))

    result = sampled_v + sampled_s
    rng.shuffle(result)
    return result


def load_dataset(
    dataset_name: str = "devign",
    split: str = "test",
    sample_ratio: float = 1.0,
    max_samples: Optional[int] = None,
    seed: int = 42,
    use_mock: bool = False,
) -> List[Dict[str, Any]]:
    """Loads and standardizes dataset split."""
    if use_mock or dataset_name.lower() == "mock":
        count = max_samples or (20 if split == "test" else 50)
        return generate_mock_dataset(num_samples=count, prefix=f"mock_{split}")

    # Check local JSON/JSONL/GZ search locations
    ds_capitalized = "Devign" if dataset_name.lower() == "devign" else ("Reveal" if dataset_name.lower() == "reveal" else dataset_name)
    possible_paths = [
        Path(f"data/{dataset_name}_{split}_processed.json"),
        Path(f"data/{dataset_name}_{split}.json"),
        Path(f"data/{dataset_name}_{split}.jsonl"),
        Path(f"D:/JUNIOR/LabThayTho/HuuHieu03/GRACE/data/processed/{dataset_name}_{split}_compact_cpg.json.gz"),
        Path(f"C:/MY-FILES/LAB-THAY-THO/Graduation-Project/Ablation_V2/{ds_capitalized}/Code-CPG/{dataset_name}_{split}_cpg.jsonl"),
    ]

    raw_items = None
    for p in possible_paths:
        if p.is_file():
            logger.info("Found local dataset file: %s", p)
            try:
                if p.suffix == ".gz":
                    with gzip.open(p, "rt", encoding="utf-8") as f:
                        raw_items = json.load(f)
                elif p.suffix == ".jsonl":
                    with p.open("r", encoding="utf-8") as f:
                        raw_items = [json.loads(line) for line in f if line.strip()]
                else:
                    with p.open("r", encoding="utf-8") as f:
                        raw_items = json.load(f)
                break
            except Exception as e:
                logger.warning("Error reading local dataset %s: %s", p, e)

    # Fallback to Hugging Face if no local file found
    if raw_items is None:
        hf_map = {
            "devign": "DetectVul/devign",
            "reveal": "claudios/ReVeal",
            "bigvul": "bstee615/bigvul",
        }
        hf_id = hf_map.get(dataset_name.lower(), dataset_name)
        logger.info("Loading '%s' (split='%s') from Hugging Face Hub...", hf_id, split)
        try:
            from datasets import load_dataset as hf_load_dataset
            ds = hf_load_dataset(hf_id, split=split)
            raw_items = list(ds)
        except Exception as e:
            logger.warning("Failed to load from Hugging Face (%s). Falling back to synthetic mock data.", e)
            return generate_mock_dataset(num_samples=max_samples or 30, prefix=f"{dataset_name}_{split}")

    standardized = [standardize_sample(item, i, dataset_name) for i, item in enumerate(raw_items)]
    return slice_dataset_stratified(standardized, sample_ratio=sample_ratio, max_samples=max_samples, seed=seed)
