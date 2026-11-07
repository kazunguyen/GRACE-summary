# HỒ SƠ KIỂM TOÁN THUẬT TOÁN CONTRASTIVE DEMO (ARM B3) & TIẾN ĐỘ OSF

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
