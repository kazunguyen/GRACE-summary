# Đăng Ký Trước Giao Thức Nghiên Cứu (Preregistration Protocol v1)

- **Study ID:** `grace_diag_replication_v1`
- **Version:** `prereg-v1`
- **Registration Date:** 2026-10-31 (Cập nhật chuẩn hóa hoàn thiện Bước 4: 2026-11-02)
- **Repository Version / Git Tag:** `prereg-v1`
- **Protocol Configuration File:** [`01_Author_Baseline_Unified/diagnostic_kit/configs/protocol.yaml`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/01_Author_Baseline_Unified/diagnostic_kit/configs/protocol.yaml) & [`configs/protocol.yaml`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/configs/protocol.yaml)
- **Locked Thresholds File:** [`configs/thresholds.json`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/configs/thresholds.json) & [`configs/thresholds_flat.json`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/configs/thresholds_flat.json)
- **Tài liệu đề cương gốc:** [`00_Reports_and_Docs/PhuongAn2_De_cuong_nghien_cuu_GRACE_hop_nhat.pdf`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/00_Reports_and_Docs/PhuongAn2_De_cuong_nghien_cuu_GRACE_hop_nhat.pdf)

Ngày 2026-10-31 ở trên là ngày ghi trên tài liệu giao thức lịch sử, **không phải** thời điểm gửi hoặc được OSF phê duyệt. URL và thời điểm đăng ký OSF thực tế còn chờ bổ sung. Tag `prereg-v1` chỉ định danh một snapshot của repository, không chứng minh mọi quyết định đã có trước các lượt test kê dưới đây.

---

## 1. Công Bố Minh Bạch Về Tiếp Xúc Dữ Liệu Test (Test Exposure Disclosure & Ledger)

Tập dữ liệu kiểm thử (test set) của Devign và ReVeal đã từng được tiếp xúc trong giai đoạn thăm dò sơ bộ ban đầu (gồm 36 lượt chạy API thử nghiệm, tập dev-100, và các phép đo động cơ H1–H3). 

Bảng kê tiếp xúc bên dưới ghi lại các lượt suy luận test và việc xem metric thăm dò trước khi gửi OSF. Giao thức, prompt, arm và ngưỡng hiện tại được ghi lại cho công việc tiếp theo; tài liệu này **không khẳng định** mọi quyết định đã được khóa trước các lượt test lịch sử đó. Các giá trị ngưỡng trong `configs/thresholds.json` được chọn trên validation, nhưng chưa có bằng chứng việc khóa ngưỡng xảy ra trước mọi lượt test Tầng 1 hoặc B2-flip. Metric Tầng 1 đã xem là kết quả existing data ở mức following analysis, không phải kết quả xác nhận tiến cứu của lần đăng ký này. Mọi thay đổi và phân tích về sau phải ghi ngày, lý do trong `CHANGES_AFTER_PREREG.md`; chỉ gọi một phân tích là xác nhận tiến cứu khi chứng minh được nó chưa thực hiện tại thời điểm đăng ký OSF.

### 1.1. Khai Báo Mức Dữ Liệu Có Sẵn Trên OSF (OSF Existing Data Declarations)

Theo phân loại của Open Science Framework (OSF):
- **Registration following analysis of the data:** Áp dụng cho các arm Tầng 1 (B0, B1, B2) trên tập Test của Devign và ReVeal do các chỉ số thăm dò (MCC, AUROC) đã được tính toán trong giai đoạn thăm dò. Trong Bảng B của bài báo, các cặp so sánh này được ghi nhận rõ trạng thái "đã xem trước đăng ký".
- **Registration prior to analysis of the data:** Chỉ áp dụng cho từng phân tích test Tầng 2–3 và so sánh xác nhận thực sự chưa làm tại thời điểm gửi OSF, gồm các phân tích dự kiến Bảng B/D và chấm mù 2 người nếu lúc đó vẫn chưa thực hiện. Đây là phân loại theo phân tích: B2-rand đã chạy một phần validation, còn 230 nhãn raw của B2-flip Devign test đã được xem trước đăng ký và được đánh dấu chạy lại. Các tiếp xúc đó vẫn phải khai báo dù các so sánh dự kiến chưa được tính.

### 1.2. Bảng Kê Tiếp Xúc (Exposure Ledger) & Kiểm Toán 3 Điều Kiện Giữ / Chạy Lại

Thực hiện theo chỉ đạo của Cố vấn khoa học, nhóm nghiên cứu đã kiểm toán 3 điều kiện đối với các lượt chạy lịch sử:
- **Điều kiện 1 (Khớp giao thức):** Kiểm tra đối chiếu manifest của lượt cũ với `protocol.yaml`. Tất cả các lượt giữ lại đều dùng chung checkpoint `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf` (SHA-256 `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`), backend `llama-cpp-python 0.3.16`, context limit 8,192 tokens, và thứ tự prompt Hình 6 chuẩn mực.
- **Điều kiện 2 (Độ đầy đủ logprob và cận trên):** Toàn bộ record đều lưu logprob của token `0` và `1` để tính $s = \operatorname{sigmoid}(\operatorname{logit}_1 - \operatorname{logit}_0)$. Đối với các token vắng mặt trong top-k (nếu có), áp dụng cận trên bảo thủ $p \le p(\text{token thấp nhất trong top-}k)$ kèm cờ `s_bounded`, bảo đảm tỷ lệ bị chặn $< 1\%$.
- **Điều kiện 3 (Cách ly cache B2-rep):** Arm B2-rep chưa từng chạy trên GPU; khi thực thi bắt buộc bật `repeat: true` và `tag="repeat"` trong bộ chẩn đoán v1.1 để cô lập cache, bảo đảm không bao giờ nhận lại câu trả lời từ cache của B2.

