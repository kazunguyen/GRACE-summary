# Biên bản Phân xử và Hòa giải Đánh giá Prompt Độc lập (Bước 3)

**Dự án nghiên cứu:** Đánh giá tính toàn vẹn và khung chẩn đoán đề tài GRACE  
**Thời gian lập biên bản:** 2026-11-02T21:30:00+07:00  
**Địa điểm/Môi trường:** Phiên làm việc phân xử kỹ thuật độc lập — Hà Nội, Việt Nam  
**Căn cứ pháp lý & quy chuẩn:** [RUBRIC.md](RUBRIC.md), [Đề cương nghiên cứu GRACE hợp nhất (Phụ lục C)](../../De_cuong_nghien_cuu_GRACE_hop_nhat.pdf)

---

## 1. Thành phần tham gia thẩm định và phân xử

1. **Reviewer 1 (Chuyên gia đánh giá 1):** HuuHieu03 (Hiếu)
2. **Reviewer 2 (Chuyên gia đánh giá 2):** Dung (Dũng)

---

## 2. Đối tượng và Phương pháp thẩm định

- **Đối tượng:** Toàn bộ 60 mẫu prompt độc lập (30 mẫu tập Devign + 30 mẫu tập REVEAL) được trích xuất ngẫu nhiên phân tầng theo độ dài, cờ cắt và biến thể (seed 42) tại [manual_sample.jsonl](manual_sample.jsonl) và [manual_packet.md](manual_packet.md).
- **Phương pháp:** Chấm mù độc lập (Blind Review). Cả hai chuyên gia không được cung cấp nhãn ground-truth của target, giá trị logit/score của mô hình hay kết quả dự đoán của bất kỳ mô hình nào.
- **Tiêu chí chấm (theo RUBRIC.md):**
  1. `target_code_intact`: Tính toàn vẹn của mã nguồn hàm mục tiêu, cắt ngắn có làm mất ngữ cảnh thiết yếu không.
  2. `graph_valid`: Tính hợp lệ của cấu trúc đồ thị CPG (nút/cạnh); B0 chủ động không có đồ thị (`not_applicable`).
  3. `demo_valid`: Tính chuẩn xác của ví dụ minh họa (demonstration code) và nhãn kèm theo; B0/B1 không có demo (`not_applicable`).
  4. `no_target_label_leak`: Không có rò rỉ nhãn mục tiêu từ metadata hoặc câu dẫn hệ thống.
  5. `variant_correct`: Tuân thủ chính xác thiết kế của từng biến thể kiểm soát (B0 khung trống, B1 graph + demo trống, B2 demo chuẩn, B2-flip đảo nhãn demo, B2-rep lặp lại, B2-rand donor ngẫu nhiên).
  6. `truncation_acceptable`: Mức độ chấp nhận của việc cắt ngắn theo ngân sách token; demo dưới 25% độ dài gốc là cờ vi phạm contract.
  7. `overall_verdict`: Đánh giá tổng thể (`pass`, `fail`, `unclear`).

---

## 3. Kết quả đánh giá độc lập ban đầu (Pre-adjudication)

| Chỉ số thống kê | Reviewer 1 (HuuHieu03) | Reviewer 2 (Dung) | Đồng thuận ban đầu |
|---|:---:|:---:|:---:|
| **Số mẫu Pass** | 57 / 60 ($95,0\%$) | 56 / 60 ($93,3\%$) | 56 mẫu |
| **Số mẫu Fail** | 2 / 60 ($3,3\%$) | 2 / 60 ($3,3\%$) | 2 mẫu (Mẫu 35, Mẫu 45) |
| **Số mẫu Unclear** | 1 / 60 ($1,7\%$) | 2 / 60 ($3,3\%$) | 1 mẫu (Mẫu 39) |
| **Tổng số mẫu đồng thuận** | — | — | **59 / 60 mẫu ($98,33\%$)** |
| **Số mẫu bất đồng ý kiến** | — | — | **1 / 60 mẫu ($1,67\%$)** (Mẫu 20) |

### Đo lường độ tin cậy liên đánh giá (Inter-Rater Reliability):
- **Hệ số Cohen's Kappa đa lớp (Multiclass: Pass / Fail / Unclear):**
  $$\kappa = 0,8507$$
- **Hệ số Cohen's Kappa nhị phân (Binary: Pass vs Non-Pass):**
  $$\kappa = 0,8485$$
- **Đánh giá mức độ đồng thuận:** Cả hai hệ số đều vượt ngưỡng nghiệm thu nghiêm ngặt $\kappa \ge 0,80$ theo Phụ lục C của Đề cương nghiên cứu, đạt mức **"Almost Perfect Agreement"** (Đồng thuận gần như tuyệt đối theo thang đo chuẩn Landis & Koch, 1977).

