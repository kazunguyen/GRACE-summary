# Dry-run toàn validation — 02/11/2026

**Kết luận sau đối chiếu nguồn: 28/28 tập đạt audit tự động; 0 lỗi dựng, 0 cờ nhãn chưa giải quyết trong phạm vi kiểm tra.** Bộ dò ban đầu ghi 27 pass và 1 needs_review; giữ nguyên số liệu gốc trong summary.json/audit_summary.json. Đọc [final_status.json](final_status.json) và [leak_review.json](leak_review.json) để xem kết luận cuối.

Đã dựng 70.070 dòng prompt trên đủ 2.732 Devign và 2.273 REVEAL validation cho các arm đủ dữ liệu. Không inference LLM, không tạo score, không fit tau.
H2 và bốn arm B3 giữ trạng thái blocked vì thiếu evidence/cặp demo. Giữ target thiếu graph ở B1-shuf với graph trống và cờ missing theo xác nhận người dùng.
Phiên donor frozen thống nhất. B0/B1 và các probe graph giữ scaffold demo trống; không thay prompt/output lịch sử. Prefix graph tái dùng cache đã kiểm hash và tái dựng chính xác; full/shuffle được dựng thật từ graph nguồn.

| Dataset | Arm | Seed | Dựng/đủ | Demo rỗng | Graph thiếu | Cờ nhãn trước đối chiếu nguồn | Lỗi dựng | Trạng thái bộ dò ban đầu |
|---|---|---:|---:|---:|---:|---:|---:|---|
| devign | B0 | 42 | 2732/2732 | 0.000% | 0.000% | 0 | 0 | pass |
| devign | B1 | 42 | 2732/2732 | 0.000% | 0.110% | 0 | 0 | pass |
| devign | B1-full | 42 | 2732/2732 | 0.000% | 0.110% | 0 | 0 | pass |
| devign | B1-shuf | 42 | 2732/2732 | 0.000% | 0.110% | 0 | 0 | pass |
| devign | B1-shuf | 43 | 2732/2732 | 0.000% | 0.110% | 0 | 0 | pass |
| devign | B1-shuf | 44 | 2732/2732 | 0.000% | 0.110% | 0 | 0 | pass |
| devign | B2 | 42 | 2732/2732 | 0.549% | 0.110% | 0 | 0 | pass |
| devign | B2-rand | 42 | 2732/2732 | 0.549% | 0.110% | 0 | 0 | pass |
| devign | B2-rand | 43 | 2732/2732 | 0.695% | 0.110% | 0 | 0 | pass |
| devign | B2-rand | 44 | 2732/2732 | 0.878% | 0.110% | 0 | 0 | pass |
| devign | B2-nolabel | 42 | 2732/2732 | 0.549% | 0.110% | 0 | 0 | pass |
| devign | B2-labelonly | 42 | 2732/2732 | 0.000% | 0.110% | 0 | 0 | pass |
| devign | B2-flip | 42 | 2732/2732 | 0.549% | 0.110% | 0 | 0 | pass |
| devign | B2-rep | 42 | 2732/2732 | 0.549% | 0.110% | 0 | 0 | pass |
| reveal | B0 | 42 | 2273/2273 | 0.000% | 0.000% | 0 | 0 | pass |
| reveal | B1 | 42 | 2273/2273 | 0.000% | 1.188% | 0 | 0 | pass |
| reveal | B1-full | 42 | 2273/2273 | 0.000% | 1.188% | 0 | 0 | pass |
| reveal | B1-shuf | 42 | 2273/2273 | 0.000% | 1.188% | 0 | 0 | pass |
| reveal | B1-shuf | 43 | 2273/2273 | 0.000% | 1.188% | 0 | 0 | pass |
| reveal | B1-shuf | 44 | 2273/2273 | 0.000% | 1.188% | 1 | 0 | needs_review |
| reveal | B2 | 42 | 2273/2273 | 0.264% | 1.188% | 0 | 0 | pass |
| reveal | B2-rand | 42 | 2273/2273 | 0.616% | 1.188% | 0 | 0 | pass |
| reveal | B2-rand | 43 | 2273/2273 | 0.572% | 1.188% | 0 | 0 | pass |
| reveal | B2-rand | 44 | 2273/2273 | 0.308% | 1.188% | 0 | 0 | pass |
| reveal | B2-nolabel | 42 | 2273/2273 | 0.264% | 1.188% | 0 | 0 | pass |
| reveal | B2-labelonly | 42 | 2273/2273 | 0.000% | 1.188% | 0 | 0 | pass |
| reveal | B2-flip | 42 | 2273/2273 | 0.264% | 1.188% | 0 | 0 | pass |
| reveal | B2-rep | 42 | 2273/2273 | 0.264% | 1.188% | 0 | 0 | pass |