| Arm | Dataset | Split | Lần Chạy Đầu (UTC) | Commit | Nội Dung Đã Xem | Khớp Giao Thức Khóa? | Hành Động |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **B0** | Devign | Val / Test | 2026-11-01T04:21:38Z | `7b045e7` | MCC, AUROC, CM | Có (`yes`) | Giữ nguyên (`keep`) |
| **B0** | ReVeal | Val / Test | 2026-11-01T04:21:38Z | `7b045e7` | MCC, AUROC, CM | Có (`yes`) | Giữ nguyên (`keep`) |
| **B1** | Devign | Val / Test | 2026-11-01T10:17:36Z | `0785f78` | MCC, AUROC | Có (`yes`) | Giữ nguyên (`keep`) |
| **B1** | ReVeal | Val / Test | 2026-11-01T10:17:36Z | `0785f78` | MCC, AUROC | Có (`yes`) | Giữ nguyên (`keep`) |
| **B2** | Devign | Val / Test | 2026-10-31T17:05:34Z | `8f48ea9` | MCC, AUROC, CM | Có (`yes`) | Giữ nguyên (`keep`) |
| **B2** | ReVeal | Val / Test | 2026-10-31T17:05:34Z | `8f48ea9` | MCC, AUROC, CM | Có (`yes`) | Giữ nguyên (`keep`) |
| **B2-flip** | Devign | Validation | 2026-11-01T14:46:02Z | `484b901` | Chưa xem (`none`) | Có (`yes`) | Giữ nguyên (`keep`) |
| **B2-flip** | Devign | Test | 2026-11-01T14:46:02Z | `484b901` | Nhãn thô 230 mẫu | Có (`yes`) | Chạy lại (`rerun`) |
| **B2-flip** | ReVeal | Validation | 2026-11-01T14:46:02Z | `484b901` | Chưa xem (`none`) | Có (`yes`) | Giữ nguyên (`keep`) |
| **B2-flip** | ReVeal | Test | Chưa chạy | Chưa có | Chưa xem (`none`) | Có (`yes`) | Giữ nguyên (`keep`) |
| **B2-rep** | Cả hai | Val / Test | Chưa chạy | Chưa có | Chưa xem (`none`) | Có (`yes`) | Chạy mới không cache (`rerun_repeat_only`) |
| **B2-rand** | Cả hai | Validation | 2026-11-02T00:04:23Z | `484b901` | Chưa xem (`none`) | Có (`yes`) | Giữ nguyên (`keep`) |
| **Phần còn lại Tầng 2–3** | Cả hai | Tùy arm | Chưa chạy; xem các dòng B2-flip và B2-rand ở trên | Chưa có | Chưa xem (`none`) | Cần đối chiếu từng run | Phân loại từng phân tích theo tiếp xúc thực tế khi gửi OSF |

---

## 2. Bảng 11 Giả Thuyết Nghiên Cứu (Table 4.3)

