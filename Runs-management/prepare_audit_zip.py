import os
import sys
import json
import shutil
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

bundle_dir = Path("audit_contrastive_icl_bundle")
if bundle_dir.exists():
    shutil.rmtree(bundle_dir)
bundle_dir.mkdir(parents=True, exist_ok=True)

(bundle_dir / "src").mkdir(exist_ok=True)
(bundle_dir / "data_samples").mkdir(exist_ok=True)
(bundle_dir / "evaluation_results").mkdir(exist_ok=True)
(bundle_dir / "osf_governance").mkdir(exist_ok=True)

# 1. Copy synthesis document
shutil.copy2(
    "docs/TONG_HOP_VAN_DE_CONTRASTIVE_ICL_VA_TIEN_DO_OSF.md",
    bundle_dir / "TONG_HOP_VAN_DE_CONTRASTIVE_ICL_VA_TIEN_DO_OSF.md"
)

# 2. Copy source code files
shutil.copy2(
    "01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/contrastive_pair_builder.py",
    bundle_dir / "src/contrastive_pair_builder.py"
)
shutil.copy2(
    "01_Author_Baseline_Unified/diagnostic_kit/scripts/build_specs_15arms.py",
    bundle_dir / "src/build_specs_15arms.py"
)
shutil.copy2(
    "01_Author_Baseline_Unified/diagnostic_kit/tests/test_probes.py",
    bundle_dir / "src/test_probes.py"
)

# 3. Copy OSF governance files
shutil.copy2("AGENTS.md", bundle_dir / "osf_governance/AGENTS.md")

prereg_info = """# THÔNG TIN ĐĂNG KÝ TRƯỚC (OSF PRE-REGISTRATION)

- **Trạng thái:** PUBLIC REGISTRATION (Đã đăng ký công khai chính thức)
- **Đường dẫn liên kết:** https://osf.io/fqgh2
- **Dấu thời gian chứng thực:** Nov 3, 2026, 11:13 PM (Asia/Bangkok / UTC+7)
- **Git Commit Anchor:** `7a1e16168591c37f005599cb4d5dc3ce33f7d950`
- **Git Tag:** `prereg-v1`
- **Dedicated Freeze Branch:** `release/osf-preregistration`

## Các tệp tài liệu đăng ký đã niêm phong mã băm SHA-256:
1. `GRACE_OSF_PREREGISTRATION_20261102.pdf`
   - SHA-256: `22648ead896baf5c1032de700c12fb97bd6dc44f0a8049292532ae6c0468b14c`
2. `GRACE_OSF_PREREGISTRATION_20261102.zip`
   - SHA-256: `6d6e8fe46f1dc59bf5f399defca59ba8ab0c362a0b13d0cb101c16320a2a082e`
3. `attachment_sha256.json`
   - SHA-256: `41888a239e902dc1911f7e19b5c033726ea537689fcbc82caf6aaee275dde049`
4. `configs/thresholds.json`
   - Checksum: `a0108431ad859aacc3dab29ca7e88a7eb404428b4d60fc251e3bbae7d350c831`
"""
(bundle_dir / "osf_governance/PREREGISTRATION_INFO.md").write_text(prereg_info, encoding="utf-8")

