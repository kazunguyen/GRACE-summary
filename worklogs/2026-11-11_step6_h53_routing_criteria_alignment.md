---
id: "step6-h53-routing-criteria-alignment-20261111"
title: "Bổ sung kiểm định routing theo đầy đủ tiêu chí H5.3"
recorded_at: "2026-11-11"
timezone: "Asia/Bangkok"
status: "code-updated-rerun-notebook-06-pending"
---

# Bổ sung kiểm định routing H5.3

## Lý do

Rà soát kết quả Step 6 cho thấy đường routing đã có đủ benefit, confidence, random 20 seed và oracle ở q = 5%, 10%, 25%. Tuy vậy, phần CI lưu trong kết quả cũ mới kiểm định benefit − confidence bằng MCC; chưa xuất đủ các phép so sánh H5.3 công bố trong OSF preregistration.

## Thay đổi

- Cập nhật `STEP6_supervised_anchors/src/step6_complementarity.py` để tại q = 10% xuất paired cluster-bootstrap CI (5.000 lượt) cho benefit − confidence trên balanced accuracy và MCC.
- Bổ sung paired cluster-bootstrap CI cho balanced accuracy benefit − random. Mỗi bootstrap resample lấy test clusters và resample 20 random-router seeds có hoàn lại; manifest/kết quả ghi rõ phương pháp.
- Ghi kiểm tra số ca LLM sửa đúng so với phân vị 97,5% của 20 random experts có cùng tỷ lệ dự đoán 1.
- Mỗi dataset có `h5_3_registered_checks` nêu các cận, các điều kiện đạt/chưa đạt và kết quả tổng hợp. H3-B gate là phân tích chính; SUP-LR là bổ sung.
- Giữ nguyên output CI benefit − confidence MCC cũ để tương thích; giữ nguyên `configs/protocol.yaml`, preregistration, thresholds, lock, input B2/H3-B/SUP-LR và kết quả cũ. Script hash mới làm run tiếp theo ghi vào thư mục output mới.
- Cập nhật notebook `06_run_step6_complementarity_wsl.ipynb` để hiển thị các check H5.3 sau khi chạy.

## Phạm vi và trạng thái

- Không gọi lại LLM, không fit lại anchor/gate, không chọn lại ngưỡng; notebook Step 6 chỉ tái phân tích các score đã khóa.
- Đây là sửa phần hiện thực hóa/báo cáo các phép so sánh đã được ghi trong OSF preregistration, không đổi giả thuyết, margin hay protocol.
- Chưa chạy lại notebook và chưa tạo output mới trong lần cập nhật này. Cần chạy lại duy nhất `STEP6_supervised_anchors/06_run_step6_complementarity_wsl.ipynb`; không cần chạy notebook 02, 04 hoặc 05.
- Chưa chạy test theo chỉ dẫn của phiên làm việc.