| Mã | Tên Giả Thuyết | Nội Dung Chi Tiết & Chuẩn Chấp Nhận / Bác Bỏ (Biên $\delta$ khai báo trước) |
| :--- | :--- | :--- |
| **H1.1** | GRACE không vượt Zero-shot trên Devign | Arm B2 (GRACE đầy đủ) không vượt B0 (zero-shot) về khả năng phân biệt trên Devign Test: Cận trên CI 95% của $\Delta\text{MCC}(\text{B2} - \text{B0}) < 0.03$ và của $\Delta\text{AUROC} < 0.02$ (biên thực chất $\delta = 0.02$). |
| **H1.2** | GRACE không vượt Zero-shot trên ReVeal & Không đạt mức công bố | Arm B2 không vượt B0 về khả năng phân biệt trên ReVeal Test: Cận trên CI 95% của $\Delta\text{MCC}(\text{B2} - \text{B0}) < 0.03$ và của $\Delta\text{AUROC} < 0.02$; GRACE không tái lập được hiệu năng công bố trong bài gốc: $\text{MCC}(\text{B2}) < 0.15$ trên cả hai dataset; $F_1(\text{B2})$ trên Devign thấp hơn $F_1$ luôn-vulnerable ($62.95\%$). |
| **H2.1** | Demo tác động qua nhãn | Demonstration tác động chủ yếu thông qua nhãn bề mặt: Độ nhạy nhãn thuần (Net label sensitivity) $\ge 15$ điểm phần trăm (tỷ lệ đổi khi đảo nhãn $\text{B2} \leftrightarrow \text{B2-flip}$ trừ biến động tự nhiên $\text{B2} \leftrightarrow \text{B2-rep}$). |
| **H2.2** | Nội dung demo không mang tín hiệu | Nội dung mã nguồn của demo không bổ sung tín hiệu bản chất: Cận trên CI của $\Delta\text{AUROC}(\text{B2} - \text{B2-rand}) < 0.02$ và của $\Delta\text{AUROC}(\text{B2-nolabel} - \text{B1}) < 0.02$; B2-labelonly tái tạo $\ge 80\%$ mức chênh lệch giữa B2 và B1. |
| **H2.3** | Cặp tương phản chỉ dịch chuyển điểm | Kỹ thuật cặp tương phản (B3) chỉ dịch chuyển điểm hoạt động chứ không tăng khả năng phân tách: Tỷ lệ đoán 1 của B3 cao hơn B2 $\ge 10$ điểm phần trăm trong khi cận trên CI 95% của $\Delta\text{AUROC}(\text{B3} - \text{B2}) < 0.02$. |
| **H3.1** | LLM không đọc Code Property Graph | Thông tin đồ thị CPG dạng văn bản không mang lại tín hiệu bổ sung cho LLM: Cận trên CI của $\Delta\text{AUROC}(\text{B1} - \text{B0}) < 0.02$ và của $\Delta\text{AUROC}(\text{B1} - \text{B1-shuf}) < 0.02$; B1-H2 không khác B1 theo cùng tiêu chí. |
| **H4.1** | Đo không ngưỡng gần ngẫu nhiên | Khi đánh giá không phụ thuộc ngưỡng (AUROC), toàn bộ pipeline LLM chỉ đạt hiệu năng gần mức ngẫu nhiên: $\text{AUROC} \le 0.62$ trên cả Devign và ReVeal đối với mọi arm LLM. |
| **H5.1** | Mốc có giám sát thắng rõ | Bộ phân lớp có giám sát đơn giản trên embedding đóng băng vượt trội rõ rệt pipeline LLM: $\Delta\text{MCC}(\text{SUP-LR} - \text{B2}) \ge 0.15$ với CI không chứa 0; $\text{AUROC}(\text{SUP-LR}) \ge 0.68$. |
| **H5.2** | LLM không bổ sung tín hiệu trực giao | Điểm số của LLM không bổ sung thêm tín hiệu trực giao sau khi đã có 34 đặc trưng cơ sở: Cận trên CI 95% của $\Delta\text{MCC}(P_\text{post} - P_\text{pre}) < 0.02$ (cùng 34 đặc trưng nền, cùng fold StratifiedGroupKFold, cùng ngưỡng $\tau^*$). |
| **H5.3** | Không biết trước khi nào gọi LLM (Routing $q=10\%$ Benefit vs Confidence & Complementarity) | Tại ngân sách gọi expert $q=10\%$, bộ định tuyến theo lợi ích (Benefit Router - Ridge) không vượt trội hơn bộ định tuyến theo độ tự tin (Confidence Router): Paired Bootstrap CI của $\Delta\text{Balanced Accuracy}(\text{benefit} - \text{confidence})$ và của $\Delta\text{MCC}$ có cận trên $< \delta = 0.02$ (phán quyết `no_meaningful_benefit`); đồng thời $\Delta\text{Balanced Accuracy}(\text{benefit} - \text{random})$ có cận trên CI $< 0.01$; số ca LLM sửa đúng không vượt khoảng $95\%$ của expert ngẫu nhiên cùng tỷ lệ đoán 1 (20 seed). |
| **H6.1** | Cơ chế truy hồi lệch hướng | Demonstration được truy hồi hiếm khi đúng cơ chế lỗi tương ứng; liên quan không kéo theo đúng: Tỷ lệ "Neither" $\ge 40\%$ trên Devign; chênh lệch accuracy giữa nhóm demo liên quan và không liên quan có CI chứa 0. |

### Cách Đọc Phán Quyết Cố Định Trước Cho Mọi So Sánh Cặp ($\Delta = \text{metric}(B) - \text{metric}(A)$)

- **`benefit` (Có bằng chứng lợi ích):** CI nằm hoàn toàn trên 0 ($\text{cận dưới} > 0$) và $\Delta \ge \delta$.
- **`no_meaningful_benefit` (Không có lợi ích đáng kể):** Cận trên CI $< \delta$.
- **`harm` (Gây hại hiệu năng):** CI nằm hoàn toàn dưới 0 ($\text{cận trên} < 0$).
- **`inconclusive` (Chưa đủ bằng chứng):** Khoảng CI chứa 0 hoặc cận trên $\ge \delta$ nhưng cận dưới $\le 0$.

Biên $\delta$ khai báo trước: Quy chuẩn chung cho biên thực chất khoa học là $\delta = 0.02$ (chi tiết: $\delta_\text{MCC} = 0.03$, $\delta_\text{AUROC} = 0.02$, $\delta_\text{BA} = 0.01$, $\delta_\text{MCC\_meta} = 0.02$, $\delta_\text{routing} = 0.02$).

---

## 3. Quy Tắc Phân Tích & Phương Pháp Luận Thống Kê (Mục 6)

1. **Khử trùng & Khóa Kho Dữ Liệu:**
   - Dữ liệu donor train được loại bỏ toàn bộ các mẫu trùng lặp chính xác với validation và test (sau khi chuẩn hóa bỏ khoảng trắng và chú thích).
   - Trong kho donor, giữ một đại diện cho nhóm mã trùng cùng nhãn; loại bỏ các nhóm mã trùng có mâu thuẫn nhãn.
   - Các cặp gần trùng (Jaccard token 3-gram $\ge 0.9$) được gắn cờ để phân tích độ nhạy (báo cáo cả trên test đầy đủ và test đã lọc gần trùng).
