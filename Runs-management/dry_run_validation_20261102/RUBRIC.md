# Hướng dẫn hai người đọc prompt độc lập

Trạng thái: CHƯA CHẤM. Hai phiếu còn trống; không thay thế đánh giá thực tế.
Mỗi người tự đọc cùng 60 prompt (30/dataset), điền phiếu riêng trước khi trao đổi. Không dùng score, metric hay nhãn target để chấm hoặc đổi mẫu. Sau khi nộp, đối chiếu bất đồng và lập biên bản phân xử, giữ phiếu gốc.

Mỗi tiêu chí điền pass / fail / unclear / not_applicable. Với fail/unclear, ghi vị trí và lý do cụ thể; điền tên người đọc, thời điểm thật và overall_verdict.

- target_code_intact: đúng function target, phần giữ lại có thể hiểu; cắt code đúng marker và giới hạn đã định.
- graph_valid: B0 không dùng graph là not_applicable; các arm còn lại phải đúng chính sách graph. B1-shuf cố ý dùng graph donor khác target, có provenance và ghép kích thước, không chấm sai chỉ vì graph khác target. Target thiếu graph được giữ graph trống và cờ missing theo quyết định người dùng; không tự tạo graph thay thế. B1-full dùng fill trong cùng trần 40 node/80 edge và 1.500 token.
- demo_valid: B0/B1/B1-full/B1-shuf không có demo nội dung; scaffold trống là chủ ý. B2/B2-rep có một demo retrieved; B2-rand dùng donor ngẫu nhiên frozen theo seed; B2-nolabel có code demo, không hiện nhãn demo; B2-labelonly chỉ có câu nhãn, không code demo. B2-flip cố ý đảo nhãn demo. Đánh giá theo đúng biến thể, không ép mọi arm giống B2.
- no_target_label_leak: không có đáp án target chèn từ metadata. Nhãn demo đúng thiết kế và từ Label xuất hiện tự nhiên trong C/C++ không tự động là rò rỉ. Khi mơ hồ ghi unclear và trích đoạn; không tự loại cảnh báo.
- variant_correct: kiểm vai trò code/graph/demo, thứ tự và nhãn hiển thị theo các chính sách trên. B2-rep phải giống từng byte với B2 cùng phiên; dry-run không chứng minh đã inference repeat độc lập.
- truncation_acceptable: phần còn lại có ngữ cảnh hợp lý. Demo bị cắt dưới 25% độ dài gốc vẫn giữ cờ cần xem. Tiêu chí tự động ở cấp tập là tỷ lệ demo rỗng/nội dung dưới ngưỡng <=1%, không phải mọi prompt phải hết cờ; việc đạt tỷ lệ không thay đánh giá ngữ nghĩa của người đọc.
- overall_verdict: pass / fail / unclear, nêu rõ bất đồng hoặc phần thiếu bằng chứng.

Mẫu được chọn seed 42, bảo đảm mỗi arm/seed có đại diện, phân tầng độ dài và cờ cắt, bù đủ 30 mỗi dataset; không chọn theo metric. Các arm H2/B3 đang blocked không xuất hiện như prompt giả trong bộ mẫu.
