"""So hai file records.jsonl trên cùng ID. Ba việc dùng chung một công cụ:
  (1) kiểm tra đối chiếu môi trường (cùng arm, chạy ở hai nền tảng/runtime);
  (2) kiểm chứng B2-rep so với B2 (lặp cùng điều kiện): điểm s trùng tuyệt đối ở mọi ID là dấu hiệu
      đường thực thi tất định (batch 1, cùng seed) HOẶC cache — phải xem thêm timestamp/elapsed/cache_tag;
  (3) đo độ nhạy nhãn thô (B2 so với B2-flip) hay bất kỳ cặp arm nào.

  python scripts/compare_records.py --a runs/final/devign/test/B2/42/records.jsonl \
      --b runs/final/devign/test/B2-rep/42/records.jsonl [--tau 0.70] [--out runs/checks/b2_vs_rep.json]
      [--max-flip 0.01 --max-ds 0.05]   # có hai ngưỡng này thì thoát mã != 0 khi vượt

In: số ID chung, tỷ lệ trùng pred_argmax, tỷ lệ đổi nhãn tại τ (và tại 0,5), phân vị |Δs|, số ID có s trùng
bit, tập hash runtime/model của mỗi file, khoảng timestamp, elapsed trung bình, cache_tag.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


def load(p: Path):
    out = {}
    for line in open(p, encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            out[str(r["id"])] = r
    return out


def provenance(recs):
    keys = ("runtime_contract_sha256", "model_sha256", "backend", "quantization", "cache_tag", "prompt_variant")
    prov = {k: sorted({str(r.get(k)) for r in recs.values() if r.get(k) is not None}) for k in keys}
    ts = sorted(str(r.get("timestamp")) for r in recs.values() if r.get("timestamp"))
    el = [float(r["elapsed_s"]) for r in recs.values() if isinstance(r.get("elapsed_s"), (int, float))]
    return {**prov, "timestamp_min": ts[0] if ts else None, "timestamp_max": ts[-1] if ts else None,
            "elapsed_mean_s": float(np.mean(el)) if el else None, "n_elapsed_zero": int(sum(1 for e in el if e <= 0))}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--a", required=True, type=Path)
    ap.add_argument("--b", required=True, type=Path)
    ap.add_argument("--tau", type=float, default=None, help="ngưỡng đã khóa của arm A (B dùng cùng ngưỡng)")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--max-flip", type=float, default=None)
    ap.add_argument("--max-ds", type=float, default=None)
    a = ap.parse_args()
    A, B = load(a.a), load(a.b)
    ids = sorted(set(A) & set(B))
    if not ids:
        sys.exit("không có ID chung")
    both_valid = [i for i in ids if A[i].get("valid") and B[i].get("valid")]
    sa = np.array([float(A[i]["s"]) for i in both_valid])
    sb = np.array([float(B[i]["s"]) for i in both_valid])
    pa = np.array([int(A[i].get("pred_argmax", sa[k] >= 0.5)) for k, i in enumerate(both_valid)])
    pb = np.array([int(B[i].get("pred_argmax", sb[k] >= 0.5)) for k, i in enumerate(both_valid)])
    ds = np.abs(sa - sb)
    y = np.array([int(A[i]["label"]) for i in both_valid])
    rep = {
        "file_a": str(a.a), "file_b": str(a.b), "n_common": len(ids), "n_both_valid": len(both_valid),
        "n_only_a": len(set(A) - set(B)), "n_only_b": len(set(B) - set(A)),
        "pred_argmax_agreement": float((pa == pb).mean()),
        "flip_rate_at_0.5": float(((sa >= 0.5) != (sb >= 0.5)).mean()),
        "abs_delta_s": {"mean": float(ds.mean()), "median": float(np.median(ds)), "p90": float(np.quantile(ds, 0.9)),
                        "p99": float(np.quantile(ds, 0.99)), "max": float(ds.max())},
        "n_bitwise_identical_s": int((sa == sb).sum()),
        "share_bitwise_identical_s": float((sa == sb).mean()),
        "label_mismatch_between_files": int(sum(1 for i in both_valid if int(A[i]["label"]) != int(B[i]["label"]))),
        "provenance_a": provenance(A), "provenance_b": provenance(B),
    }
    if a.tau is not None:
        fa, fb = sa >= a.tau, sb >= a.tau
        rep["tau"] = a.tau
        rep["flip_rate_at_tau"] = float((fa != fb).mean())
        rep["flips_at_tau_by_direction"] = {"a1_to_b0": int((fa & ~fb).sum()), "a0_to_b1": int((~fa & fb).sum())}
        rep["flips_at_tau_right_to_wrong"] = int(((fa.astype(int) == y) & (fb.astype(int) != y)).sum())
        rep["flips_at_tau_wrong_to_right"] = int(((fa.astype(int) != y) & (fb.astype(int) == y)).sum())
    notes = []
    if rep["share_bitwise_identical_s"] >= 0.999:
        notes.append("điểm s trùng bit ở >= 99,9% ID: đường thực thi tất định hoặc cache — xác nhận bằng timestamp/elapsed/cache_tag và nhật ký phiên")
    if rep["label_mismatch_between_files"]:
        notes.append("nhãn khác nhau giữa hai file cho cùng ID: kiểm tra manifest dữ liệu")
    for side in ("a", "b"):
        if len(rep[f"provenance_{side}"]["runtime_contract_sha256"]) > 1:
            notes.append(f"file {side} trộn nhiều runtime hash")
    if rep["provenance_a"]["runtime_contract_sha256"] and rep["provenance_b"]["runtime_contract_sha256"] and \
            set(rep["provenance_a"]["runtime_contract_sha256"]) != set(rep["provenance_b"]["runtime_contract_sha256"]):
        notes.append("hai file khác runtime hash: chênh lệch gồm cả tác động môi trường")
    rep["notes"] = notes
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
    bad = False
    if a.max_flip is not None and rep.get("flip_rate_at_tau", rep["flip_rate_at_0.5"]) > a.max_flip:
        bad = True
    if a.max_ds is not None and rep["abs_delta_s"]["max"] > a.max_ds:
        bad = True
    if bad:
        print("KHÔNG ĐẠT tiêu chí --max-flip/--max-ds")
        sys.exit(1)


if __name__ == "__main__":
    main()