2. **Khóa 14 Ngưỡng Quyết Định Tối Ưu ($\tau^*$):**
   - Không dùng ngưỡng tùy tiện.
   - Công thức xác định ngưỡng tối ưu riêng cho từng dataset $d$, arm $a$, và seed $r$:
     $$\tau^*(d, a, r) = \operatorname{argmax}_{\tau \in \{0.01, 0.02, \dots, 0.99\}} \operatorname{MCC}(y_\text{val}(d), \mathbf{1}[s_\text{val}(d, a, r) \ge \tau])$$
   - **Quy tắc phá hòa (Tie-break):** Trong trường hợp có nhiều giá trị $\tau$ cùng đạt cực đại MCC, chọn giá trị gần $0.5$ nhất (`closest_to_0.5`); nếu khoảng cách tới $0.5$ bằng nhau thì lấy ngưỡng nhỏ hơn. Chỉ sử dụng các mẫu hợp lệ trên validation (`valid == True`); các ngưỡng khiến MCC không xác định (mọi dự đoán về cùng 1 lớp) bị bỏ qua.
   - **Quy tắc thừa kế ngưỡng (Threshold Inheritance Rule):** Các probe can thiệp nhãn hoặc lặp ($B2\text{-rep}$, $B2\text{-flip}$, $B3\text{-flip}$, $B3\text{-swap}$) **bắt buộc không chọn $\tau^*$ độc lập trên validation**, mà thừa kế trực tiếp giá trị $\tau^*$ đã khóa của arm gốc tương ứng ($B2$ hoặc $B3$). Việc chọn lại ngưỡng cho một arm đã bị đảo nhãn hay lặp sẽ "sửa" đúng hiệu ứng cần đo lường và làm trộn lẫn biến động do chọn ngưỡng vào hiệu ứng can thiệp.
   - 14 giá trị ngưỡng sau được ghi trong `configs/thresholds.json` và `Runs-management/thresholds.json`. Chúng được chọn trên validation; **không** khẳng định bản khóa có trước mọi lượt test lịch sử trong bảng kê tiếp xúc:
     - **Devign LLM Arms**: `devign|B0|42` = 0.08, `devign|B1|42` = 0.88, `devign|B2|42` = 0.70, `devign|B2-flip|42` = 0.70 (thừa kế từ B2), `devign|B2-rep|42` = 0.70 (thừa kế từ B2).
     - **ReVeal LLM Arms**: `reveal|B0|42` = 0.44, `reveal|B1|42` = 0.74, `reveal|B2|42` = 0.12, `reveal|B2-flip|42` = 0.12 (thừa kế từ B2), `reveal|B2-rep|42` = 0.12 (thừa kế từ B2).
     - **Meta-Models**: `devign|P-PRE|42` = 0.54, `devign|P-POST|42` = 0.60; `reveal|P-PRE|42` = 0.38, `reveal|P-POST|42` = 0.10.
3. **Thống Kê Khẳng Định & So Sánh Cặp (Bảng B):**
   - Paired Bootstrap $B = 5000$ lần lặp với seed cố định `20261117`.
   - Đơn vị gom nhóm (Cluster Units):
     - **Devign:** Cluster Bootstrap theo `commit_id` (2,068 cụm độc lập trên tập Test $N = 2,732$).
     - **ReVeal:** Cluster Bootstrap theo File-level Hashes (`file_hash`, 646 cụm độc lập trên tập Test $N = 2,274$, giải quyết triệt để rủi ro sụp đổ nhóm chrome/debian theo chuẩn Bước 0).
   - Phân chia fold meta-model: `StratifiedGroupKFold` (3 folds) trên tập Validation bảo đảm tính độc lập nhóm mã nguồn.
   - Hiệu chỉnh họ đa kiểm định theo phương pháp Holm-Bonferroni (`family_correction: holm`).
4. **Phân Tích Bổ Sung (Complementarity & Routing):**
   - 34 đặc trưng cơ sở $P_\text{pre}$ bao gồm 5 logit từ các mô hình nền tảng, xác suất tổng hợp $p$, $|p - 0.5|$, độ lệch MLP-Lexical, và 26 code metrics.
   - 4 đặc trưng từ LLM gồm: điểm $s$, cờ `valid` của **score**, tương tác $s \cdot p$, và độ lệch $s - p$. Khi không có score hợp lệ, meta-model dùng fallback đối xứng ($s = 0.5, valid = 0$); `response_valid` của raw greedy được báo riêng.
   - Mô hình meta sử dụng Logistic Regression ($C = 1.0$), 3-fold Out-Of-Fold (OOF).
   - Kiểm tra định tuyến tại các mức ngân sách 5%, 10%, 25% với Paired Bootstrap CI trực tiếp giữa Benefit Router vs Confidence Router, 20 seed ngẫu nhiên cho baseline RANDOM và trần Oracle.

---

## 4. Ma Trận 15 Cấu Hình (Arms) & Quy Tắc Dựng Probe (Mục 6.3)