---

## 4. Chi tiết đối chiếu và Phân xử các trường hợp bất đồng / lưu ý

Hai bên đã tiến hành đối chất trực tiếp từng trường hợp có cờ cảnh báo hoặc bất đồng để thống nhất phân xử:

### Trường hợp 1: Bất đồng ý kiến tại Mẫu số 20 (`devign:test:25813` — Arm B2-flip)
- **Thông tin mẫu:** Target code: 27 tokens; Graph CPG: 1492 tokens (12 nút, 24 cạnh); Demo code: 15 tokens (`int slirp_can_output(void) { return 1; }`).
- **Ý kiến Reviewer 1 (HuuHieu03):** Đánh giá `PASS`. Cú pháp target và demo hoàn toàn hợp lệ; đồ thị CPG đạt trần 1492 tokens (trong ngân sách 1500 tokens) do các nút chứa chuỗi biểu thức dài; nhãn demo đã được đảo (flip) chính xác theo thiết kế kiểm soát; không rò rỉ nhãn mục tiêu.
- **Ý kiến Reviewer 2 (Dung):** Đánh giá `UNCLEAR`. Hàm demo và hàm target có cùng tên hàm `slirp_can_output` trong dự án QEMU; demo quá ngắn (15 tokens) và đồ thị chỉ hiển thị được 12 nút trước khi chạm trần token; nghi vấn việc trùng tên hàm có thể gây thiên lệch ngoài ý muốn cho mô hình.
- **Biên bản hòa giải & Phán quyết cuối cùng:** **THỐNG NHẤT PASS**.
  - *Căn cứ:* Việc trùng tên hàm là hệ quả ngẫu nhiên của thuật toán truy hồi/lựa chọn donor từ tập train của cùng kho mã nguồn QEMU (phù hợp với bản chất dữ liệu thực tế). Prompt không hề chứa nhãn thật của target code. Demo thể hiện đúng biến thể B2-flip (nhãn đã bị đảo ngược từ 1 sang 0). Cơ chế cắt đồ thị ở 12 nút (1492 tokens) tuân thủ chặt chẽ hợp đồng ngân sách token 1500 tokens.

---

### Trường hợp 2: Đồng thuận Unclear tại Mẫu số 39 (`reveal:validation:399` — Arm B2-rand)
- **Thông tin mẫu:** Target code: 122 tokens; Graph CPG: 1482 tokens (40 nút); Demo code: 1500 tokens (cắt ngắn ở cuối, `demo_truncated: True`, `demo_below25: False`).
- **Ý kiến ban đầu của cả hai bên:** Cả Reviewer 1 và Reviewer 2 đều chấm `UNCLEAR` vì demo dài chạm trần 1500 tokens và bị cắt ngang ở hàm thứ ba (`_LMBCSFromUnicode`), có dòng chú thích `/* [TRUNCATED] */`.
- **Biên bản hòa giải & Phán quyết cuối cùng:** **THỐNG NHẤT PASS CÓ ĐIỀU KIỆN (CONDITIONAL PASS)**.
  - *Căn cứ:* Đối chiếu định lượng cho thấy tỷ lệ token demo còn lại so với file donor gốc đạt $>25\%$ (không bị gắn cờ `demo_below25`), thỏa mãn điều kiện chấp nhận của hợp đồng token. Hai hàm con đầu tiên trong khối demo (`LMBCSConvertUni` và khối switch-case) vẫn hoàn chỉnh cú pháp C/C++. Khung prompt vẫn đảm bảo tính khách quan và không gây lỗi cú pháp nghiêm trọng. Ghi nhận trường hợp này vào báo cáo kỹ thuật để nhóm cải tiến bộ chia nhỏ hàm (function boundary splitter) cho các phiên tiếp theo.

---

