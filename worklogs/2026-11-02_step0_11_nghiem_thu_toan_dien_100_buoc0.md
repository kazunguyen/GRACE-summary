---
id: "step0-20261102-11"
title: "Nghiệm thu toàn diện 100% Bước 0 (Complementarity & Benefit Router Pipeline)"
author: "Antigravity (AI Lead Coordinator)"
author_type: "AI assistant"
requested_by: "Người dùng trong chat"
recorded_at: "2026-11-02T21:16:00+07:00"
timezone: "Asia/Bangkok"
work_date: "2026-11-02"
record_type: "official_step_acceptance"
status: "completed_100_percent"
step0_status: "accepted_100_percent"
repository: "kazunguyen/GRACE-summary"
branch: "hieu"
evidence_verified_at: "2026-11-02T21:16:00+07:00"
---

# Báo cáo nghiệm thu chính thức: Hoàn tất 100% Bước 0 (Offline Diagnostic)

## 1. Tuyên bố nghiệm thu
Đến thời điểm hiện tại, **Bước 0: Phân tích chẩn đoán Offline (Complementarity & Benefit Router)** đã được thực thi trọn vẹn và đạt **100% tiêu chí nghiệm thu** quy định tại [Đề cương nghiên cứu hợp nhất](../../De_cuong_nghien_cuu_GRACE_hop_nhat.pdf) (Phụ lục C, trang 39, tiêu chuẩn 1).

---

## 2. Kết quả thực thi thực tế trên hai tập dữ liệu chuẩn

### 2.1. Tập dữ liệu Devign ($N=2.732$ Validation, $N=2.732$ Test)
- **Đơn vị Bootstrap**: Cluster Bootstrap theo `commit_id` với **2.025 cụm** trên Validation và **2.068 cụm** trên Test (khớp tuyệt đối với `protocol.yaml`).
- **Ngưỡng Gate $\tau_{\text{gate}}$**: $0,36$.
- **Ngưỡng tối ưu xác định từ Validation**: $\tau_{\text{pre}}^* = 0,3400$, $\tau_{\text{post}}^* = 0,5600$.
- **Đánh giá trên Test độc lập (Paired Cluster Bootstrap 1.000 lượt)**:
  - $\Delta\text{MCC}$: $+0,0053$ (95% CI: $[-0,0384, +0,0493]$).
  - $\Delta\text{F1}$: $-0,1657$ (95% CI: $[-0,1950, -0,1346]$).
  - $\Delta\text{AUROC}$: $+0,0015$ (95% CI: $[-0,0014, +0,0045]$).
  - Kết luận thống kê ($\delta$-verdict): `INCONCLUSIVE` (CI bao gồm 0 và có khả năng chạm biên lợi ích $\delta$).
- **Ma trận Sửa/Hỏng (Repair/Harm)**:
  - Tổng số ca Gate đoán sai được LLM sửa: **694 ca** (tỷ lệ sửa lỗi: $65,41\%$).
  - Số ca Gate đoán đúng bị LLM làm hỏng: **858 ca** (tỷ lệ làm hỏng: $51,35\%$).
  - Đối chứng ngẫu nhiên (Random Expert, 20 lượt seed): Sửa ròng $-229,4$ (LLM đạt sửa ròng $-164$, vượt trội so với ngẫu nhiên).
- **Trần lý thuyết Oracle**: Accuracy đạt **$86,57\%$** (vượt Gate standalone $+25,40\%$), MCC đạt **$0,7307$** (vượt Gate standalone $+0,4422$).

### 2.2. Tập dữ liệu REVEAL ($N=2.273$ Validation, $N=2.274$ Test)
- **Đơn vị Bootstrap**: Cluster Bootstrap theo `file_hash` với **627 cụm** trên Validation và **646 cụm** trên Test (khớp tuyệt đối với `protocol.yaml`).
- **Ngưỡng Gate $\tau_{\text{gate}}$**: $0,17$.
- **Ngưỡng tối ưu xác định từ Validation**: $\tau_{\text{pre}}^* = 0,2200$, $\tau_{\text{post}}^* = 0,1900$.
- **Đánh giá trên Test độc lập (Paired Cluster Bootstrap 1.000 lượt)**:
  - $\Delta\text{MCC}$: $-0,0274$ (95% CI: $[-0,0536, -0,0001]$).
  - $\Delta\text{AUROC}$: $+0,0026$ (95% CI: $[-0,0031, +0,0084]$).
  - Kết luận thống kê ($\delta$-verdict): `HARM` (CI hoàn toàn nằm dưới 0, LLM làm giảm hiệu quả khi kết hợp thô).
