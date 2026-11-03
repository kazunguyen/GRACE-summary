---
id: "osf-preregistration-edits-20261103"
title: "Nhật ký chỉnh sửa tài liệu preregistration cho OSF"
author: "Codex (trợ lý AI)"
author_type: "AI assistant"
requested_by: "Người dùng"
recorded_at: "2026-11-03T10:04:13+07:00"
updated_at: "2026-11-03T10:52:25+07:00"
timezone: "Asia/Bangkok"
work_date: "2026-11-03"
record_type: "document_edit_log"
status: "ongoing"
repository: "kazunguyen/GRACE-summary"
target_document: "preregistration.md"
---

# Nhật ký chỉnh sửa tài liệu preregistration cho OSF

File này ghi lại các chỉnh sửa đã thực hiện đối với [preregistration.md](../preregistration.md) để chuẩn bị hồ sơ OSF. Hiện ghi nhận bốn việc sau:

1. **Gắn link GitHub vào phần metadata đầu tài liệu.** Các mục `Protocol Configuration File`, `Locked Thresholds File` và `Tài liệu đề cương gốc` đã được chuyển từ đường dẫn văn bản sang link trỏ tới file tương ứng trên nhánh `baseline-unified` của `kazunguyen/GRACE-summary`. Các link bao gồm hai file `protocol.yaml`, hai file `thresholds.json` / `thresholds_flat.json` và bản PDF `PhuongAn2_De_cuong_nghien_cuu_GRACE_hop_nhat.pdf` trong `00_Reports_and_Docs/`.
2. **Sửa số lượng donor trong checklist.** Ở mục `8. Checklist Nghiệm Thu Đăng Ký Trước`, dòng `Manifest Dữ Liệu` được sửa từ **21.711** thành **21.691** donor Devign và từ **17.620** thành **17.636** donor ReVeal, khớp với hai dòng `Clean Donors Bank` trong bảng dữ liệu mục 7.1 của cùng tài liệu.
3. **Gắn link GitHub cho các artifact nhỏ trong bảng 7.1.** Giữ nguyên nhãn đường dẫn đang hiển thị, thêm link tới sáu file raw và hai file `stats.json` của snapshot `research_freeze_20261101` đã có trên `origin/baseline-unified`. Không gắn link GitHub giả cho hai file donor local (Devign 3.427.793.374 byte; ReVeal 1.887.092.268 byte), các specs đầy đủ vượt 100 MiB hoặc hai file subset 600 chưa tìm thấy. Đối chiếu SHA-256 cho thấy cả tám file đã liên kết đều không khớp mã băm đang in trong bảng; đã ghi cảnh báo ngay dưới bảng. Chưa đổi các mã băm hay khẳng định đây là cùng bản byte với đường dẫn cũ.
4. **Tải hai donor frozen lên Google Drive và gắn link.** Dùng `gdrive.exe` 3.9.1 qua PowerShell, tài khoản `yungngq@gmail.com`, tạo thư mục riêng `GRACE_OSF_FROZEN_DONORS_20261103` (ID `1tgtQul6NjmwthV3qSUp6yammsyhgkGGl`). Tải file từ `01_Author_Baseline_Unified/output/research_freeze_20261101/{devign,reveal}/donors.jsonl`, đổi tên trên Drive thành [devign_donors_research_freeze_20261101.jsonl](https://drive.google.com/file/d/10f_cARhg4BoMeIn4Q57qLzGiQuZUv00_/view?usp=sharing) và [reveal_donors_research_freeze_20261101.jsonl](https://drive.google.com/file/d/162syKwALRE2EvMbP5bBHA4P9eis30hjA/view?usp=sharing). **Từng file** có quyền `anyoneWithLink / reader`, kiểm tra lại bằng `gdrive permissions list`; thư mục cha giữ riêng tư. MD5 Drive khớp MD5 local: Devign `d332661e843347965b07b40d970a5864`, ReVeal `499d8dc0c4e66e580523c319fa0e9acd`. SHA-256 local khớp `freeze_manifest.json`: Devign `7727d2793fbb9f305e547bd6e7126ae70f2e0ee97e2b7c5c260322c6b6af5a62`, ReVeal `6bf44ab86c8524d239e610fdccff5916cfc402fef7945d7cbe7f695e287abbce`. Hai link Drive đã được gắn vào dòng `Clean Donors Bank` tương ứng trong bảng 7.1, giữ nguyên nhãn đường dẫn và hash lịch sử đang in; ghi rõ sự khác hash trong chú thích dưới bảng. Hệ thống duyệt quyền đã từ chối thao tác mở công khai cả thư mục vì sẽ mở rộng quyền tới nội dung khác; thao tác đó không được thực hiện và không ảnh hưởng quyền public của hai file.

Nhật ký này chỉ ghi nhận bốn chỉnh sửa trên; các nội dung khác của tài liệu chưa được ghi là đã chỉnh sửa tại đây.
