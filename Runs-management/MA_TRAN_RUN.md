# Ma trận quản lý run GRACE

Ma trận theo Phương án 2, Bước 5. Một run trong bảng là một tổ hợp **arm × seed × dataset × split**. Thực hiện trên Devign và REVEAL, với validation trước test; chọn và lưu ngưỡng trên validation trước khi chạy test. Sổ kết quả và bằng chứng từng lượt nằm tại [RUNS.md](RUNS.md).

Quy ước graph cho kế hoạch này: các arm có graph dùng tối đa **40 nút / 80 cạnh**, ngân sách graph tối đa **1.500 token**, theo [contract của baseline](../01_Author_Baseline_Unified/evaluation_contract.yaml). Số thực tế có thể thấp hơn do graph thiếu, graph nhỏ hoặc giới hạn token. Với graph xáo trộn áp dụng cùng giới hạn cho graph donor. Với B1-full và B1-H2, cần bảo đảm bộ dựng prompt thực sự áp dụng giới hạn này và cùng ngân sách trước khi chạy; đây là lựa chọn thống nhất với contract, khác mô tả prefix 25/25 trong PDF. Ghi nhận thay đổi giao thức trước lượt xác nhận.

| Tầng | Arm | Nội dung cấu hình | Graph dự kiến | Seed | Chú thích |
|---|---|---|---|---|---|
| 1 | B0 | Chỉ code target mang dữ liệu; giữ câu dẫn/khung B2, để trống node/edge, mã và nhãn demo theo yêu cầu ngày 01/11/2026. | Không có payload graph; giữ câu dẫn | 42 | Biến thể b0_b2_empty_blocks_v1, khác B0 bỏ hẳn khối trong PDF. Hai notebook tại [02_Arm_B0_Source_Only](../02_Arm_B0_Source_Only/README.md); đã nhập output Kaggle: devign validation: 2732 (complete); devign test: 2732 (complete); reveal validation: 2273 (complete); reveal test: 2274 (complete); xem I-03 trong RUNS.md. |
| 1 | B1 | B0 + CPG của target; giữ câu dẫn demo trống theo cùng scaffold B0, không mã/nhãn demo. | Prefix tối đa 40 nút / 80 cạnh; tối đa 1.500 token | 42 | Notebook prompt tại [03_Arm_B1_Graph_Only](../03_Arm_B1_Graph_Only/README.md); dùng graph cache specs B2; đã có notebook inference Kaggle B1, chưa xác nhận run thật. |
| 1 | B2 | B1 + một demo truy hồi từ train, kèm nhãn thật của demo. Mốc GRACE đầy đủ. | Prefix tối đa 40 nút / 80 cạnh; tối đa 1.500 token | 42 | |
| 1 | B2-flip | Như B2, đảo nhãn demo. Đo độ nhạy với nhãn demo. | Prefix tối đa 40 nút / 80 cạnh; tối đa 1.500 token | 42 | Notebook prompt tại [04_Arm_B2_Flip](../04_Arm_B2_Flip/README.md); cùng demo/graph của B2 tham chiếu. Chưa tạo notebook inference. |
| 1 | B2-rep | Gọi lại cùng prompt B2 để đo biến động tự nhiên. | Prefix tối đa 40 nút / 80 cạnh; tối đa 1.500 token | 42 | Notebook prompt tại [05_Arm_B2_Rep](../05_Arm_B2_Rep/README.md); prompt phải giống B2 từng ký tự. Khi inference phải gọi mới backend, không dùng response cache B2. |
| 2 | B2-rand | Như B2, thay demo truy hồi bằng demo donor ngẫu nhiên kèm nhãn thật. | Prefix tối đa 40 nút / 80 cạnh; tối đa 1.500 token | 42, 43, 44 | |
| 2 | B2-nolabel | Như B2, giữ mã demo nhưng bỏ nhãn demo. | Prefix tối đa 40 nút / 80 cạnh; tối đa 1.500 token | 42 | |
| 2 | B2-labelonly | Như B2, bỏ mã demo, chỉ giữ câu gợi ý nhãn của hàm tương tự. | Prefix tối đa 40 nút / 80 cạnh; tối đa 1.500 token | 42 | |
| 2 | B1-shuf | Như B1, thay graph target bằng graph của hàm donor khác có số nút gần tương đương (±10%). | Graph donor tối đa 40 nút / 80 cạnh; tối đa 1.500 token | 42, 43, 44 | |
| 3 | B1-full | B0 + CPG target, tìm prefix nút lớn nhất vừa ngân sách, giữ cạnh nội bộ trong trần 80. | Tối đa 40 nút / 80 cạnh và 1.500 token | 42 | Đã áp trần trong renderer. Có thể trùng B1 khi graph vừa ngân sách; notebook cần báo tỷ lệ trùng prompt. |
| 3 | B1-H2 | B0 + graph đóng gói thành cụm evidence H2. | Graph nguồn tối đa 40 nút / 80 cạnh; evidence tối đa 1.500 token | 42 | Renderer yêu cầu h2_source_limits; notebook tạo evidence và kiểm chứng graph nguồn sẽ làm sau. |
| 3 | B3 | B1 + hai demo tương phản: một vulnerable, một safe, kèm mô tả khác biệt. | Prefix tối đa 40 nút / 80 cạnh; tối đa 1.500 token | 42 | |
| 3 | B3-nodiff | Như B3, bỏ khối mô tả khác biệt giữa hai demo. | Prefix tối đa 40 nút / 80 cạnh; tối đa 1.500 token | 42 | |
| 3 | B3-swap | Như B3, đảo thứ tự hai demo để đo thiên lệch vị trí. | Prefix tối đa 40 nút / 80 cạnh; tối đa 1.500 token | 42 | |
| 3 | B3-flip | Như B3, đảo nhãn cả hai demo, kể cả nhãn trong mô tả khác biệt. | Prefix tối đa 40 nút / 80 cạnh; tối đa 1.500 token | 42 | |

Tổng cộng **15 arm, 19 tổ hợp arm–seed** cho mỗi dataset và split. Nếu chạy cả hai dataset và hai split thì có **76 run**; số prompt phụ thuộc số mẫu validation thực tế. Seed 42 là lượt chính; 43 và 44 dành cho hai arm ngẫu nhiên. Các mốc SUP và phân tích P-PRE/P-POST được tính riêng, không phải arm gọi LLM trong bảng này.