# 4. Copy Evaluation Metrics
eval_files = [
    # Author (Dũng) B2 Baseline: Đã chạy CẢ Validation VÀ Test (Census 100%)
    ("01_Author_Baseline_Unified/kaggle_qwen_q4_b2/downloaded_output_20261101_run3/grace_b2_four_split_8h/devign/validation/evaluation.json", "evaluation_results/devign_validation_B2_author_evaluation.json"),
    ("01_Author_Baseline_Unified/kaggle_qwen_q4_b2/downloaded_output_20261101_run3/grace_b2_four_split_8h/devign/test/evaluation.json", "evaluation_results/devign_test_B2_author_evaluation.json"),
    ("01_Author_Baseline_Unified/kaggle_qwen_q4_b2/downloaded_output_20261101_run3/grace_b2_four_split_8h/reveal/validation/evaluation.json", "evaluation_results/reveal_validation_B2_author_evaluation.json"),
    ("01_Author_Baseline_Unified/kaggle_qwen_q4_b2/downloaded_output_20261101_run3/grace_b2_four_split_8h/reveal/test/evaluation.json", "evaluation_results/reveal_test_B2_author_evaluation.json"),

    # Nhóm ta chạy mới (04-05/11): Mới chạy MÌNH Validation (Census 100%)
    ("runs/final/devign/validation/B1-full/42/evaluation.json", "evaluation_results/devign_validation_B1-full_evaluation.json"),
    ("runs/final/reveal/validation/B1-full/42/evaluation.json", "evaluation_results/reveal_validation_B1-full_evaluation.json"),
    ("runs/final/devign/validation/B2-nolabel/42/evaluation.json", "evaluation_results/devign_validation_B2-nolabel_evaluation.json"),
    ("runs/final/reveal/validation/B2-nolabel/42/evaluation.json", "evaluation_results/reveal_validation_B2-nolabel_evaluation.json"),
    ("runs/final/devign/validation/B2-labelonly/42/evaluation.json", "evaluation_results/devign_validation_B2-labelonly_evaluation.json"),
    ("runs/final/reveal/validation/B2-labelonly/42/evaluation.json", "evaluation_results/reveal_validation_B2-labelonly_evaluation.json"),
    ("runs/final/devign/validation/B2-rep/42/evaluation.json", "evaluation_results/devign_validation_B2-rep_evaluation.json"),
    ("runs/final/reveal/validation/B2-rep/42/evaluation.json", "evaluation_results/reveal_validation_B2-rep_evaluation.json"),
    ("runs/final/devign/validation/B1-shuf/42/evaluation.json", "evaluation_results/devign_validation_B1-shuf_seed42_evaluation.json"),
    ("runs/final/reveal/validation/B1-shuf/42/evaluation.json", "evaluation_results/reveal_validation_B1-shuf_seed42_evaluation.json"),
]

for src, dst in eval_files:
    if os.path.exists(src):
        shutil.copy2(src, bundle_dir / dst)

# 5. Extract 100 sample pairs (with full function code) for audit
for ds in ['devign', 'reveal']:
    in_path = f'data/specs/{ds}_validation_15arms.jsonl'
    out_path = bundle_dir / f"data_samples/sample_100_{ds}_pairs.jsonl"
    with open(in_path, 'r', encoding='utf-8') as f_in, open(out_path, 'w', encoding='utf-8') as f_out:
        for i in range(100):
            line = f_in.readline()
            if not line: break
            d = json.loads(line)
            dp = d.get('demonstrations_pair', [])
            item = {
                'id': d['id'],
                'target_label': d['label'],
                'target_commit_group': d.get('group'),
                'target_code': d['query_code'],
                'demonstrations_pair': [
                    {
                        'target': dp[0]['target'],
                        'commit_group': dp[0].get('group'),
                        'func': dp[0]['func']
                    },
                    {
                        'target': dp[1]['target'],
                        'commit_group': dp[1].get('group'),
                        'func': dp[1]['func']
                    }
                ] if len(dp) == 2 else [],
                'security_difference': d.get('security_difference')
            }
            f_out.write(json.dumps(item, ensure_ascii=False) + '\n')

# 6. Write standalone audit script
audit_script = '''"""Standalone Audit Script for Contrastive Pair Quality & Security Difference.
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

    print(f"\\n=======================================================")
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
'''
(bundle_dir / "audit_contrastive_pairs.py").write_text(audit_script, encoding="utf-8")

