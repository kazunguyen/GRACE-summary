"""Metric trên một tập con ID và phần bù của nó — để phân tầng (ví dụ B1-H2: mẫu có/không có evidence;
B1: graph_missing; mẫu gần trùng với bank) mà không sửa script đánh giá chính.

  python scripts/subset_metrics.py --records runs/final/reveal/test/B1-H2/42/records.jsonl \
      [--ids ids_with_evidence.txt | --field graph_missing --value false] [--tau 0.21]

In cho tập con và phần bù: n, n_valid, tỷ lệ dương, AUROC, AUPRC, MCC/BA/F1/tỷ lệ đoán 1 tại s>=0,5 và tại τ.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from grace_diag import stats as S  # noqa: E402


def metrics(recs, tau):
    valid = [r for r in recs if r.get("valid")]
    out = {"n": len(recs), "n_valid": len(valid)}
    if len(valid) < 2:
        return out
    y = np.array([int(r["label"]) for r in valid])
    s = np.array([float(r["s"]) for r in valid])
    out["positive_rate"] = float(y.mean())
    out["auroc"] = S.auroc(y, s)
    out["auprc"] = S.auprc(y, s)
    m = S.thresholded_metrics(y, (s >= 0.5).astype(int))
    out.update({"mcc@0.5": m["mcc"], "ba@0.5": m["balanced_accuracy"], "f1@0.5": m["f1"], "ppr@0.5": m["positive_rate"]})
    if tau is not None:
        m = S.thresholded_metrics(y, (s >= tau).astype(int))
        out.update({"tau": tau, "mcc@tau": m["mcc"], "ba@tau": m["balanced_accuracy"], "f1@tau": m["f1"], "ppr@tau": m["positive_rate"]})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--records", required=True, type=Path)
    ap.add_argument("--ids", type=Path, help="file text, một ID mỗi dòng")
    ap.add_argument("--field", help="tên trường trong record để lọc (thay cho --ids)")
    ap.add_argument("--value", help="giá trị cần khớp (so sánh dạng chuỗi, không phân biệt hoa thường)")
    ap.add_argument("--tau", type=float)
    a = ap.parse_args()
    recs = [json.loads(l) for l in open(a.records, encoding="utf-8") if l.strip()]
    if a.ids:
        want = {l.strip() for l in open(a.ids, encoding="utf-8") if l.strip()}
        inside = [r for r in recs if str(r["id"]) in want]
        outside = [r for r in recs if str(r["id"]) not in want]
        name = f"ids in {a.ids.name}"
    elif a.field:
        inside = [r for r in recs if str(r.get(a.field)).lower() == str(a.value).lower()]
        outside = [r for r in recs if str(r.get(a.field)).lower() != str(a.value).lower()]
        name = f"{a.field} == {a.value}"
    else:
        sys.exit("cần --ids hoặc --field/--value")
    rep = {"records": str(a.records), "subset": name, "inside": metrics(inside, a.tau), "outside": metrics(outside, a.tau),
           "all": metrics(recs, a.tau)}
    print(json.dumps(rep, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
