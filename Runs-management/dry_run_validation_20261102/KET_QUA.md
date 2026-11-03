# Dry-run toàn validation — 02/11/2026

Đã dựng 95,095 prompt trên đủ 2.732 Devign và 2.273 REVEAL validation cho cả 15 arm chẩn đoán. Không inference LLM, không tạo score, không fit tau.
Trạng thái 15 arm: 15/15 arm hoàn tất. 0 rò rỉ nhãn, 0 lỗi dựng. Khối CPG và contrastive pair bảo toàn chuẩn hóa thứ tự.
Phiên donor frozen thống nhất. B0/B1 và các probe graph giữ scaffold demo trống; không thay prompt/output lịch sử. Prefix graph tái dùng cache đã kiểm hash và tái dựng chính xác; full/shuffle được dựng thật từ graph nguồn.

| Dataset | Arm | Seed | Dựng/đủ | Demo rỗng | Graph thiếu | Cờ nhãn chưa giải quyết | Lỗi dựng | Trạng thái |
|---|---|---:|---:|---:|---:|---:|---:|---|
| devign | B0 | 42 | 2732/2732 | 0.000% | 0.000% | 0 | 0 | pass |
| devign | B1 | 42 | 2732/2732 | 0.000% | 0.110% | 0 | 0 | pass |
| devign | B1-full | 42 | 2732/2732 | 0.000% | 0.110% | 0 | 0 | pass |
| devign | B1-shuf | 42 | 2732/2732 | 0.000% | 0.110% | 0 | 0 | pass |
| devign | B1-shuf | 43 | 2732/2732 | 0.000% | 0.110% | 0 | 0 | pass |
| devign | B1-shuf | 44 | 2732/2732 | 0.000% | 0.110% | 0 | 0 | pass |
| devign | B1-H2 | 42 | 2732/2732 | 0.000% | 0.000% | 0 | 0 | pass |
| devign | B2 | 42 | 2732/2732 | 0.549% | 0.110% | 0 | 0 | pass |
| devign | B2-rand | 42 | 2732/2732 | 0.549% | 0.110% | 0 | 0 | pass |
| devign | B2-rand | 43 | 2732/2732 | 0.695% | 0.110% | 0 | 0 | pass |
| devign | B2-rand | 44 | 2732/2732 | 0.878% | 0.110% | 0 | 0 | pass |
| devign | B2-nolabel | 42 | 2732/2732 | 0.549% | 0.110% | 0 | 0 | pass |
| devign | B2-labelonly | 42 | 2732/2732 | 0.000% | 0.110% | 0 | 0 | pass |
| devign | B2-flip | 42 | 2732/2732 | 0.549% | 0.110% | 0 | 0 | pass |
| devign | B2-rep | 42 | 2732/2732 | 0.549% | 0.110% | 0 | 0 | pass |
| devign | B3 | 42 | 2732/2732 | 0.732% | 0.110% | 0 | 0 | pass |
| devign | B3-nodiff | 42 | 2732/2732 | 0.732% | 0.110% | 0 | 0 | pass |
| devign | B3-swap | 42 | 2732/2732 | 0.732% | 0.110% | 0 | 0 | pass |
| devign | B3-flip | 42 | 2732/2732 | 0.732% | 0.110% | 0 | 0 | pass |
| reveal | B0 | 42 | 2273/2273 | 0.000% | 0.000% | 0 | 0 | pass |
| reveal | B1 | 42 | 2273/2273 | 0.000% | 1.188% | 0 | 0 | pass |
| reveal | B1-full | 42 | 2273/2273 | 0.000% | 1.188% | 0 | 0 | pass |
| reveal | B1-shuf | 42 | 2273/2273 | 0.000% | 1.188% | 0 | 0 | pass |
| reveal | B1-shuf | 43 | 2273/2273 | 0.000% | 1.188% | 0 | 0 | pass |
| reveal | B1-shuf | 44 | 2273/2273 | 0.000% | 1.188% | 0 | 0 | pass |
| reveal | B1-H2 | 42 | 2273/2273 | 0.000% | 0.000% | 0 | 0 | pass |
| reveal | B2 | 42 | 2273/2273 | 0.264% | 1.188% | 0 | 0 | pass |
| reveal | B2-rand | 42 | 2273/2273 | 0.616% | 1.188% | 0 | 0 | pass |
| reveal | B2-rand | 43 | 2273/2273 | 0.572% | 1.188% | 0 | 0 | pass |
| reveal | B2-rand | 44 | 2273/2273 | 0.308% | 1.188% | 0 | 0 | pass |
| reveal | B2-nolabel | 42 | 2273/2273 | 0.264% | 1.188% | 0 | 0 | pass |
| reveal | B2-labelonly | 42 | 2273/2273 | 0.000% | 1.188% | 0 | 0 | pass |
| reveal | B2-flip | 42 | 2273/2273 | 0.264% | 1.188% | 0 | 0 | pass |
| reveal | B2-rep | 42 | 2273/2273 | 0.264% | 1.188% | 0 | 0 | pass |
| reveal | B3 | 42 | 2273/2273 | 0.308% | 1.188% | 0 | 0 | pass |
| reveal | B3-nodiff | 42 | 2273/2273 | 0.308% | 1.188% | 0 | 0 | pass |
| reveal | B3-swap | 42 | 2273/2273 | 0.308% | 1.188% | 0 | 0 | pass |
| reveal | B3-flip | 42 | 2273/2273 | 0.308% | 1.188% | 0 | 0 | pass |

B1-full và B1-shuf có same_prompt_as_B1 trong summary; trùng do graph nhỏ/thiếu hoặc cùng trần 40/80 được báo, không coi đã tạo khác biệt khi prompt giống nhau.

**Bước 3 ĐÃ HOÀN THÀNH TOÀN DIỆN 15/15 ARM:** 95.095 prompt đạt kiểm toán 0 label leak, token trong ngân sách 8.192, 0 LLM call.

[Summary](summary.json), [arm blocked](blocked_arms.json), [lỗi dựng](render_errors.json), [nguồn/hash](source_hashes.json), [60 mẫu chấm](manual_packet.md), [rubric](RUBRIC.md).
