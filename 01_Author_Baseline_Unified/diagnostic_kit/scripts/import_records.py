"""Gom các file records.jsonl nằm rải rác (theo bố cục thư mục của repo thực nghiệm) về đúng bố cục
của bộ công cụ:  <dst>/<dataset>/<split>/<arm>/<seed>/records.jsonl  — để chạy được
`python -m grace_diag.thresholds` và `python -m grace_diag.evaluate_final` (CI ghép cặp, McNemar, Holm).

  python scripts/import_records.py --src /path/to/GRACE-summary --dst runs/final [--dry-run]
      [--groups-csv groups.csv] [--on-conflict abort|first|latest] [--only-arm B2 B2-flip ...]

Quy tắc:
  * dataset/split/arm/seed đọc từ CHÍNH từng record (không đoán từ tên thư mục); seed thiếu -> 42.
  * Trường bắt buộc: id, dataset, split, arm, label, s, valid (pred_argmax suy ra từ s nếu thiếu).
  * Cùng (dataset, split, arm, seed, id) xuất hiện ở hai file nguồn: s bằng nhau -> giữ một bản;
    s khác nhau -> xung đột; mặc định dừng và in danh sách (xung đột là dấu hiệu hai lượt chạy khác
    runtime cho cùng mẫu, phải xử lý có chủ đích, không gộp lặng lẽ).
  * Mỗi nhóm ghi kèm import_manifest.json: file nguồn + sha256, số bản ghi, tập hash runtime/model/backend
    (nhiều hơn một hash runtime trong cùng arm = trộn runtime -> cảnh báo), khoảng timestamp.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

REQUIRED = ("id", "dataset", "split", "arm", "label", "s", "valid")
PROVENANCE_FIELDS = ("runtime_contract_sha256", "model_sha256", "backend", "quantization", "threshold_lock_sha256",
                     "prompt_variant", "cache_tag")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def norm_dataset(x: str) -> str:
    x = str(x).strip().lower()
    return {"reveal": "reveal", "reveal_": "reveal", "devign": "devign"}.get(x, x)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True, type=Path, nargs="+", help="thư mục gốc (quét đệ quy) hoặc file records.jsonl")
    ap.add_argument("--dst", required=True, type=Path)
    ap.add_argument("--pattern", default="records*.jsonl")
    ap.add_argument("--only-arm", nargs="*", default=None)
    ap.add_argument("--only-split", nargs="*", default=None)
    ap.add_argument("--groups-csv", type=Path, help="CSV id,group (commit/project) để bootstrap theo cụm")
    ap.add_argument("--on-conflict", choices=["abort", "first", "latest"], default="abort")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    files = []
    for s in a.src:
        files += [s] if s.is_file() else sorted(s.rglob(a.pattern))
    if not files:
        sys.exit("không tìm thấy file records nào")
    groups = {}
    if a.groups_csv:
        import csv
        for r in csv.DictReader(open(a.groups_csv, encoding="utf-8")):
            groups[str(r["id"])] = r["group"]

    buckets = defaultdict(dict)          # key -> {id: record}
    sources = defaultdict(set)           # key -> {file}
    conflicts = []
    n_read = 0
    for f in files:
        for ln, line in enumerate(open(f, encoding="utf-8"), 1):
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError as e:
                sys.exit(f"{f}:{ln}: JSON lỗi: {e}")
            missing = [k for k in REQUIRED if k not in r]
            if missing:
                sys.exit(f"{f}:{ln}: thiếu trường {missing}")
            r["dataset"] = norm_dataset(r["dataset"])
            r["seed"] = int(r.get("seed", 42))
            if a.only_arm and r["arm"] not in a.only_arm:
                continue
            if a.only_split and r["split"] not in a.only_split:
                continue
            if r.get("pred_argmax") is None and r.get("s") is not None:
                r["pred_argmax"] = int(float(r["s"]) >= 0.5)
            if groups and "group" not in r:
                r["group"] = groups.get(str(r["id"]))
            r["_source"] = str(f)
            key = (r["dataset"], r["split"], r["arm"], r["seed"])
            rid = str(r["id"])
            n_read += 1
            old = buckets[key].get(rid)
            if old is None:
                buckets[key][rid] = r
            else:
                same = (old.get("s") is None and r.get("s") is None) or (
                    old.get("s") is not None and r.get("s") is not None and abs(float(old["s"]) - float(r["s"])) < 1e-9)
                if same:
                    continue
                conflicts.append({"key": "|".join(map(str, key)), "id": rid, "s_a": old.get("s"), "s_b": r.get("s"),
                                  "src_a": old["_source"], "src_b": str(f),
                                  "runtime_a": old.get("runtime_contract_sha256"), "runtime_b": r.get("runtime_contract_sha256")})
                if a.on_conflict == "latest" and str(r.get("timestamp", "")) > str(old.get("timestamp", "")):
                    buckets[key][rid] = r
            sources[key].add(str(f))

    print(f"đọc {n_read} bản ghi từ {len(files)} file; {len(buckets)} nhóm (dataset|split|arm|seed)")
    if conflicts:
        print(f"XUNG ĐỘT: {len(conflicts)} id có điểm s khác nhau giữa hai file nguồn (10 dòng đầu):")
        for c in conflicts[:10]:
            print("  ", json.dumps(c, ensure_ascii=False))
        if a.on_conflict == "abort":
            sys.exit("dừng: xử lý xung đột có chủ đích (chạy lại phần thiểu số hoặc --on-conflict first|latest kèm ghi nhật ký)")

    summary = []
    for key in sorted(buckets):
        recs = buckets[key]
        d, sp, arm, seed = key
        valid = sum(1 for r in recs.values() if r.get("valid"))
        prov = {k: sorted({str(r.get(k)) for r in recs.values() if r.get(k) is not None}) for k in PROVENANCE_FIELDS}
        ts = sorted(str(r.get("timestamp", "")) for r in recs.values() if r.get("timestamp"))
        mixed = len(prov.get("runtime_contract_sha256", [])) > 1 or len(prov.get("model_sha256", [])) > 1
        row = {"dataset": d, "split": sp, "arm": arm, "seed": seed, "n": len(recs), "n_valid": valid,
               "sources": sorted(sources[key]), "provenance": prov, "timestamp_min": ts[0] if ts else None,
               "timestamp_max": ts[-1] if ts else None, "mixed_runtime": mixed}
        summary.append(row)
        flag = "  <-- TRỘN RUNTIME" if mixed else ""
        print(f"{d:8s} {sp:11s} {arm:14s} seed {seed}: n={len(recs):5d} valid={valid:5d} runtime={len(prov['runtime_contract_sha256'])} src={len(sources[key])}{flag}")
        if a.dry_run:
            continue
        out_dir = a.dst / d / sp / arm / str(seed)
        out_dir.mkdir(parents=True, exist_ok=True)
        with open(out_dir / "records.jsonl", "w", encoding="utf-8") as fo:
            for rid in sorted(recs, key=lambda x: (len(x), x)):
                r = dict(recs[rid])
                r.pop("_source", None)
                fo.write(json.dumps(r, ensure_ascii=False) + "\n")
        man = {**row, "sources_sha256": {s: sha256_file(Path(s)) for s in row["sources"]},
               "records_sha256": sha256_file(out_dir / "records.jsonl"),
               "conflicts": [c for c in conflicts if c["key"] == "|".join(map(str, key))], "on_conflict": a.on_conflict}
        (out_dir / "import_manifest.json").write_text(json.dumps(man, indent=2, ensure_ascii=False), encoding="utf-8")
    if not a.dry_run:
        (a.dst / "import_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        print("ghi", a.dst)


if __name__ == "__main__":
    main()