| Nhóm Tầng (Tier) | Mã Arm | Nội Dung Prompt & Đặc Tính Probe | Khác Biệt So Với Arm Gốc | RQ Tương Ứng |
| :--- | :--- | :--- | :--- | :--- |
| **Sàn & Mốc** | ALL-0, ALL-1, RAND | Dự đoán hằng số 0, hằng số 1, ngẫu nhiên theo phân bố nhãn | Không gọi LLM; baseline phân bố nhãn | Tất cả |
| **Sàn & Mốc** | SUP-LR, SUP-MLP, SUP-METRIC | Logistic Regression trên CodeT5 768d, MLP 768→128→1, LR trên 26 code metrics | Mốc có giám sát trên embedding đóng băng (3 seed 42, 43, 44) | RQ5 |
| **Tầng 1** | **B0** | Role + domain + target code + binary question | Zero-shot; không đồ thị CPG, không demonstration | RQ1 |
| **Tầng 1** | **B1** | B0 + CPG nodes & edges (prefix 40 nút / 80 cạnh) | Thêm đồ thị CPG như bản tái triển khai | RQ1, RQ3 |
| **Tầng 1** | **B2** | B1 + 1 demo truy hồi từ kho clean donor kèm nhãn thật | GRACE hoàn chỉnh | RQ1, RQ2 |
| **Tầng 1** | **B2-flip** | B2 nhưng đảo nhãn demo ($1 \leftrightarrow 0$) ở câu dẫn | Đo độ nhạy nhãn (label sensitivity) | RQ2 |
| **Tầng 1** | **B2-rep** | B2 chạy lần 2 với cùng prompt (bỏ qua cache) | Đo biến động tự nhiên từ batching / GPU nondeterminism | RQ2 |
| **Tầng 2** | **B2-rand** | B1 + 1 demo ngẫu nhiên từ kho clean donor kèm nhãn thật | Nội dung demo không liên quan cơ chế (3 seed: 42, 43, 44) | RQ2 |
| **Tầng 2** | **B2-nolabel** | B1 + demo truy hồi; đổi câu dẫn thành "The following is a related example." (không nhãn) | Bỏ nhãn demonstration | RQ2 |
| **Tầng 2** | **B2-labelonly** | B1 + câu dẫn "A function similar to the one above was labelled Vulnerable/Non-vulnerable." (không có mã demo) | Chỉ còn gợi ý nhãn bề mặt | RQ2 |
| **Tầng 2** | **B1-shuf** | B0 + CPG của một hàm khác cùng số nút ($\pm 10\%$), cùng ngân sách | Đồ thị không mang thông tin target (3 seed: 42, 43, 44) | RQ3 |
| **Tầng 3** | **B1-full** | B0 + CPG lấp đầy ngân sách 1,500 token | Đổi chính sách cắt đồ thị (nhiều nút hơn) | RQ3 |
| **Tầng 3** | **B1-H2** | B0 + cụm evidence của H2 guarded cùng 1,500 token | Đổi cách đóng gói đồ thị theo vết luồng thực thi | RQ3 |
| **Tầng 3** | **B3** | B1 + cặp demo tương phản (1 vuln, 1 safe) + khối Key difference | Phương pháp Contrastive ICL đề xuất | RQ2, RQ4 |
| **Tầng 3** | **B3-nodiff** | B3 nhưng lược bỏ khối Key difference | Tách tác dụng của khối phân tích khác biệt | RQ2 |
| **Tầng 3** | **B3-swap** | B3 nhưng đảo thứ tự xuất hiện giữa 2 demo | Đo thiên lệch vị trí (recency bias) | RQ2 |
| **Tầng 3** | **B3-flip** | B3 nhưng đảo nhãn cả 2 demo ($1 \leftrightarrow 0$) | Đo độ nhạy nhãn khi cấu trúc nhãn đã được cân bằng | RQ2 |

---

## 5. Quy Chuẩn Prompt, Ngân Sách Token & Thứ Tự Section (Hình 6 & Mục 6.4)

1. **Thứ Tự Canonical (Figure 6 & Mã Tác Giả):**
   `[role_domain, target_code, question, node_info, edge_info, demonstration, answer]`
   *Quy tắc bất biến: Target code đi trước, graph ở giữa, demonstration ở cuối cùng ngay trước câu trả lời. Nhãn target tuyệt đối không bao giờ xuất hiện trong prompt.*
2. **Ngân Sách Token Tối Đa (8,192 Token Context):**
   - Mã nguồn target: $\le 3,000$ tokens.
   - Demonstration: $\le 1,500$ tokens mỗi demo.
   - Đồ thị CPG: $\le 1,500$ tokens.
   - Dự phòng (Reserve): $64$ tokens.
   - Đơn vị đo: Duy nhất bằng tokenizer của model (`Qwen3-Coder-30B-A3B-Instruct`).
