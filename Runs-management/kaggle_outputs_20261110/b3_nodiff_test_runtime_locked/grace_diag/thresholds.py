"""Chọn và KHÓA ngưỡng τ* chỉ từ validation, trước khi chạy test.

Quy tắc (đăng ký trước): với mỗi (dataset, arm, seed), τ* = argmax MCC trên validation,
lưới 0,01..0,99 bước 0,01, hòa thì lấy ngưỡng gần 0,5 nhất; chỉ dùng các mẫu hợp lệ.
Arm có `threshold_from: <arm gốc>` trong arms.yaml (B2-rep, B2-flip, B3-flip, B3-swap) KHÔNG chọn
ngưỡng riêng mà dùng τ* của arm gốc: chọn lại ngưỡng cho một arm đã bị đảo nhãn/đảo thứ tự/lặp
sẽ "sửa" đúng cái hiệu ứng cần đo và trộn thêm biến động do chọn ngưỡng.

Đầu ra: thresholds.json gồm τ*, MCC tại τ* trên validation, số mẫu dùng, chính sách, hash của
các file validation đã đọc và sha256 của chính nội dung — evaluate_final.py chỉ ĐỌC file này;
thiếu ngưỡng cho một arm có test là lỗi, không mặc định 0,5.

  python -m grace_diag.thresholds --runs runs/final --arms configs/arms.yaml \
      [--anchor-csv runs/anchor/anchor_scores.csv] --out runs/thresholds.json
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np

from . import stats as S


def load_validation_scores(runs_root: Path, anchor_csv: Optional[Path]) -> Tuple[Dict[Tuple[str, str, int], Dict], Dict[str, str]]:
    """-> {(dataset, arm, seed): {"y": [...], "s": [...]}} chỉ từ split validation; + hash file đã đọc."""
    data: Dict[Tuple[str, str, int], Dict] = defaultdict(lambda: {"y": [], "s": []})
    hashes: Dict[str, str] = {}
    for path in sorted(runs_root.glob("*/validation/*/*/records.jsonl")):
        hashes[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
        for line in open(path, encoding="utf-8"):
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("split") != "validation" or not r.get("valid") or r.get("s") is None:
                continue
            key = (r["dataset"], r["arm"], int(r["seed"]))
            data[key]["y"].append(int(r["label"]))
            data[key]["s"].append(float(r["s"]))
    if anchor_csv and anchor_csv.exists():
        hashes[str(anchor_csv)] = hashlib.sha256(anchor_csv.read_bytes()).hexdigest()
        # nhãn validation cho mốc có giám sát lấy từ records của bất kỳ arm LLM nào cùng dataset (cùng ID)
        id_label: Dict[Tuple[str, str], int] = {}
        for path in sorted(runs_root.glob("*/validation/*/*/records.jsonl")):
            for line in open(path, encoding="utf-8"):
                if line.strip():
                    r = json.loads(line)
                    id_label[(r["dataset"], str(r["id"]))] = int(r["label"])
        for r in csv.DictReader(open(anchor_csv, encoding="utf-8")):
            if r["split"] != "validation":
                continue
            lab = id_label.get((r["dataset"], r["id"]))
            if lab is None:
                continue
            key = (r["dataset"], r["arm"], int(r["seed"]))
            data[key]["y"].append(lab)
            data[key]["s"].append(float(r["score"]))
    return data, hashes


def compute_thresholds(val: Dict[Tuple[str, str, int], Dict], arms_cfg: Dict[str, Dict], grid=None) -> Dict[str, Dict]:
    out: Dict[str, Dict] = {}
    # 1) arm chọn ngưỡng riêng
    for (d, a, sd), v in sorted(val.items()):
        if arms_cfg.get(a, {}).get("threshold_from"):
            continue
        y, s = np.asarray(v["y"]), np.asarray(v["s"], dtype=float)
        tau, m = S.pick_threshold(y, s, grid)
        defined = m == m  # NaN khi không có ngưỡng nào cho MCC xác định (điểm hằng / một lớp)
        out[f"{d}|{a}|{sd}"] = {"dataset": d, "arm": a, "seed": sd, "tau": round(float(tau), 4),
                                "mcc_val": (float(m) if defined else None), "n_val": int(len(y)),
                                "policy": "argmax_mcc_validation" if defined else "fallback_0.5_no_defined_mcc"}
    # 2) arm dùng ngưỡng của arm gốc
    for (d, a, sd), v in sorted(val.items()):
        base = arms_cfg.get(a, {}).get("threshold_from")
        if not base:
            continue
        src = out.get(f"{d}|{base}|{sd}") or out.get(f"{d}|{base}|42")
        if src is None:
            raise SystemExit(f"Thiếu ngưỡng của arm gốc {base} cho {d}/{a}/{sd}: chạy validation của {base} trước")
        out[f"{d}|{a}|{sd}"] = {"dataset": d, "arm": a, "seed": sd, "tau": src["tau"], "mcc_val": None, "n_val": int(len(v["y"])),
                                "policy": f"inherit_from:{base}"}
    # arm dùng ngưỡng gốc nhưng chưa có validation riêng vẫn phải có mục (để test đọc được)
    for key, src in list(out.items()):
        d, a, sd = src["dataset"], src["arm"], src["seed"]
        for child, cfg in arms_cfg.items():
            if cfg.get("threshold_from") == a and f"{d}|{child}|{sd}" not in out:
                out[f"{d}|{child}|{sd}"] = {"dataset": d, "arm": child, "seed": sd, "tau": src["tau"], "mcc_val": None,
                                            "n_val": 0, "policy": f"inherit_from:{a}"}
    return out


def write_locked(out_path: Path, thresholds: Dict[str, Dict], input_hashes: Dict[str, str], grid_desc: str) -> str:
    body = {"rule": "tau* = argmax MCC on validation; grid " + grid_desc + "; ties -> closest to 0.5; valid samples only",
            "inputs_sha256": input_hashes, "thresholds": thresholds}
    text = json.dumps(body, indent=2, ensure_ascii=False, sort_keys=True)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    body["locked_sha256"] = digest
    if out_path.exists():
        old = json.loads(out_path.read_text(encoding="utf-8"))
        if old.get("locked_sha256") and old.get("locked_sha256") != digest:
            # không ghi đè ngưỡng đã khóa; giữ lịch sử
            backup = out_path.with_suffix(f".{old['locked_sha256'][:8]}.json")
            backup.write_text(json.dumps(old, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
            print(f"CẢNH BÁO: ngưỡng đã khóa trước đó khác bản mới; bản cũ lưu tại {backup}. Ghi lý do vào CHANGES_AFTER_PREREG.md")
    out_path.write_text(json.dumps(body, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    return digest


def load_locked(path: Path) -> Dict[str, Dict]:
    body = json.loads(Path(path).read_text(encoding="utf-8"))
    check = {k: v for k, v in body.items() if k != "locked_sha256"}
    digest = hashlib.sha256(json.dumps(check, indent=2, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    if digest != body.get("locked_sha256"):
        raise SystemExit("thresholds.json đã bị sửa sau khi khóa (sha256 không khớp)")
    return body["thresholds"]


def _main():
    import argparse, sys, yaml
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", required=True, type=Path)
    ap.add_argument("--arms", required=True, type=Path)
    ap.add_argument("--anchor-csv", type=Path)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()
    arms_cfg = {x["name"]: x for x in yaml.safe_load(a.arms.read_text(encoding="utf-8"))["arms"]}
    val, hashes = load_validation_scores(a.runs, a.anchor_csv)
    if not val:
        raise SystemExit("Không có records validation nào dưới " + str(a.runs))
    th = compute_thresholds(val, arms_cfg)
    digest = write_locked(a.out, th, hashes, "0.01..0.99 step 0.01")
    for k, v in th.items():
        print(f"{k:40s} tau*={v['tau']:.2f}  mcc_val={'' if v['mcc_val'] is None else round(v['mcc_val'], 3)}  n={v['n_val']}  {v['policy']}")
    print("locked", a.out, "sha256", digest[:16])


if __name__ == "__main__":
    _main()
