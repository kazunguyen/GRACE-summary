"""Contrastive Demonstration Pair Builder for B3 Family.
Tuân thủ nghiêm ngặt nguyên tắc Zero Label Leakage:
- Nửa thứ nhất lấy từ B2 demo (hoặc unsupervised retrieval).
- Nửa thứ hai lấy từ donor sạch có nhãn ngược lại (1 - label(B2)), Jaccard cao nhất với query.
- Chuẩn hóa thứ tự cặp: Vulnerable (1) luôn đứng trước, Safe (0) luôn đứng sau.
- Tự động phân tích security_difference giữa 2 demo.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def normalize_code_tokens(code: str) -> List[str]:
    toks = re.findall(r"[A-Za-z_]\w*|\d+|[^\s\w]", code)
    return [t for t in toks if not t.startswith("//")]


def jaccard_similarity(code_a: str, code_b: str) -> float:
    sa = set(normalize_code_tokens(code_a))
    sb = set(normalize_code_tokens(code_b))
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def load_donors_bank(donor_clean_path: Path) -> Dict[str, Any]:
    donors = []
    by_uid = {}
    vuln_donors = []
    safe_donors = []

    with open(donor_clean_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            d = json.loads(line)
            uid = str(d.get("function_uid") or d.get("id")).strip()
            d["function_uid"] = uid
            d["target"] = int(d["target"])
            donors.append(d)
            by_uid[uid] = d
            if d["target"] == 1:
                vuln_donors.append(d)
            else:
                safe_donors.append(d)

    def build_index(pool):
        inv = defaultdict(list)
        tokens_map = []
        for idx, d in enumerate(pool):
            toks = set(normalize_code_tokens(d["func"]))
            tokens_map.append(toks)
            for t in toks:
                inv[t].append(idx)
        return pool, tokens_map, inv

    return {
        "donors": donors,
        "by_uid": by_uid,
        "all_idx": build_index(donors),
        "vuln_idx": build_index(vuln_donors),
        "safe_idx": build_index(safe_donors),
    }


def find_best_counterpart(query_code: str, target_label: int, donor_pack: Dict[str, Any]) -> Dict[str, Any]:
    """Tìm donor sạch có nhãn target_label với Jaccard token similarity cao nhất với query_code."""
    pool, tokens_map, inv = donor_pack["vuln_idx"] if target_label == 1 else donor_pack["safe_idx"]
    q_toks = set(normalize_code_tokens(query_code))
    if not q_toks or not pool:
        return pool[0] if pool else None

    cand_scores = defaultdict(int)
    for t in q_toks:
        for idx in inv.get(t, []):
            cand_scores[idx] += 1

    if not cand_scores:
        return pool[0]

    top_cands = sorted(cand_scores.items(), key=lambda x: -x[1])[:200]
    best_sim = -1.0
    best_d = pool[top_cands[0][0]]
    for idx, _ in top_cands:
        d_toks = tokens_map[idx]
        inter = len(q_toks & d_toks)
        union = len(q_toks | d_toks)
        sim = inter / max(1, union)
        if sim > best_sim:
            best_sim = sim
            best_d = pool[idx]

    return best_d


def identify_security_difference(vuln_code: str, safe_code: str) -> str:
    """Phân tích điểm khác biệt an ninh mấu chốt giữa mẫu Vulnerable và Safe."""
    diffs = []
    v_lower = vuln_code.lower()
    s_lower = safe_code.lower()

    # Kiểm tra kích thước / giới hạn bộ đệm
    has_v_bounds = any(k in v_lower for k in ("sizeof", "< sizeof", "len <", "size <", "bounds"))
    has_s_bounds = any(k in s_lower for k in ("sizeof", "< sizeof", "len <", "size <", "bounds"))
    if has_s_bounds and not has_v_bounds:
        diffs.append("Safe demo validates buffer size or bounds before operation; Vulnerable demo lacks bounds check")

    # Kiểm tra NULL check
    has_v_null = any(k in v_lower for k in ("== null", "!= null", "!ptr", "!p", "if (!"))
    has_s_null = any(k in s_lower for k in ("== null", "!= null", "!ptr", "!p", "if (!"))
    if has_s_null and not has_v_null:
        diffs.append("Safe demo validates pointers against NULL before dereferencing")

    # Kiểm tra hàm copy nguy hiểm
    v_has_copy = any(k in v_lower for k in ("memcpy", "strcpy", "sprintf", "strcat"))
    s_has_safe_copy = any(k in s_lower for k in ("strncpy", "snprintf", "strlcpy"))
    if v_has_copy and s_has_safe_copy:
        diffs.append("Safe demo uses bounded copy routines; Vulnerable demo performs unbounded copy")
    elif v_has_copy and not has_v_bounds:
        diffs.append("Vulnerable demo performs unbounded memory copy without bounds check")

    if not diffs:
        diffs.append("Differences in bounds validation conditions and control flow constraints")

    return "; ".join(diffs)


def build_contrastive_pair(
    query_code: str,
    b2_demo: Dict[str, Any],
    donor_pack: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], str]:
    """Xây dựng cặp tương phản B3 từ B2 demo và đối chứng opposite-label donor."""
    b2_label = int(b2_demo["target"])
    opposite_label = 1 - b2_label
    counterpart = find_best_counterpart(query_code, target_label=opposite_label, donor_pack=donor_pack)

    counter_demo = {
        "function_uid": counterpart["function_uid"],
        "func": counterpart["func"],
        "target": counterpart["target"],
    }
    b2_clean = {
        "function_uid": b2_demo["function_uid"],
        "func": b2_demo["func"],
        "target": b2_demo["target"],
    }

    if b2_label == 1:
        vuln_d = b2_clean
        safe_d = counter_demo
    else:
        vuln_d = counter_demo
        safe_d = b2_clean

    # Chuẩn hóa thứ tự: Vulnerable (1) đứng trước, Safe (0) đứng sau
    pair = [vuln_d, safe_d]
    sec_diff = identify_security_difference(vuln_d["func"], safe_d["func"])

    return pair, sec_diff
