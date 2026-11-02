# B1 — bước 3: hậu kiểm sau inference

Trạng thái: **kiểm tra máy hoàn tất trong phạm vi dưới đây; chờ hai người chấm và nghiệm thu**. Không phải bằng chứng audit trước LLM. Không thay báo cáo audit nghiên cứu toàn bộ 15 arm.

Đã kiểm từng ID, label, hash prompt, nội dung scaffold rỗng, 2 logprob và score, tính toàn vẹn checkpoint, đối chiếu bốn tập prompt với hash đã audit bằng tokenizer pin, và so record lượt cha. Tất cả 10.011 ID khớp; 0 trường hợp demo/scaffold sai, 0 score/logprob sai; 5 raw response không hợp lệ, 0 score không hợp lệ. Chi tiết, hash và thống kê từng split trong `b1_posthoc_audit.json`.

Audit payload, token, graph và regex trước đó nằm ở [prompt audit](../prompt_audit_20261102/KET_QUA.md); các cờ nhãn đã được phân loại theo ngữ cảnh. Không diễn giải regex/metadata là bằng chứng tuyệt đối không có rò rỉ ngữ nghĩa. Graph thiếu đã gắn cờ: Devign val 3, test 2; REVEAL val 27, test 23. B1 không dùng demo, không áp ngưỡng demo rỗng như lỗi.

Đã chuẩn bị `manual_packet_b1.md`, `manual_sample_b1.jsonl`, hai phiếu độc lập để trống. Đây là bộ riêng B1; không thay packet toàn nghiên cứu. Cần hai người thật đánh giá, biên bản bất đồng/phân xử và quyết định nghiệm thu. Thiếu audit trước inference không thể khắc phục hồi tố.