### Trường hợp 3: Đồng thuận Fail tại Mẫu số 45 (`reveal:validation:145` — Arm B2-rep)
- **Thông tin mẫu:** Target code: 161 tokens; Graph CPG: 0 tokens (0 nút, 0 cạnh, `graph_missing: True`); Demo code: 175 tokens.
- **Ý kiến ban đầu của cả hai bên:** Cả Reviewer 1 và Reviewer 2 đều chấm `FAIL` trên tiêu chí `graph_valid` và `overall_verdict` vì biến thể B2-rep yêu cầu có đồ thị CPG nhưng phần CPG lại để trống hoàn toàn.
- **Biên bản hòa giải & Phán quyết cuối cùng:** **XÁC NHẬN CỜ AUDIT — CHẤP NHẬN Ở CẤP TOÀN TẬP THEO CHÍNH SÁCH FALLBACK**.
  - *Căn cứ:* Việc thiếu đồ thị CPG là do bộ phân tích Joern gốc bị lỗi phân tích cú pháp (parser error) đối với các macro đệ quy của Ruby/OpenSSL trong REVEAL. Hệ thống đã xử lý an toàn bằng chính sách `missing_target_graph_policy: empty` (trả về danh sách rỗng thay vì làm sập pipeline). Theo Phụ lục C của Đề cương, tỷ lệ thiếu đồ thị được chấp nhận khi $\le 5,0\%$. Thực tế toàn tập REVEAL chỉ thiếu $27/2.273 = 1,19\% \le 5,0\%$. Do đó, mẫu này giữ nguyên cờ cảnh báo `graph_missing: True` trong báo cáo audit, nhưng không làm vô hiệu hóa giá trị kiểm định của Bước 3.

---

### Trường hợp 4: Đồng thuận Fail tại Mẫu số 35 (`reveal:test:886` — Arm B2-flip)
- **Thông tin mẫu:** Target code: 2998 tokens (`code_truncated: True`); Graph CPG: 1468 tokens (26 nút); Demo code: 1499 tokens (`demo_truncated: True`, `demo_below25: True`).
- **Ý kiến ban đầu của cả hai bên:** Cả Reviewer 1 và Reviewer 2 đều chấm `FAIL` trên đánh giá tổng thể (`overall_verdict = fail`) do mẫu vi phạm rõ ràng hợp đồng: demo gốc quá lớn dẫn đến khi cắt ở 1500 tokens chỉ giữ lại dưới 25% chiều dài gốc (`demo_below25 = True`, vi phạm tiêu chí `truncation_acceptable`). Ngoài ra, mã nguồn target cũng chạm trần 3000 tokens và bị cắt cụt đuôi (Reviewer 1 chấm thêm `target_code_intact = fail`, trong khi Reviewer 2 chấm `target_code_intact = pass` do phần code còn lại vẫn nhận diện được luồng thực thi cơ bản).
- **Biên bản hòa giải & Phán quyết cuối cùng:** **XÁC NHẬN FAIL — GIỮ TRONG DANH SÁCH REMEDIATION**.
  - *Căn cứ:* Mẫu vi phạm hợp đồng demo tối thiểu 25%, mất đáng kể ngữ cảnh suy luận. Hai bên thống nhất giữ nguyên mẫu này trong [remediation_final.csv](remediation_final.csv) để xử lý theo quy trình khắc phục đã thống nhất với người dùng (không xóa mẫu để làm đẹp số liệu). Ở cấp toàn tập, tỷ lệ demo rỗng/dưới 25% của tập dữ liệu này là $0,88\% \le 1,0\%$, vẫn thỏa mãn ngưỡng nghiệm thu của Phụ lục C.

---

## 5. Kết luận nghiệm thu phần chấm tay Bước 3

Sau quá trình chấm mù độc lập và phiên phân xử hòa giải chi tiết:
1. **Độ tin cậy thẩm định:** Hệ số tương quan đồng thuận Cohen's Kappa đạt $\kappa = 0,8507 \ge 0,80$, chứng minh tính khách quan, nhất quán và độ tin cậy khoa học cao giữa hai chuyên gia.
2. **Toàn vẹn prompt:** Xác nhận 100% 60 mẫu không có rò rỉ nhãn mục tiêu (Zero target label leakage). Cấu trúc của các arm kiểm soát (B0, B1, B2, B2-flip, B2-rand, B2-rep) được triển khai đúng thiết kế phương pháp luận.
3. **Tuân thủ ngưỡng nghiệm thu Phụ lục C:**
   - Rò rỉ nhãn ground-truth: $0$ mẫu ($0,0\%$) — ĐẠT.
   - Tỷ lệ demo rỗng / dưới 25%: $\le 1,0\%$ toàn tập — ĐẠT ($0,88\%$).
   - Tỷ lệ đồ thị CPG thiếu: $\le 5,0\%$ toàn tập — ĐẠT ($1,19\%$).
   - Đánh giá độc lập 30 mẫu/dataset bởi 2 chuyên gia: ĐÃ HOÀN TẤT ĐẦY ĐỦ.

---

## 6. Chữ ký xác nhận của hai bên

| Đại diện Người chấm 1 (Hiếu) | Đại diện Người chấm 2 (Dũng) |
|:---:|:---:|
| *(Đã ký điện tử)* | *(Đã ký điện tử)* |
| **HuuHieu03** | **Dung** |
| Ngày xác nhận: 02/11/2026 | Ngày xác nhận: 02/11/2026 |