B1-full và B1-shuf có same_prompt_as_B1 trong summary; mọi prompt trùng được giữ và báo; không coi đã tạo khác biệt khi prompt giống nhau.

**Chưa hoàn thành toàn bộ Bước 3:** còn 5 arm blocked và hai người đọc mẫu chưa có kết quả. Lượt này là dry-run chuẩn bị cho tương lai, không thay audit trước inference của run lịch sử.

[Summary](summary.json), [arm blocked](blocked_arms.json), [lỗi dựng](render_errors.json), [nguồn/hash](source_hashes.json), [60 mẫu chấm](manual_packet.md), [rubric](RUBRIC.md).

## Cảnh báo nhầm có bằng chứng nguồn

B1-shuf REVEAL seed 44, target reveal:validation:1629: bộ dò thấy Label: trong node donor reveal:train:664, CALL 30064771247. Node hiển thị bị cắt ở 40 ký tự, làm mất phần còn lại của chuỗi định dạng trường giao thức. Code node nguyên bản:

~~~c
proto_item_append_text ( item , " Label: \"%s\"" , label )
~~~

Đã kiểm node/câu lệnh này tồn tại trong function donor frozen và tái tạo đúng dòng graph ở offset cảnh báo. Đây là chuỗi hiển thị trường giao thức, không chèn đáp án target. Giữ nguyên raw_label_flags.json, audit_rows.csv và summary ban đầu; [đối chiếu nguồn](source_context_resolution.json) và [kiểm độc lập](verification.json) lưu bằng chứng.

## Kiểm tra bàn giao và cờ từng mẫu

Đã kiểm độc lập hash 70.070 prompt, ID validation chính thức, budget code/graph/demo/context, graph donor frozen và dung sai kích thước B1-shuf. Threshold và snapshot niêm phong giữ nguyên hash. Test probe: 20 passed; test bộ chạy: 4 passed. Các test này không thay nghiệm thu GPU hoặc sửa lỗi tích hợp helper B2 đã ghi trong tiến độ chung.

[review_flags.csv](review_flags.csv) có 562 dòng: 176 dòng gắn cờ demo và 390 dòng thiếu graph; hai loại có thể giao nhau. 390 dòng thiếu graph là 30 target lặp lại trên 13 tổ hợp arm/seed có graph. 30 target thiếu graph được giữ ở cả ba seed B1-shuf thành 90 dòng graph trống có cờ. Mỗi tập đều đạt demo rỗng ≤1%; cờ từng mẫu vẫn được giữ.

## Token và tỷ lệ cắt

