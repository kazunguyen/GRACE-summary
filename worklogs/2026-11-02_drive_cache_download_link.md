---
id: "drive-cache-download-link-20261102"
title: "Bổ sung link Drive cho cache tái sử dụng dựng prompt"
author: "Codex (trợ lý AI)"
recorded_at: "2026-11-02T23:01:36+07:00"
timezone: "Asia/Bangkok"
status: "completed_documentation"
remote_contents_verified: false
---

# Bổ sung nguồn tải cache ngoài Git

## Yêu cầu

Người nhận clone repo cần nguồn tải 16 file lớn không commit. Người dùng cung cấp link Drive và yêu cầu chèn vào tài liệu dự án.

## Đã làm

- Thêm [link Drive](https://drive.google.com/drive/folders/1oV49c5JgLJl5sD1_v7NPlDOs0Hik_0Zl?usp=sharing) vào mục dữ liệu của README gốc và danh mục input.
- Ghi tên ZIP, kích thước 2.272.473.727 byte và SHA256 ba930b27c769af4c53594f2ce912595ea9276416c392a18139ef09d43c6c63e0 theo gói local đã kiểm.
- Bổ sung hướng dẫn kiểm checksum, giải nén đúng gốc repo và chạy VERIFY_RESTORE.py cùng verifier input Git.
- Phân biệt CodeT5/raw/compact bank/B2 new_reference trên Git với CPG/donor graph/specs trong ZIP; giữ phiên donor cũ/mới riêng.

## File thay đổi và kiểm tra

- [README](../README.md#tải-cache-lớn-từ-google-drive).
- [Danh mục input](../Runs-management/PROMPT_INPUTS_GIT_20261102.md).
- Kiểm link Drive trùng URL người dùng cung cấp, tên/size/hash trùng ARCHIVE_SHA256.json của gói local; kiểm diff và kích thước trước commit.

## Giới hạn xác minh

Link Drive do người dùng cung cấp. Công cụ duyệt web chưa đọc được nội dung folder; không ghi rằng đã tải lại hoặc kiểm hash bản trên Drive. Checksum công bố giúp người nhận kiểm đúng gói sau tải. Không thay payload/archive hoặc các notebook/run đang được chỉnh ở workspace.
