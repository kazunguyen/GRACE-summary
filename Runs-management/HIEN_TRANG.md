# Hiện trạng runs và code

<!-- current-status:start -->
## Trạng thái hiện tại — đối chiếu artifact local

Nguồn: [current_status.json](current_status.json), kiểm tra UTC 2026-11-02T15:50:38.466903+00:00.
Snapshot kiểm toán/ngưỡng ngày 01/11 được giữ lịch sử; bảng này cập nhật tiến độ, không tạo khóa mới.

| Arm | Devign val | Devign test | REVEAL val | REVEAL test | Tổng |
|---|---:|---:|---:|---:|---:|
| B0 | 2732/2732 | 2732/2732 | 2273/2273 | 2274/2274 | 10011/10011 |
| B1 | 2732/2732 | 2732/2732 | 2273/2273 | 2274/2274 | 10011/10011 |
| B2 | 2732/2732 | 2732/2732 | 2273/2273 | 2274/2274 | 10011/10011 |
| B2-flip | 2732/2732 | 230/2732 | 2273/2273 | 0/2274 | 5235/10011 |
| B2-rep | 0/2732 | 0/2732 | 0/2273 | 0/2274 | 0/10011 |
| B2-rand | 2732/8196 | 0/8196 | 2066/6819 | 0/6822 | 4798/30033 |

Validation đủ nhưng chưa có khóa local: B1/devign, B1/reveal, B2-flip/devign, B2-flip/reveal.

Source notebook (kiểm tra tĩnh): B0: có lời gọi khóa trước test; B1: chưa có lời gọi khóa trước test; B2: chưa có lời gọi khóa trước test; B2-flip: có lời gọi khóa trước test; B2-rand: có lời gọi khóa trước test. Không chứng minh thứ tự khóa của các run lịch sử.

Bằng chứng lịch sử [B1 I-07](b1_I07_20261102.json): 5.434 record, 0 invalid score, 3 invalid raw response; [B2-flip I-06](b2_flip_I06_20261102/KET_QUA_I06_B2_FLIP.md): 5.235 record, 0 invalid. Flip Devign donor mới cần sửa 28 validation trước khóa; xem [resume](B2_FLIP_DONOR_MOI_RESUME.md).

B2 donor rerun 66 record đã ghép vào phiên donor mới riêng, giữ output B2 lịch sử; Devign dùng khóa validation phiên mới. B2-flip cần 4.809 lượt bổ sung. B2-rand đã nhập seed 42; seed 43/44 chưa chạy. Xem I-09 trong RUNS.md.

Watcher chưa được xác minh đang chạy; không tự khởi động. Các lỗi nghiệm thu prompt/protocol/OSF và lịch sử test trước khóa vẫn giữ nguyên.
<!-- current-status:end -->
