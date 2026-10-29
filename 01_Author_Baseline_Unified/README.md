# GRACE Author Baseline Unified (01_Author_Baseline_Unified)

Phiên bản mã nguồn chuẩn hóa phục dựng mô hình gốc (Baseline) của tác giả GRACE, tuân thủ nghiêm ngặt theo bản giao kèo đánh giá chung (`evaluation_contract_v2_context8192bytes_20261029`).

---

## 1. Mục Đích & Bối Cảnh

Trước đây, nhóm nghiên cứu tồn tại nhiều bản baseline khác nhau:
1. Bản triển khai của Hiếu tại `d:\JUNIOR\LabThayTho\HuuHieu03\GRACE\02_Baseline_Code_Author`.
2. Các bản tái dựng tại `Graduation-Project\Ablation_V2\Reproduced-Code-Based` và `Reproduced-Paper-Based`.
3. Mã nguồn gốc tác giả phát hành (`basep.py`, `genexample.py`, `llmpre.py`, `util.py`).

Giữa các bản này có 4 sự sai lệch kỹ thuật lớn:
- **Mô hình LLM**: Định danh model, xử lý chế độ thinking ngầm, tham số ngẫu nhiên, endpoint API.
- **Xây dựng Prompt**: Trần ngữ cảnh (hạ từ 24.000 bytes về 8.192 bytes), trần đồ thị (40 node, 80 edge), thứ tự cắt xén ưu tiên, chỉ dẫn ép khuôn đầu ra dòng cuối 0/1.
- **Evaluator**: Parser cũ có lỗi tự động gán ép nhãn 0 khi gặp phản hồi sai định dạng; nay đã chuẩn hóa sang parser nghiêm ngặt (Strict binary last line), loại bỏ hoàn toàn thiên vị đánh giá.
- **Tech Stack & Thuật toán**: Chuẩn hóa quy trình CodeT5 768d + BERT-Whitening 256d + Reranker lai ghép $0.7 \times \text{Jaccard} + 0.3 \times \text{AST\_Sim}$ từ ngân sách ứng viên Top 50 theo Contract.

Thư mục này là **bản baseline chốt chung duy nhất**, được kiểm thử chạy được ngay lập tức, làm mốc quy chiếu tin cậy cho mọi nghiên cứu cải tiến tiếp theo.

---

## 2. Cấu Trúc Mã Nguồn

```
01_Author_Baseline_Unified/
├── config.py                 # Cấu hình trung tâm, nạp tham số từ contract và .env
├── evaluation_contract.yaml  # Bản hợp đồng đánh giá chuẩn (Context 8.192 bytes)
├── prompt_template.txt       # Mẫu prompt chuẩn mực
├── data_loader.py            # Nạp và chuẩn hóa dữ liệu (Local JSON, HF Hub, Mock)
├── graph_extractor.py        # Định dạng cấu trúc Whole CPG (nodes <= 40, edges <= 80)
├── embedding_engine.py       # CodeT5 encoder + Whitening 256d + Fallback CPU
├── retrieval_engine.py       # Candidate pool Top 50 + Hybrid Reranker (0.7 Code + 0.3 AST)
├── prompt_builder.py         # Ghép prompt và kiểm soát trần 8.192 bytes UTF-8
├── llm_backbone.py           # Bộ gọi LLM đa nền tảng (FPT AI / Vertex AI / Mock, thinking=False)
├── parser.py                 # Parser nghiêm ngặt kiểm tra đúng dòng cuối 0/1
├── evaluator.py              # Đánh giá benchmark trên tập Valid, tách biệt Invalid
├── run_pipeline.py           # CLI điều phối thực nghiệm toàn trình với checkpointing
├── test_baseline.py          # Bộ kiểm thử tự động xác minh tính toàn vẹn
├── requirements.txt          # Danh sách thư viện phụ thuộc
├── ARCHITECTURE_DECISIONS.md # Báo cáo chi tiết quyết định kỹ thuật cho 4 điểm sai khác
└── RUN_GUIDE.md              # Hướng dẫn chi tiết cách chạy từ Mock tới Full API
```

---

## 3. Khởi Chạy Nhanh Trong 15 Giây

```bash
# 1. Chạy toàn bộ 5 bài kiểm thử tự động
python test_baseline.py

# 2. Chạy thử nghiệm end-to-end trên dữ liệu mẫu offline
python run_pipeline.py --mock --dataset mock --max-targets 10 --experiment-name quick_test
```

Chi tiết kịch bản chạy trên API thật (FPT Cloud, Google Vertex AI) hoặc Kaggle GPU xem tại [RUN_GUIDE.md](file:///d:/JUNIOR/LabThayTho/GRACE-summary/01_Author_Baseline_Unified/RUN_GUIDE.md).
Quyết định giải quyết 4 điểm sai khác xem tại [ARCHITECTURE_DECISIONS.md](file:///d:/JUNIOR/LabThayTho/GRACE-summary/01_Author_Baseline_Unified/ARCHITECTURE_DECISIONS.md).
