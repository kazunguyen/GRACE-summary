#!/usr/bin/env python3
"""Sanitize 15-arm specs (data/specs/*_15arms.jsonl) to ensure 100% clean donor bank alignment.
Eliminates all references to removed donors and synchronizes B2 demos and contrastive pairs
with the frozen clean donor bank.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "01_Author_Baseline_Unified/diagnostic_kit/src"))

from grace_diag.contrastive_pair_builder import build_contrastive_pair, load_donors_bank, identify_security_difference
from grace_diag.sink_evidence import build_evidence_text


def load_clean_bank_dict(bank_path: Path) -> Dict[str, Dict[str, Any]]:
    bank = {}
    with open(bank_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            uid = str(r.get("id") or r.get("function_uid")).strip()
            bank[uid] = {
                "function_uid": uid,
                "func": r["func"],
                "target": int(r["target"]),
            }
    return bank


def sanitize_split(
    specs_in_path: Path,
    specs_out_path: Path,
    dataset: str,
    split: str,
    clean_bank_dict: Dict[str, Dict[str, Any]],
    clean_donors_pack: Dict[str, Any],
    clean_b2_uids: List[str],
) -> Dict[str, int]:
    print(f"[{dataset}/{split}] Processing {specs_in_path} -> {specs_out_path}...")
    stats = {
        "total": 0,
        "b2_demo_updated": 0,
        "pair_regenerated": 0,
        "pair_kept": 0,
    }

    temp_out = specs_out_path.with_suffix(".tmp")
    with open(specs_in_path, "r", encoding="utf-8") as in_f, open(temp_out, "w", encoding="utf-8") as out_f:
        for idx, line in enumerate(in_f):
            if not line.strip():
                continue
            r = json.loads(line)
            stats["total"] += 1

            query_code = r["query_code"]
            qid = r["id"]
            canonical_id = f"reveal:{split}:{idx}" if dataset == "reveal" else qid
            label = int(r["label"])
            group = r.get("group")
            nodes = r.get("nodes") or []
            edges = r.get("edges") or []

            # 1. Clean B2 demo
            canonical_b2_uid = clean_b2_uids[idx]
            canonical_b2_demo = clean_bank_dict[canonical_b2_uid]

            current_demos = r.get("demonstrations") or []
            current_b2_uid = (current_demos[0].get("function_uid") or current_demos[0].get("id")) if current_demos else None

            if current_b2_uid != canonical_b2_uid:
                stats["b2_demo_updated"] += 1

            # 2. Contrastive pair
            current_pair = r.get("demonstrations_pair") or []
            current_sec_diff = r.get("security_difference")

            pair_valid = False
            if len(current_pair) == 2:
                p0_uid = current_pair[0].get("function_uid") or current_pair[0].get("id")
                p1_uid = current_pair[1].get("function_uid") or current_pair[1].get("id")
                # Pair is valid if both donors exist in clean bank, one of them is the canonical B2 demo, and labels are opposite
                if (p0_uid in clean_bank_dict and p1_uid in clean_bank_dict and
                    (p0_uid == canonical_b2_uid or p1_uid == canonical_b2_uid) and
                    int(current_pair[0]["target"]) != int(current_pair[1]["target"])):
                    pair_valid = True

            if pair_valid:
                # Ensure fields are clean
                pair = [
                    clean_bank_dict[current_pair[0].get("function_uid") or current_pair[0].get("id")],
                    clean_bank_dict[current_pair[1].get("function_uid") or current_pair[1].get("id")],
                ]
                sec_diff = current_sec_diff or identify_security_difference(pair[0]["func"], pair[1]["func"])
                stats["pair_kept"] += 1
            else:
                pair, sec_diff = build_contrastive_pair(query_code, canonical_b2_demo, clean_donors_pack)
                stats["pair_regenerated"] += 1

            # 3. Evidence H2
            h2_ev = r.get("h2_evidence")
            if not h2_ev:
                h2_ev = build_evidence_text(query_code)

            spec_row = {
                "id": canonical_id,
                "original_id": qid,
                "query_code": query_code,
                "nodes": nodes,
                "edges": edges,
                "demonstrations": [canonical_b2_demo],
                "demonstrations_pair": pair,
                "security_difference": sec_diff,
                "h2_evidence": h2_ev,
                "h2_source_limits": {"nodes": 40, "edges": 80},
                "label": label,
                "group": group,
            }
            out_f.write(json.dumps(spec_row, ensure_ascii=False) + "\n")

    # Replace original file with sanitized version
    temp_out.replace(specs_out_path)
    print(f"[{dataset}/{split}] Done: {stats}")
    return stats


def main():
    cache_dir = REPO_ROOT / "Runs-management" / "donor_reconciliation_20261101" / "cache"
    new_ref_dir = REPO_ROOT / "Runs-management" / "donor_reconciliation_20261101" / "new_reference" / "B2"
    specs_dir = REPO_ROOT / "data" / "specs"

    devign_bank_path = cache_dir / "devign_new_bank.jsonl"
    reveal_bank_path = cache_dir / "reveal_new_bank.jsonl"

    print("Loading clean banks...")
    devign_bank_dict = load_clean_bank_dict(devign_bank_path)
    reveal_bank_dict = load_clean_bank_dict(reveal_bank_path)
    devign_donors_pack = load_donors_bank(devign_bank_path)
    reveal_donors_pack = load_donors_bank(reveal_bank_path)
    print(f"Loaded Devign bank: {len(devign_bank_dict)} donors")
    print(f"Loaded ReVeal bank: {len(reveal_bank_dict)} donors")

    # Load canonical B2 retrieval UIDs
    with open(cache_dir / "devign_new_retrieval.json", "r", encoding="utf-8") as f:
        devign_retrieval = json.load(f)["selected_ids"]
    devign_val_b2_uids = devign_retrieval[:2732]
    devign_test_b2_uids = devign_retrieval[2732:5464]

    with open(new_ref_dir / "reveal" / "validation" / "prompts.jsonl", "r", encoding="utf-8") as f:
        reveal_val_b2_uids = [json.loads(l)["demo_ids"][0] for l in f]
    with open(new_ref_dir / "reveal" / "test" / "prompts.jsonl", "r", encoding="utf-8") as f:
        reveal_test_b2_uids = [json.loads(l)["demo_ids"][0] for l in f]

    targets = [
        ("devign", "validation", specs_dir / "devign_validation_15arms.jsonl", devign_bank_dict, devign_donors_pack, devign_val_b2_uids),
        ("devign", "test", specs_dir / "devign_test_15arms.jsonl", devign_bank_dict, devign_donors_pack, devign_test_b2_uids),
        ("reveal", "validation", specs_dir / "reveal_validation_15arms.jsonl", reveal_bank_dict, reveal_donors_pack, reveal_val_b2_uids),
        ("reveal", "test", specs_dir / "reveal_test_15arms.jsonl", reveal_bank_dict, reveal_donors_pack, reveal_test_b2_uids),
    ]

    all_stats = {}
    for dataset, split, specs_path, bank_dict, pack, b2_uids in targets:
        all_stats[f"{dataset}_{split}"] = sanitize_split(
            specs_in_path=specs_path,
            specs_out_path=specs_path,
            dataset=dataset,
            split=split,
            clean_bank_dict=bank_dict,
            clean_donors_pack=pack,
            clean_b2_uids=b2_uids,
        )

    print("\n--- FINAL AUDIT ACROSS ALL SANITIZED SPECS ---")
    all_clean = True
    for dataset, split, specs_path, bank_dict, _, _ in targets:
        clean_uids = set(bank_dict.keys())
        bad_demos = 0
        bad_pairs = 0
        total = 0
        with open(specs_path, "r", encoding="utf-8") as f:
            for line in f:
                total += 1
                r = json.loads(line)
                for d in r.get("demonstrations", []):
                    uid = d.get("function_uid") or d.get("id")
                    if uid not in clean_uids:
                        bad_demos += 1
                for p in r.get("demonstrations_pair", []):
                    uid = p.get("function_uid") or p.get("id")
                    if uid not in clean_uids:
                        bad_pairs += 1
        print(f"Audit {dataset}/{split}: total={total}, bad_demos={bad_demos}, bad_pairs={bad_pairs}")
        if bad_demos > 0 or bad_pairs > 0:
            all_clean = False

    if all_clean:
        print("\nSUCCESS: 100% of samples across all 4 splits are STRICTLY SANITIZED with ZERO external donors!")
    else:
        print("\nFAILURE: Some external donors remain.")
        sys.exit(1)


if __name__ == "__main__":
    main()
