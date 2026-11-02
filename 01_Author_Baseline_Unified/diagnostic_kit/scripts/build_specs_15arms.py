#!/usr/bin/env python3
"""Đóng gói file data/specs/<dataset>_<split>_15arms.jsonl đầy đủ 15 arm chẩn đoán.
Cấu trúc chuẩn: {id, query_code, nodes, edges, demonstrations, demonstrations_pair, security_difference, h2_evidence, h2_source_limits, label, group}.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "01_Author_Baseline_Unified/diagnostic_kit/src"))

from grace_diag.contrastive_pair_builder import build_contrastive_pair, load_donors_bank
from grace_diag.sink_evidence import build_evidence_text


def pack_15arms_specs(
    base_specs_path: Path,
    out_path: Path,
    donor_clean_path: Path,
    dataset: str,
    split: str,
) -> int:
    print(f"[{dataset}/{split}] Đang đọc {base_specs_path}...")
    donors_bank = load_donors_bank(donor_clean_path)
    print(f"[{dataset}/{split}] Đã nạp {len(donors_bank['donors'])} donors sạch.")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with open(base_specs_path, "r", encoding="utf-8") as in_f, open(out_path, "w", encoding="utf-8") as out_f:
        for line in in_f:
            if not line.strip():
                continue
            r = json.loads(line)
            qid = r["id"]
            canonical_id = f"reveal:{split}:{count}" if dataset == "reveal" else qid
            query_code = r["query_code"]
            label = int(r["label"])
            group = r.get("group")
            nodes = r.get("nodes") or []
            edges = r.get("edges") or []
            demos = r.get("demonstrations") or []

            # 1. B2 demo
            b2_demo = demos[0] if demos else None
            if not b2_demo:
                b2_demo = donors_bank["donors"][0]

            # 2. Cặp tương phản B3
            pair = r.get("demonstrations_pair")
            sec_diff = r.get("security_difference")
            if not pair or len(pair) != 2:
                pair, sec_diff = build_contrastive_pair(query_code, b2_demo, donors_bank)
            elif not sec_diff:
                from grace_diag.contrastive_pair_builder import identify_security_difference
                sec_diff = identify_security_difference(pair[0]["func"], pair[1]["func"])

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
                "demonstrations": [b2_demo],
                "demonstrations_pair": pair,
                "security_difference": sec_diff,
                "h2_evidence": h2_ev,
                "h2_source_limits": {"nodes": 40, "edges": 80},
                "label": label,
                "group": group,
            }
            out_f.write(json.dumps(spec_row, ensure_ascii=False) + "\n")
            count += 1
            if count % 1000 == 0:
                print(f"[{dataset}/{split}] Đã xử lý {count} dòng...")

    print(f"[{dataset}/{split}] HOÀN TẤT {count} specs -> {out_path}")
    return count


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=REPO_ROOT)
    args = ap.parse_args()

    specs_dir = args.root / "data" / "specs"
    manifests_dir = args.root / "data" / "manifests"

    targets = [
        ("devign", "validation", specs_dir / "devign_validation.jsonl", specs_dir / "devign_validation_15arms.jsonl", manifests_dir / "devign_donor_clean.jsonl"),
        ("devign", "test", specs_dir / "devign_test.jsonl", specs_dir / "devign_test_15arms.jsonl", manifests_dir / "devign_donor_clean.jsonl"),
        ("reveal", "validation", specs_dir / "reveal_validation.jsonl", specs_dir / "reveal_validation_15arms.jsonl", manifests_dir / "reveal_donor_clean.jsonl"),
        ("reveal", "test", specs_dir / "reveal_test.jsonl", specs_dir / "reveal_test_15arms.jsonl", manifests_dir / "reveal_donor_clean.jsonl"),
    ]

    for dataset, split, base_in, out_f, donor_clean in targets:
        pack_15arms_specs(base_in, out_f, donor_clean, dataset, split)


if __name__ == "__main__":
    main()
