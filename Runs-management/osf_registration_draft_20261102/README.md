# Hồ sơ OSF bản nháp

Chưa đăng ký OSF. Ngày soạn trong PDF là giờ máy local; OSF chỉ ghi thời điểm khi gửi registration trên nền tảng và hoàn tất quy trình xác nhận.

- PDF để duyệt/đính kèm: output/pdf/GRACE_OSF_DRAFT_20261102.pdf.
- Bản nguồn dễ sửa: OSF_DRAFT.md; document.json là nội dung dùng dựng PDF. Sửa nguồn phải sinh lại PDF và hash tương ứng trước gửi.
- source_inventory.json và evidence_snapshot/: bằng chứng tại thời điểm soạn, bao gồm audit mới chưa commit.
- attachment_sha256.json: hash các file đóng gói; không chứng thực thời gian.

Vào https://osf.io/registries, đăng nhập, tạo Registration (có thể chọn Open-Ended), điền metadata/tác giả, đính kèm hồ sơ đã duyệt, Preview, chọn public/embargo và Submit. Làm theo email/trạng thái xác nhận OSF. Chỉ tạo draft hoặc upload PDF vào Project chưa phải đăng ký chính thức.

Trước Submit cần chủ nhiệm duyệt mục20 của PDF: tác giả/cơ quan, dữ liệu cloud đã sinh/đã xem, public/embargo, remediation demo<25%, endpoint H2.2/80%, họ Holm, quy tắc CI suy biến và REVEAL grouping. Các mục chưa chốt được ghi pending; không suy rằng hồ sơ này đã khóa toàn bộ phân tích.

Sau gửi, giữ nguyên bytes attachment; lưu URL/ngày gửi/ngày xác nhận ở biên bản mới, không chỉnh PDF cũ để điền ngày OSF. Không có inference, fit ngưỡng, commit hoặc push phát sinh từ việc sinh hồ sơ này.

Hướng dẫn: https://help.osf.io/article/330-welcome-to-registrations
