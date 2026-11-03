---
id: "osf-preregistration-edits-20261103"
title: "Nhật ký chỉnh sửa tài liệu preregistration cho OSF"
author: "Codex (trợ lý AI)"
author_type: "AI assistant"
requested_by: "Người dùng"
recorded_at: "2026-11-03T10:04:13+07:00"
timezone: "Asia/Bangkok"
work_date: "2026-11-03"
record_type: "document_edit_log"
status: "ongoing"
repository: "kazunguyen/GRACE-summary"
target_document: "preregistration.md"
---

# Nhật ký chỉnh sửa tài liệu preregistration cho OSF

File này ghi lại các chỉnh sửa đã thực hiện đối với [preregistration.md](../preregistration.md) để chuẩn bị hồ sơ OSF. Hiện ghi nhận ba việc sau:

1. **Gắn link GitHub vào phần metadata đầu tài liệu.** Các mục `Protocol Configuration File`, `Locked Thresholds File` và `Tài liệu đề cương gốc` đã được chuyển từ đường dẫn văn bản sang link trỏ tới file tương ứng trên nhánh `baseline-unified` của `kazunguyen/GRACE-summary`. Các link bao gồm hai file `protocol.yaml`, hai file `thresholds.json` / `thresholds_flat.json` và bản PDF `PhuongAn2_De_cuong_nghien_cuu_GRACE_hop_nhat.pdf` trong `00_Reports_and_Docs/`.
2. **Sửa số lượng donor trong checklist.** Ở mục `8. Checklist Nghiệm Thu Đăng Ký Trước`, dòng `Manifest Dữ Liệu` được sửa từ **21.711** thành **21.691** donor Devign và từ **17.620** thành **17.636** donor ReVeal, khớp với hai dòng `Clean Donors Bank` trong bảng dữ liệu mục 7.1 của cùng tài liệu.
3. **Gắn link GitHub cho các artifact nhỏ trong bảng 7.1.** Giữ nguyên nhãn đường dẫn đang hiển thị, thêm link tới sáu file raw và hai file `stats.json` của snapshot `research_freeze_20261101` đã có trên `origin/baseline-unified`. Không gắn link GitHub giả cho hai file donor local (Devign 3.427.793.374 byte; ReVeal 1.887.092.268 byte), các specs đầy đủ vượt 100 MiB hoặc hai file subset 600 chưa tìm thấy. Đối chiếu SHA-256 cho thấy cả tám file đã liên kết đều không khớp mã băm đang in trong bảng; đã ghi cảnh báo ngay dưới bảng. Chưa đổi các mã băm hay khẳng định đây là cùng bản byte với đường dẫn cũ.

Nhật ký này chỉ ghi nhận ba chỉnh sửa trên; các nội dung khác của tài liệu chưa được ghi là đã chỉnh sửa tại đây.
