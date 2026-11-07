"""Standalone Audit Script for Contrastive Pair Quality & Security Difference.
Chạy trực tiếp: python audit_contrastive_pairs.py
"""
import sys
import json
from pathlib import Path
from collections import Counter

# Đảm bảo in UTF-8 không lỗi trên Windows console cp1252
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def audit_file(path_str):
    p = Path(path_str)
    if not p.exists():
        print(f"File không tồn tại: {path_str}")
        return

    total = 0
    same_group = 0
    jaccards = []
    sec_diff_counter = Counter()

    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            d = json.loads(line)
            dp = d.get("demonstrations_pair", [])
            sec_diff = d.get("security_difference", "")
            sec_diff_counter[sec_diff] += 1
            total += 1

            if len(dp) == 2:
                g0 = dp[0].get("commit_group")
                g1 = dp[1].get("commit_group")
                if g0 and g1 and g0 == g1:
                    same_group += 1

                t0 = set(dp[0]["func"].split())
                t1 = set(dp[1]["func"].split())
                sim = len(t0 & t1) / max(1, len(t0 | t1))
                jaccards.append(sim)

    print(f"\n=======================================================")
    print(f"KIỂM TOÁN TỆP: {p.name} (N = {total} mẫu)")
    print(f"=======================================================")
    print(f"1. Cặp có cùng commit group: {same_group} / {total} ({same_group / total * 100:.2f}%)")
    if jaccards:
        mean_j = sum(jaccards) / len(jaccards)
        sorted_j = sorted(jaccards)
        median_j = sorted_j[len(sorted_j) // 2]
        low_sim = sum(1 for j in jaccards if j < 0.20)
        print(f"2. Độ tương đồng từ vựng (Token Jaccard) giữa 2 Demo trong cặp:")
        print(f"   - Trung bình: {mean_j:.4f}")
        print(f"   - Trung vị:   {median_j:.4f}")
        print(f"   - Tỷ lệ cặp có Jaccard < 0.20: {low_sim} / {total} ({low_sim / total * 100:.1f}%)")

    print(f"3. Phân phối Security Difference (Top chuỗi xuất hiện nhiều nhất):")
    for msg, count in sec_diff_counter.most_common(5):
        pct = count / total * 100
        print(f"   - [{count:4d} mẫu ({pct:5.1f}%)]: {msg[:90]}...")

if __name__ == "__main__":
    print("BẮT ĐẦU KIỂM TOÁN CÁC MẪU CONTRASTIVE DEMO...")
    base_dir = Path(__file__).resolve().parent
    for name in ["sample_100_devign_pairs.jsonl", "sample_100_reveal_pairs.jsonl"]:
        p = base_dir / "data_samples" / name
        audit_file(p)
