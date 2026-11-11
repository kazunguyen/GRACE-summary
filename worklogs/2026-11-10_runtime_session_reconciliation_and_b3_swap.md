# Đối chiếu runtime từng phiên và triển khai B3-swap — 10/11/2026

Đã đọc lại 265 record-file artifact (88 file hash khác nhau), log/ZIP và saved notebook; loại cache test và không cộng bản sao thành phiên mới. Audit chính: `Runs-management/runtime_session_reconciliation_20261110/REPORT.md`, JSON ledger, CSV scope rows và hash từng artifact.

B2-nolabel, B2-labelonly và B2-rep test: sáu process gắn chính xác đủ 15.018 record với timestamp window, ID/score hiển thị, hash records/manifest; score tính lại khớp. Session log có wheel hash thực và CMake 4.4.4. Source dùng verbose=False, thiếu native 49/49, archive-origin/loaded-library/effective-thread/contract provenance. Giữ PARTIAL_CORE_MATCH_NOT_FULL_LOCK; không gán native validation sang test, không tự rerun.

Validation của ba arm và B1-full có native/core phù hợp và record window khớp. B1-shuf validation chỉ gắn được 619 Devign + 2.273 REVEAL seed44 với log đang có; 12.123 rows còn cần đúng session log. Gói executed ZIP hiện kiểm không có log seed43. Giữ nguyên biên bản test B1-shuf đã nghiệm thu riêng.

B2-rand test: exact full-record equality gán đủ final 15.018 về head42 4.749, head43 4.760, head44 4.661 và tail 848/877. Giữ 29 overlap head. Phát hiện checkout CRLF làm raw source/lock hash khác; phục hồi đúng byte Git blob vào audit evidence, khớp provenance. Provenance packages/constructor/GPU/threads đúng, còn native/build log chưa có để replay. Không đổi raw hash/profile của các record head/tail.

B3 lịch sử: 29 record locked_vti6l7nv và 947 locked_rt3jkftt đạt launch runtime theo sáu package, source/helper/native/build log hash và record-provenance references. Công bố đúng subset 976. 4.029 original rows chỉ đạt native/core matching, chưa full contract chain; không biến chúng thành amended B3. Các B0/B1/B2/B2-flip/B1-H2 đã được đối chiếu với saved output và ghi rõ phần carry-over/raw artifact đang thiếu; Colab tách profile.

Trong lúc audit, người dùng yêu cầu chạy B3-swap bằng account còn quota và nhắc có bốn account. Đã nạp cấu hình huuhieu3333, lznt123, tomandjerry223 và thanhduy9a4tv (access token); không in credential. Chỉ Thanh Duy còn quota khả dụng dương, gần 30h. Private dataset tạo thành công/ready; model source riêng có đúng GGUF output. Notebook đổi mount/account, giữ worker, prompt, threshold và runtime; preflight ZIP/manifest/census/cell syntax pass. V1 submit 23:00 GMT+7, source readback khớp/private/T4. Theo chỉ đạo push lại khi queue, V2 submit 23:10; latest QUEUED, các request tiếp theo bị server từ chối do Maximum batch GPU session count of 2 reached. Không có session ID được API xác nhận để cancel; không đoán ID, không tuyên bố các phiên cũ đã hủy hay runtime đã pass.

Tài liệu ma trận/status và CHANGES được cập nhật. Kiểm tra audit scope/binding tám invariant PASS; các bộ integrity/probe/statistics bắt buộc chạy trước commit. ZIP input, credentials và output lớn giữ ngoài Git; publish receipt, source/pin và bằng chứng audit cần thiết.