3. **Đầu Ra, Score & Validity của Inference Đã Chạy:**
   - Notebook Kaggle gọi `llama-cpp-python` trực tiếp, đọc toàn bộ logits ở vị trí token đầu tiên sau prompt; xác định token ID riêng cho `0` và `1`, rồi tính `logprob_0`, `logprob_1`. Điểm $s = \frac{p(1)}{p(0)+p(1)} = \operatorname{sigmoid}(\operatorname{logit}_1-\operatorname{logit}_0)$. `top5` được lưu để chẩn đoán, **không phải** điều kiện để lấy score.
   - `valid` là cờ **score hợp lệ**: hai token ID phải xác định được, khác nhau, nằm trong vocabulary; logits phải hữu hạn và $s$ tính được. Nếu thiếu logits, logits không hữu hạn, tokenizer không khớp hoặc backend lỗi thì không có score hợp lệ; không ép score về 0. Trong notebook hiện tại, lỗi trước khi ghi record sẽ dừng lượt chạy hoặc để checkpoint giữ các record đã hoàn tất, thay vì tự tạo record `valid=false` cho mẫu lỗi.
   - `raw` là token greedy trên **toàn vocabulary**; `response_valid = true` chỉ khi raw sau giải mã là đúng `0` hoặc `1`. Raw khác hai nhãn có thể xảy ra dù `valid=true` và $s$ hữu hạn. Báo riêng số lượng/tỷ lệ `valid` và `response_valid`; không loại score hữu hạn chỉ vì raw không hợp lệ. `pred_argmax` của score dùng $s \ge 0.5$; khi đánh giá theo ngưỡng khóa thì dùng $s \ge \tau^*$, không đồng nhất hai dự đoán này với raw greedy.
   - Parser OpenAI-compatible cũ trong `llm_backend.py` dùng `top_logprobs` và chỉ cho score hợp lệ khi **cả token `0` lẫn token `1`** có mặt trong top-k; thiếu một trong hai là invalid. Quy tắc đó áp dụng cho chế độ API cũ, không phải cách notebook Kaggle đã tính score từ logits đầy đủ.

---

## 6. Quy Tắc Dừng (Stopping Rules)

1. **Lợi thế SUP-LR biến mất:** Nếu sau khi khử trùng và kiểm toán nhãn, mô hình SUP-LR không còn vượt trội B2, dừng nghiên cứu để rà soát toàn bộ quy trình tiền xử lý dữ liệu trước khi viết báo cáo.
2. **Thất bại Kiểm toán Prompt Audit:** Nếu tỷ lệ demonstration rỗng $> 1\%$, tỷ lệ thiếu đồ thị $> 5\%$ (ngoài các ca Joern lỗi đã gắn cờ), hoặc phát hiện rò rỉ nhãn target $> 0$, dừng quy trình, sửa hợp đồng dựng prompt, và chạy lại toàn bộ arm bị ảnh hưởng.
3. **Thất bại Smoke Test Backend:** Nếu tỷ lệ phản hồi hợp lệ có token 0/1 trong top-5 logprob $< 99\%$, không tiến hành chạy ma trận xác nhận cho đến khi backend mô hình đạt độ ổn định định lượng. Đây là tiêu chí smoke test API ở Bước 1, không phải định nghĩa `valid` của score trong inference Kaggle dùng logits đầy đủ.
4. **Đóng băng giao thức cho công việc tiếp theo:** Kể từ bản khóa có chứng cứ, thay đổi arm, model hoặc ngưỡng phải có amendment ghi ngày và phân loại thăm dò rõ ràng. Quy tắc này không được dùng để mô tả hồi tố các lượt test Tầng 1/B2-flip đã tiếp xúc. Các phân tích ngoài kế hoạch đăng ký về sau phải ghi là "thăm dò sau đăng ký" trong bài báo.

---

## 7. Bảng Băm Manifest & Checkpoint Đã Đóng Băng

### 7.1. Bảng Mã Băm SHA-256 Của Dữ Liệu & Manifest