| Dataset | Arm | Seed | Token p50 | Token p95 | Max | Cắt code | Cắt graph | Cắt demo |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| devign | B0 | 42 | 365.0 | 2072.6 | 3100 | 2.196% | 0.000% | 0.000% |
| devign | B1 | 42 | 1820.0 | 3410.0 | 4579 | 2.196% | 92.753% | 0.000% |
| devign | B1-full | 42 | 1746.5 | 3336.4 | 4576 | 2.196% | 92.753% | 0.000% |
| devign | B1-shuf | 42 | 1817.5 | 3412.2 | 4579 | 2.196% | 92.716% | 0.000% |
| devign | B1-shuf | 43 | 1821.0 | 3448.0 | 4575 | 2.196% | 93.631% | 0.000% |
| devign | B1-shuf | 44 | 1822.0 | 3425.6 | 4578 | 2.196% | 93.082% | 0.000% |
| devign | B2 | 42 | 2086.5 | 4827.3 | 6080 | 2.196% | 92.753% | 7.321% |
| devign | B2-rand | 42 | 2235.0 | 4038.8 | 6078 | 2.196% | 92.753% | 8.346% |
| devign | B2-rand | 43 | 2261.0 | 3955.3 | 6061 | 2.196% | 92.753% | 8.236% |
| devign | B2-rand | 44 | 2253.0 | 4001.7 | 6079 | 2.196% | 92.753% | 7.943% |
| devign | B2-nolabel | 42 | 2081.5 | 4821.8 | 6074 | 2.196% | 92.753% | 7.321% |
| devign | B2-labelonly | 42 | 1821.5 | 3412.0 | 4580 | 2.196% | 92.753% | 0.000% |
| devign | B2-flip | 42 | 2087.5 | 4827.4 | 6080 | 2.196% | 92.753% | 7.321% |
| devign | B2-rep | 42 | 2086.5 | 4827.3 | 6080 | 2.196% | 92.753% | 7.321% |
| reveal | B0 | 42 | 262.0 | 1570.4 | 3100 | 1.496% | 0.000% | 0.000% |
| reveal | B1 | 42 | 1717.0 | 2922.6 | 4578 | 1.496% | 92.961% | 0.000% |
| reveal | B1-full | 42 | 1666.0 | 2843.8 | 4566 | 1.496% | 92.961% | 0.000% |
| reveal | B1-shuf | 42 | 1716.0 | 2982.6 | 4578 | 1.496% | 93.621% | 0.000% |
| reveal | B1-shuf | 43 | 1717.0 | 2934.2 | 4576 | 1.496% | 93.577% | 0.000% |
| reveal | B1-shuf | 44 | 1718.0 | 2946.6 | 4576 | 1.496% | 93.929% | 0.000% |
| reveal | B2 | 42 | 1873.0 | 3959.4 | 6080 | 1.496% | 92.961% | 3.256% |
| reveal | B2-rand | 42 | 1990.0 | 3411.2 | 5499 | 1.496% | 92.961% | 4.399% |
| reveal | B2-rand | 43 | 1993.0 | 3464.4 | 6026 | 1.496% | 92.961% | 4.443% |
| reveal | B2-rand | 44 | 1999.0 | 3479.2 | 6068 | 1.496% | 92.961% | 4.267% |
| reveal | B2-nolabel | 42 | 1867.0 | 3954.0 | 6074 | 1.496% | 92.961% | 3.256% |
| reveal | B2-labelonly | 42 | 1719.0 | 2924.6 | 4580 | 1.496% | 92.961% | 0.000% |
| reveal | B2-flip | 42 | 1872.0 | 3959.6 | 6079 | 1.496% | 92.961% | 3.256% |
| reveal | B2-rep | 42 | 1873.0 | 3959.4 | 6080 | 1.496% | 92.961% | 3.256% |

## Điều kiện Bước 3 còn thiếu

- B1-H2: evidence và bằng chứng giới hạn nguồn graph ≤40 node/80 edge.
- B3/B3-nodiff/B3-swap/B3-flip: cặp demo; Key difference cho các biến thể cần khối này. Giữ blocked, không tạo prompt giả.
- Dry-run/audit đủ 15 arm sau khi có các đầu vào trên.
- Hai người đọc độc lập, điền phiếu thật và lập biên bản phân xử. [60 mẫu phiên này](manual_packet.md), [rubric](RUBRIC.md), [người 1](reviewer_1.csv), [người 2](reviewer_2.csv) chưa có chấm thực tế.

[Lượt thread dở](../dry_run_validation_20261102_interrupted_threads/ATTEMPT_STATUS.json) được lưu riêng và không cộng vào kết quả hoàn tất. Không gọi LLM, không tính tau hoặc đổi run lịch sử.
