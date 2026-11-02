---
id: "drive-large-inputs-pack-20261102"
title: "Đóng gói 16 input lớn để tải lên Drive"
author: "Codex (trợ lý AI)"
recorded_at: "2026-11-02T21:55:38.847+07:00"
timezone: "Asia/Bangkok"
status: "completed_verified"
---

# Đóng gói input lớn để tải lên Drive

## Yêu cầu và lựa chọn

Gom 16 file trên ngưỡng Git vào chung một thư mục. Dữ liệu gốc có tổng 22,35 GiB; ổ D/C không đủ chỗ tạo bản sao đầy đủ. Người dùng chọn nén ZIP trong thư mục bàn giao, giữ file nguồn nguyên vị trí.

## Đã làm

- Tạo ZIP64 chứa sáu CPG Joern, hai donor frozen có graph, bốn specs và bốn donor copies B2 cũ; giữ đường dẫn tương đối từ gốc repo.
- Tính SHA256 từng file khi nén, so với checksum chuẩn hiện có; đọc ngược đủ 16 entry để kiểm SHA256 và CRC.
- Kiểm nguồn giữ nguyên size/mtime trong suốt lượt đóng gói; không di chuyển/xóa hoặc chỉnh sửa payload gốc.
- Kèm manifest, hướng dẫn giải nén, verifier Python chuẩn và checksum ZIP.

## Kết quả và bằng chứng

- [Thư mục bàn giao](../output/drive_upload_20261102/): ZIP 2272473727 byte (2.12 GiB), chứa đủ 16 payload tổng 23996808869 byte.
- [Manifest](../output/drive_upload_20261102/DRIVE_INPUTS_MANIFEST_20261102.json), [checksum archive](../output/drive_upload_20261102/ARCHIVE_SHA256.json), [trạng thái hoàn tất](../output/drive_upload_20261102/PACK_STATUS.json).
- SHA256 ZIP: `ba930b27c769af4c53594f2ce912595ea9276416c392a18139ef09d43c6c63e0`.
- Thư mục output vốn được Git ignore; đây là gói local để người dùng tự tải lên Drive, chưa upload dịch vụ ngoài.

Mở README_RESTORE.md trong thư mục để khôi phục đúng đường dẫn vào repo và kiểm lại dữ liệu sau giải nén.