- **Ma trận Sửa/Hỏng (Repair/Harm)**:
  - Số ca sửa lỗi của Gate: **180 ca** (tỷ lệ sửa lỗi: $57,14\%$).
  - Số ca làm hỏng: **197 ca** (tỷ lệ làm hỏng: $10,06\%$).
  - Đối chứng ngẫu nhiên (Random Expert): Sửa ròng $-55,1$ (LLM đạt sửa ròng $-17$, an toàn hơn đoán mò).
- **Trần lý thuyết Oracle**: Accuracy đạt **$94,06\%$**, MCC đạt **$0,6439$** (vượt Gate standalone $+0,2881$).

---

## 3. Danh mục Artifact chính thức đã lưu trữ
Toàn bộ artifact đã được tạo lập và lưu trữ có hệ thống tại:
- Báo cáo JSON chi tiết:
  - [`Runs-management/step0_diagnostic/devign/diagnostic_report_devign.json`](../Runs-management/step0_diagnostic/devign/diagnostic_report_devign.json)
  - [`Runs-management/step0_diagnostic/reveal/diagnostic_report_reveal.json`](../Runs-management/step0_diagnostic/reveal/diagnostic_report_reveal.json)
- Báo cáo tóm tắt Markdown kèm bảng biểu:
  - [`Runs-management/step0_diagnostic/devign/diagnostic_summary_devign.md`](../Runs-management/step0_diagnostic/devign/diagnostic_summary_devign.md)
  - [`Runs-management/step0_diagnostic/reveal/diagnostic_summary_reveal.md`](../Runs-management/step0_diagnostic/reveal/diagnostic_summary_reveal.md)
- Bảng dữ liệu kiểm chứng canonical:
  - `Runs-management/step0_diagnostic/devign/canonical_devign_*.csv`
  - `Runs-management/step0_diagnostic/reveal/canonical_reveal_*.csv`
- Hướng dẫn và mô tả:
  - [`Runs-management/step0_diagnostic/README.md`](../Runs-management/step0_diagnostic/README.md)

---

## 4. Bảng đối chiếu tiêu chuẩn Phụ lục C (Checklist Verification)

| Tiêu chuẩn Phụ lục C | Quy định | Kết quả nghiệm thu thực tế | Đánh giá |
|---|---|---|:---:|
| **Tái tạo metric lịch sử** | Sai lệch $\le 0,001$ từ file từng mẫu | Sai lệch metric $= 0.00000000$ | **PASS** |
| **Bảng Sửa–Hỏng** | Bắt buộc có các hàng đối chứng `ALL-0`, `ALL-1` và `RANDOM` (20 seed) | Đầy đủ 3 hàng đối chứng, xuất bảng chi tiết theo Section B.5 | **PASS** |
| **Gom cụm Bootstrap** | Devign theo commit ID, REVEAL theo file hash | Devign = 2.068 cụm Test; REVEAL = 646 cụm Test | **PASS** |
| **Trần Oracle** | Đo giới hạn lý thuyết tối đa của mô hình kết hợp | Devign đạt Oracle Acc $86,57\%$, REVEAL đạt $94,06\%$ | **PASS** |
| **Out-Of-Fold Router** | Huấn luyện $R(x)$ trên Validation, áp sang Test độc lập | Ridge benefit router, xuất đường cong định tuyến chọn lọc ($q=10\%$) | **PASS** |
| **Kiểm thử tự động** | Pass toàn bộ test suite | 13/13 test trong `test_step0_offline_diagnostic.py` pass xanh | **PASS** |
| **MỨC ĐỘ HOÀN THÀNH** | **Hoàn tất 100% tiêu chí Bước 0** | **100% ĐẠT CHUẨN** | **ACCEPT** |
