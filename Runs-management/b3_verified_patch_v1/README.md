# B3 — điểm bắt đầu hiện hành

Đọc [trạng thái B3 hiện tại](../../docs/B3_CURRENT_STATUS_20261108.md) trước khi chạy bất kỳ notebook nào.

- Devign dùng `release_20261108_v6`; REVEAL dùng `release_20261108_v7_reveal`, cùng method/runtime. Hai pool đã được người thật duyệt; full validation prompts2.732/2.273 và CPU integration đạt.
- Native GPU acceptance và validation inference mới **chưa chạy**. Quota huuhieu3333 lần kiểm gần nhất không đủ request9h; kiểm lại trước launch. Chưa có τ* mới hay test mới.
- Latest detailed acceptance: `v7_reveal_acceptance_20261108/DUAL_DATASET_READINESS.md`; two-input identity: `experiment_index.json` cùng thư mục.
- `release_20261108`…`v5` và các audit/remediation trước là **lịch sử**. Có release từng chứa review tự sinh không hợp lệ hoặc delivery lỗi; giữ để kiểm toán, không dùng như pool/runtime đang được chấp nhận. Dùng `b3_step6_packet_tool.py` hoặc admission tool với final forms thật; không dùng script historical `b3_step6_dual_review.py` để tạo quyết định người thật.
- ZIP prompt tổng là local-only tại `Runs-management/local_deliveries/`; hash/counts có trong `B3_PROMPT_HANDOFF_MANIFEST_20261108.json`. Hai ZIP input theo dataset trong release là launch artifacts riêng, không phải ZIP tổng bàn giao. Không mount cả hai roots vào một notebook yêu cầu một root.

Các tests integration yêu cầu frozen local assets/tokenizer đã có theo project setup; metadata hashes không thay thế quyền truy cập các nguồn dữ liệu đó. Không skip checks để che thiếu asset hoặc gate chưa đạt.
