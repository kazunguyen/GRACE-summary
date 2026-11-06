# Hiện trạng runs và code

<!-- current-status:start -->
## Trạng thái hiện tại — đối chiếu artifact local

Nguồn: [current_status.json](current_status.json), kiểm tra UTC 2026-11-05T09:36:32.991667+00:00.
Snapshot kiểm toán/ngưỡng ngày 01/11 được giữ lịch sử; bảng này cập nhật tiến độ, không tạo khóa mới.

| Arm | Devign val | Devign test | REVEAL val | REVEAL test | Tổng |
|---|---:|---:|---:|---:|---:|
| B0 | 2732/2732 | 2732/2732 | 2273/2273 | 2274/2274 | 10011/10011 |
| B1 | 2732/2732 | 2732/2732 | 2273/2273 | 2274/2274 | 10011/10011 |
| B2 | 2732/2732 | 2732/2732 | 2273/2273 | 2274/2274 | 10011/10011 |
| B2-flip | 2732/2732 | 2732/2732 | 2273/2273 | 2274/2274 | 10011/10011 |
| B2-rep | 0/2732 | 0/2732 | 0/2273 | 0/2274 | 0/10011 |
| B2-rand | 5464/8196 | 0/8196 | 2325/6819 | 0/6822 | 7789/30033 |

Validation đủ nhưng chưa có khóa local: Không có.

Source notebook (kiểm tra tĩnh): B0: có lời gọi khóa trước test; B1: có lời gọi khóa trước test; B2: có lời gọi khóa trước test; B2-flip: có lời gọi khóa trước test; B2-rand: chưa có lời gọi khóa trước test. Không chứng minh thứ tự khóa của các run lịch sử.

Bằng chứng lịch sử [B1 I-07](b1_I07_20261102.json): 5.434 record, 0 invalid score, 3 invalid raw response; [B2-flip I-06](b2_flip_I06_20261102/KET_QUA_I06_B2_FLIP.md): 5.235 record. Run I-10 đã hoàn tất B2-flip donor mới đủ 10.011/10.011; ngưỡng kế thừa B2 là Devign 0,70 và ReVeal 0,12. B2 donor rerun 66 record thuộc B2, giữ lịch sử B2 riêng.

Run I-11 B2-rand chỉ chạy validation: seed 42 đủ 5.005/5.005; seed 43 được 2.784/5.005; seed 44 chưa chạy. Tổng 7.789/15.015 validation, chưa fit ngưỡng và chưa chạy test. Xem hai run mới trong RUNS.md.

Watcher chưa được xác minh đang chạy; không tự khởi động. Các lỗi nghiệm thu prompt/protocol/OSF và lịch sử test trước khóa vẫn giữ nguyên.
<!-- current-status:end -->