# 7. Write README_AUDIT.md
readme_content = """# HỒ SƠ KIỂM TOÁN THUẬT TOÁN CONTRASTIVE DEMO (ARM B3) & TIẾN ĐỘ OSF

> **Gói tài liệu phục vụ quy trình thẩm định độc lập (Audit & Peer Review)**  
> **Dự án:** GRACE Diagnostic Replication & Contrastive Evaluation  
> **Thời gian xuất hồ sơ:** 05/11/2026  

---

## 1. Cấu trúc Thư mục Hồ sơ

```text
audit_contrastive_icl_bundle/
├── README_AUDIT.md                                # Tài liệu hướng dẫn kiểm toán này
├── TONG_HOP_VAN_DE_CONTRASTIVE_ICL_VA_TIEN_DO_OSF.md # Báo cáo tổng hợp chi tiết vấn đề & số liệu
├── audit_contrastive_pairs.py                    # Script chạy độc lập để tái hiện 100% số liệu kiểm toán
├── src/                                          # Mã nguồn thuật toán liên quan
│   ├── contrastive_pair_builder.py               # Thuật toán tìm cặp tương phản & parser an ninh
│   ├── build_specs_15arms.py                     # Script đóng gói cặp vào spec 15 arm
│   └── test_probes.py                            # Unit tests kiểm tra probes B3
├── data_samples/                                 # Mẫu dữ liệu thực tế (đầy đủ code hàm để soi lỗi)
│   ├── sample_100_devign_pairs.jsonl             # 100 mẫu đối chứng trên Devign
│   └── sample_100_reveal_pairs.jsonl             # 100 mẫu đối chứng trên ReVeal
├── evaluation_results/                           # Kết quả chạy thực nghiệm GPU chính thức (Census 100%)
│   ├── # 1. Baseline B2 của Dũng (Chạy ĐẦY ĐỦ CẢ Validation VÀ Test)
│   ├── devign_validation_B2_author_evaluation.json
│   ├── devign_test_B2_author_evaluation.json
│   ├── reveal_validation_B2_author_evaluation.json
│   ├── reveal_test_B2_author_evaluation.json
│   │
│   ├── # 2. Các Arm nhóm ta mới chạy (MỚI CHẠY MÌNH Validation, chưa chạy Test)
│   ├── devign_validation_B1-full_evaluation.json
│   ├── reveal_validation_B1-full_evaluation.json
│   ├── devign_validation_B2-nolabel_evaluation.json
│   ├── reveal_validation_B2-nolabel_evaluation.json
│   ├── devign_validation_B2-labelonly_evaluation.json
│   ├── reveal_validation_B2-labelonly_evaluation.json
│   ├── devign_validation_B2-rep_evaluation.json
│   ├── reveal_validation_B2-rep_evaluation.json
│   ├── devign_validation_B1-shuf_seed42_evaluation.json
│   └── reveal_validation_B1-shuf_seed42_evaluation.json
└── osf_governance/                               # Bằng chứng pháp lý & Hợp đồng OSF đã đóng băng
    ├── AGENTS.md                                 # Hợp đồng vận hành & quy tắc đóng băng nghiêm ngặt
    └── PREREGISTRATION_INFO.md                   # Thông tin xác thực, URL OSF và bảng băm SHA-256
```

---

## 2. Hướng dẫn Chạy Kiểm toán Nhanh (Audit Quickstart)

Để kiểm tra và tái hiện ngay các số liệu thống kê về độ lệch của thuật toán chọn cặp:

```bash
python audit_contrastive_pairs.py
```

### Các số liệu auditor có thể kiểm chứng ngay lập tức:
1. **0% Cặp cùng Commit:** Cả 2 demo trong cặp đối chứng hoàn toàn thuộc 2 file/dự án xa lạ.
2. **Độ tương đồng từ vựng cực thấp:** Median Jaccard chỉ ~0.18 (Devign) và ~0.29 (ReVeal), hơn 50% cặp có Jaccard < 0.20.
3. **Ảo giác giải thích mã hóa cứng:** 67% - 83% rơi vào câu mặc định *"Differences in bounds validation conditions and control flow constraints"*.

---

## 3. Bản chất của Vấn đề Cần Thẩm định

1. **Vì sao thuật toán hiện tại chưa đạt chuẩn Counterfactual?**
   - Thuật toán chọn Demo 2 dựa trên độ tương đồng từ vựng với Target Code (chứ không tìm bản vá tương ứng của Demo 1).
   - Dẫn đến việc ghép một hàm socket mạng với một hàm giải mã âm thanh/video.
2. **Ảnh hưởng tới bài báo:**
   - Trong nhánh **Confirmatory (OSF)**: Phải giữ nguyên dữ liệu gốc để bảo vệ cam kết tiền đăng ký công khai trên OSF (https://osf.io/fqgh2).
   - Trong nhánh **Exploratory (Đóng góp mới)**: Xây dựng thuật toán `B3-enhanced` chỉ ghép các cặp hàm trước/sau commit vá lỗi thực sự (Commit-level patch pairs).
"""
(bundle_dir / "README_AUDIT.md").write_text(readme_content, encoding="utf-8")

# 8. Create ZIP archive
zip_path = Path("HO_SO_AUDIT_CONTRASTIVE_ICL_VA_OSF_20261105.zip")
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(bundle_dir):
        for f in files:
            fp = Path(root) / f
            arcname = fp.relative_to(bundle_dir)
            zf.write(fp, arcname)

print(f"Created archive: {zip_path.resolve()} ({zip_path.stat().st_size} bytes)")