| Tập Dữ Liệu | Phân Vùng / Mục | Số Dòng (Samples) | Tỷ Lệ Positive (Vuln) | Đường Dẫn Tệp | Mã Băm SHA-256 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Devign** | Raw Train | 21,854 | 45.84% | [`data/raw/devign_train.jsonl`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/01_Author_Baseline_Unified/output/research_freeze_20261101/devign/train_raw.jsonl) | `e456e20da10aa9a30df406d78dcf5f15f91da8c49fd5028584ca248b03f13f35` |
| **Devign** | Raw Validation | 2,732 | 43.45% | [`data/raw/devign_validation.jsonl`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/01_Author_Baseline_Unified/output/research_freeze_20261101/devign/validation_raw.jsonl) | `7318bc4aab8fecdac3ce1afe51c7833714be1b807c5437ab2c7dc0384a6543e0` |
| **Devign** | Raw Test | 2,732 | 45.94% | [`data/raw/devign_test.jsonl`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/01_Author_Baseline_Unified/output/research_freeze_20261101/devign/test_raw.jsonl) | `7f77094d9328624036cbd43ab1281aaf0c3378e220d5b3a10ba0a98922ab39c6` |
| **Devign** | Clean Donors Bank | 21,691 | 45.91% | [`data/manifests/devign_donor_clean.jsonl`](https://drive.google.com/file/d/10f_cARhg4BoMeIn4Q57qLzGiQuZUv00_/view?usp=sharing) | `5eda46695ea98091168c2a87591010b4fe6c08597a376c3361b4cf40297d1dfe` |
| **Devign** | **Manifest Concatenation** | - | - | [`data/manifests/devign_manifest_stats.json`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/01_Author_Baseline_Unified/output/research_freeze_20261101/devign/stats.json) | **`5a084a10e5c191039e56e351bf8d722fe017424f159a84d6b92be86a1d0f4952`** |
| **Devign** | Val Subset 600 (Seed 42) | 600 | 43.50% | [`data/specs/devign_val_subset600.jsonl`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/data/specs/devign_val_subset600.jsonl) | `88f749c000a7b110ed87641d9d5dc4bc912b9f2fdb3dcc2a97753238a4dbcdfd` |
| **Devign** | Test Specs | 2,732 | 45.94% | `data/specs/devign_test.jsonl` | `bd0f4d025afd051c064ab58c1495a887c5851b6408e2d47d39ae64d421b898c6` |
| **ReVeal** | Raw Train | 18,187 | 9.90% | [`data/raw/reveal_train.jsonl`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/01_Author_Baseline_Unified/output/research_freeze_20261101/reveal/train_raw.jsonl) | `87c6ec979d8724d1db25217ae6c5637fedaca5350fc954baab4c615efc56f66c` |
| **ReVeal** | Raw Validation | 2,273 | 9.24% | [`data/raw/reveal_validation.jsonl`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/01_Author_Baseline_Unified/output/research_freeze_20261101/reveal/validation_raw.jsonl) | `03ccd535ecc5c85601377d1880f05307d20577e195cc8808d2c5cbd880725d50` |
| **ReVeal** | Raw Test | 2,274 | 10.11% | [`data/raw/reveal_test.jsonl`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/01_Author_Baseline_Unified/output/research_freeze_20261101/reveal/test_raw.jsonl) | `5132c4a2cab7cea81435b5039af964cab184e6ce7b4d9e2df524962b0f6d45f3` |
| **ReVeal** | Clean Donors Bank | 17,636 | 9.57% | [`data/manifests/reveal_donor_clean.jsonl`](https://drive.google.com/file/d/162syKwALRE2EvMbP5bBHA4P9eis30hjA/view?usp=sharing) | `9e891cf5b8dfa93c2c3d9d5039e328c5d36c115d173051c5991fc0939e1d372d` |
| **ReVeal** | **Manifest Concatenation** | - | - | [`data/manifests/reveal_manifest_stats.json`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/01_Author_Baseline_Unified/output/research_freeze_20261101/reveal/stats.json) | **`59498c4a4ab038babe558675c183c2b104b0145590fb0accf8b02cd5440d57f7`** |
| **ReVeal** | Val Subset 600 (Seed 42) | 600 | 9.17% | [`data/specs/reveal_val_subset600.jsonl`](https://github.com/kazunguyen/GRACE-summary/blob/prereg-v1/data/specs/reveal_val_subset600.jsonl) | `72ce24b2629588a7edf5206c99b26865b630a489580a6b03964c368fad79858e` |
| **ReVeal** | Test Specs | 2,274 | 10.11% | `data/specs/reveal_test.jsonl` | `26d79cec7a31e45a99cf8f22266aa793f323eacb6328cf8d5bd2fc1b34131deb` |

**Lưu ý đối chiếu artifact:** Tên hiển thị trong cột đường dẫn được giữ theo bản đăng ký; link GitHub trỏ tới raw/stats trong snapshot `research_freeze_20261101`, còn hai link Drive trỏ tới file `donors.jsonl` cùng snapshot (Devign SHA-256 `7727d2793fbb9f305e547bd6e7126ae70f2e0ee97e2b7c5c260322c6b6af5a62`; ReVeal SHA-256 `6bf44ab86c8524d239e610fdccff5916cfc402fef7945d7cbe7f695e287abbce`). SHA-256 đang in trong bảng **không khớp byte** với các file raw/stats/donor đã liên kết, nên chưa được dùng để xác thực những link đó. Các dòng specs đầy đủ local vượt giới hạn GitHub (2.732 / 2.274 mẫu). Hai file subset 600 chuẩn hóa `data/specs/devign_val_subset600.jsonl` (SHA-256 `88f749c000a7b110ed87641d9d5dc4bc912b9f2fdb3dcc2a97753238a4dbcdfd`) và `data/specs/reveal_val_subset600.jsonl` (SHA-256 `72ce24b2629588a7edf5206c99b26865b630a489580a6b03964c368fad79858e`) đã được đối chiếu khớp chính xác 100% với bảng trên và mở ngoại lệ `.gitignore` trong repository.

### 7.2. Checkpoint Mô Hình & Môi Trường Suy Luận (Provenance Chuẩn Hóa)

- **Kiến trúc và tokenizer:** `Qwen/Qwen3-Coder-30B-A3B-Instruct`; tokenizer ở revision `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`.
- **Trọng số model thực chạy:** GGUF từ `ggml-org/Qwen3-Coder-30B-A3B-Instruct-GGUF`, file `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`, lượng tử hóa `Q4_K_M`, SHA-256 `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`. Manifest của các lượt B0, B1, B2, B2-flip và B2-rand đã có output đều ghi cùng định danh này.
- **Backend inference thực chạy:** `llama-cpp-python 0.3.16` gọi trực tiếp `Llama(...)` trên Kaggle GPU 2× Tesla T4, với `n_ctx=8192`, `n_batch=256`, `n_gpu_layers=-1`, `logits_all=True`; chấm điểm từ logits token đầu của nhãn `0` và `1`. Đây là cấu hình trong notebook và run manifest, không phải `llama-server` qua REST/Cloudflare.
- **Nguồn file model trên Kaggle:** Notebook B2 tìm đúng tên GGUF trong output của `quangdung1111/qwen3coder30b-prepare-notebook`; các notebook arm khác tìm file GGUF gắn làm Input và kiểm SHA-256 trước khi inference. Slug `tnthnhneee/qwen3-30b-a3b/gguf/coder-instruct-ud-q4_k_xl` trong bản protocol cũ không định danh file `Q4_K_M` đã chạy.
- **Phạm vi model fallback:** Không có run inference B0/B1/B2/B2-flip/B2-rand đã đối chiếu nào dùng vLLM hoặc Qwen2.5-Coder. Các lựa chọn đó trong `protocol.yaml` là phương án dự kiến trước đây, không được gộp vào kết quả của model GGUF trên.
- **Ghi chú về bản khóa:** Hai bản `protocol.yaml` được giữ nguyên như artifact lịch sử vì `thresholds.json` lưu SHA-256 của protocol đã khóa. Phần này là đối chiếu hậu kiểm với notebook và output thực chạy, không thay đổi thời điểm hay nội dung bản khóa cũ.

---

## 8. Checklist Nghiệm Thu Đăng Ký Trước (Phụ Lục C - Proposal)

- [x] **Bước 0:** Metric lịch sử tạo lại từ file từng mẫu (sai khác $\le 0.001$); bảng sửa–hỏng có hàng ALL-0 / ALL-1 / RANDOM; paired bootstrap 5,000 reps; cluster unit resolved: Devign (2,068 commit groups), ReVeal (646 file hash groups); StratifiedGroupKFold OOF; Paired Bootstrap CI cho Routing q=10% (Benefit vs Confidence).
- [x] **Smoke Test Backend:** $\ge 99\%$ prompt có cả hai token 0 và 1 trong top-k ($k = 20$); hai lần chạy trùng $\ge 98\%$ ($100\%$ trùng); thông lượng và độ trễ đã đo; fail-fast 0 retry khi context exceeded.
- [x] **Manifest Dữ Liệu:** Đã băm SHA-256 đóng băng; một kiểm toán trùng lặp duy nhất (loại 18 ca Devign, 129 ca ReVeal); kho donor đã khử trùng (21,691 Devign, 17,636 ReVeal).
- [x] **Kiểm Thử & Prompt Audit:** pytest tests/ xanh (100%); prompt audit: rò rỉ nhãn $= 0$, demo rỗng $\le 1\%$ ($0.0\%$ trên Devign, $0.7\%$ trên ReVeal); đồ thị thiếu được gắn cờ; 30 prompt mỗi dataset đã sẵn sàng trong `manual_sample.jsonl`.
- [x] **Giao thức và công bố tiếp xúc:** Giao thức hiện tại và `preregistration.md` đã được ghi dưới tag `prereg-v1` để chuẩn bị gửi OSF; việc gửi OSF thực tế còn chờ. Suy luận test Tầng 1 và các metric thăm dò đã có trước đăng ký, được khai báo là existing data mức following analysis.
- [x] **Bản ghi ngưỡng hiện tại (Bước 5):** 14 giá trị $\tau^*$ được ghi là chọn trên validation trong `thresholds.json` cùng `locked_sha256`; lịch sử hiện có không chứng minh đã khóa trước mọi lượt test cũ. Các probe lặp/đảo ($B2\text{-flip}$, $B2\text{-rep}$, $B3\text{-flip}$, $B3\text{-swap}$) thừa kế $\tau^*$ của arm gốc theo giao thức hiện tại. Test Tầng 1 lịch sử vẫn được khai báo ở mức following analysis.
- [x] **Bảng Kê Tiếp Xúc Test (Exposure Ledger):** Đã điền cho mọi arm đã chạy trước đăng ký (`exposure_ledger`); arm giữ lại có `manifest.json` khớp giao thức khóa và records đủ logprob khôi phục $s$; không lượt B2-rep nào từng đọc cache (`repeat: true`, `tag="repeat"`).
- [x] **Schema Thực Thi B.2:** Mọi run test có `records.jsonl` đủ schema B.2 và `manifest.json` môi trường; cache theo identity đầy đủ; candidate-score validity và raw verdict validity được tách biệt minh bạch.
- [x] **Mô Hình Meta & Routing Bước 6:** SUP-LR/SUP-MLP/SUP-METRIC 3 seed; P_pre/P_post cùng fold StratifiedGroupKFold và fallback đối xứng; routing với random 20 seed, trần oracle và paired bootstrap CI tại q=10%.
- [x] **Đánh Giá Cuối & Bảng A/B/C/D:** Bảng A, B, C, D và hai hình sinh từ một script thống nhất (`evaluate_final.py`), không sửa tay; Bảng B có cột kết luận theo biên $\delta = 0.02$ và số lượt bootstrap suy biến.
- [x] **Đối chiếu 11 giả thuyết:** Bảng 4.3 ghi tiêu chuẩn ủng hộ / bác bỏ / chưa đủ bằng chứng và biên thực chất $\delta$ của kế hoạch hiện tại. Không khẳng định các tiêu chuẩn này có trước test Tầng 1 lịch sử; trạng thái tiến cứu phải xét riêng cho từng so sánh chưa làm.
- [ ] **Chấm Mù & Kiểm Toán Nhãn (Bước 8):** $\kappa$ chấm mù (retrieval và gói 60 ca), bảng phân tích có điều kiện; kiểm toán nhãn 100 ca mỗi dataset (kế hoạch và format gói ca đã chuẩn bị sẵn, thực hiện song song với Bước 5 trên GPU).
- [x] **Gói Tái Lập OSF Độc Lập:** Gói tái lập chạy lại được từ README trên một máy sạch; phần offline không cần GPU; không có khóa API trong log; 39 artifact được đóng gói trong ZIP và xác thực mã băm SHA-256 đối soát.

