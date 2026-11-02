# Gói Artifact Chẩn đoán Offline Bước 0 (Complementarity & Benefit Router)

## 1. Tổng quan
Thư mục này lưu trữ các tệp kết quả nghiệm thu chính thức của **Bước 0: Phân tích chẩn đoán Offline** theo đúng quy chuẩn [Đề cương nghiên cứu hợp nhất](../../De_cuong_nghien_cuu_GRACE_hop_nhat.pdf) (Phụ lục C, trang 39, tiêu chí 1):
- **Quy chuẩn thực thi**: Phương pháp luận chuẩn 2-Split (Khớp mô hình và chọn ngưỡng $\tau^*$ trên tập Validation; Đánh giá và kiểm định Paired Cluster Bootstrap CI độc lập trên tập Test).
- **Tài nguyên**: Hoàn toàn Offline (0 GPU).
- **Bộ dữ liệu**: Devign ($N=2.732$ Validation, $N=2.732$ Test) và REVEAL ($N=2.273$ Validation, $N=2.274$ Test).

---

## 2. Thông số kỹ thuật & Đơn vị gom cụm (Cluster Units)
- **Devign**:
  - Đơn vị gom cụm: `commit_id` (2.025 cụm trên Validation, 2.068 cụm trên Test).
  - Ngưỡng Gate: $\tau_{\text{gate}} = 0,36$.
  - Ngưỡng tối ưu xác định từ Validation: $\tau_{\text{pre}}^* = 0,34$, $\tau_{\text{post}}^* = 0,56$.
  - Số lượt Paired Bootstrap CI: 1.000 lượt (seed = `20261117`).
- **REVEAL**:
  - Đơn vị gom cụm: `file_hash` (627 cụm trên Validation, 646 cụm trên Test).
  - Ngưỡng Gate: $\tau_{\text{gate}} = 0,17$.
  - Ngưỡng tối ưu xác định từ Validation: $\tau_{\text{pre}}^* = 0,22$, $\tau_{\text{post}}^* = 0,19$.
  - Số lượt Paired Bootstrap CI: 1.000 lượt (seed = `20261117`).

---

## 3. Cấu trúc tệp
```
Runs-management/step0_diagnostic/
├── README.md
├── devign/
│   ├── canonical_devign.csv            # Dữ liệu hợp nhất kèm nhãn và dự đoán
│   ├── canonical_devign_val.csv        # Split validation
│   ├── canonical_devign_test.csv       # Split test
│   ├── diagnostic_report_devign.json   # Báo cáo JSON đầy đủ số liệu và CI
│   └── diagnostic_summary_devign.md    # Tóm tắt Markdown gồm ma trận Sửa/Hỏng & Oracle
└── reveal/
    ├── canonical_reveal.csv
    ├── canonical_reveal_val.csv
    ├── canonical_reveal_test.csv
    ├── diagnostic_report_reveal.json
    └── diagnostic_summary_reveal.md
```

---

## 4. Bằng chứng đối chiếu tiêu chí Phụ lục C
1. **Tái tạo metric lịch sử**: Đạt sai lệch metric $= 0.00000000 \le 0.001$.
2. **Bảng sửa–hỏng (Repair/Harm)**: Có đầy đủ các hàng đối chứng `ALL-0`, `ALL-1` và `RANDOM` (20 lượt lặp ngẫu nhiên) theo đúng Section B.5.
3. **Paired Cluster Bootstrap**: Hoạt động với 2.068 cụm commit (Devign) và 646 cụm file hash (REVEAL).
4. **Trần chẩn đoán Oracle & OOF Benefit Router**: Đã sinh đường cong định tuyến selective routing curves.
