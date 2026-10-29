# Báo Cáo Quyết Định Kiến Trúc & Thống Nhất Baseline GRACE Gốc

Tài liệu này phân tích chi tiết toàn bộ các điểm sai khác kỹ thuật giữa các phiên bản baseline hiện tại (Mã nguồn tác giả công bố, Baseline của Hiếu tại `02_Baseline_Code_Author`, và các phiên bản tái dựng tại `Graduation-Project/Ablation_V2`), đồng thời xác lập các quyết định thống nhất cuối cùng cho bản baseline chung tại `d:\JUNIOR\LabThayTho\GRACE-summary\01_Author_Baseline_Unified`.

---

## 1. Sai Khác & Thống Nhất về Model LLM Backbone

### 1.1. Hiện trạng sai khác giữa các phiên bản
- **Mã nguồn tác giả công bố (`basep.py`, `llmpre.py`)**:
  - Dùng OpenAI API (`openai.ChatCompletion.create`) với model `gpt-4`.
  - Không truyền tham số `temperature`, `seed`, hay giới hạn `max_tokens`.
- **Baseline của Hiếu (`02_Baseline_Code_Author`)**:
  - Mặc định đặt model `gemma-4-26B-A4B-it` hoặc `Llama-3.3-70B-Instruct` thông qua FPT Cloud API (`https://mkp-api.fptcloud.com`).
  - Cho phép trích xuất `reasoning_content` nếu `content` trả về rỗng.
  - Tích hợp chế độ `use_mock` để chạy thử cục bộ.
- **Bản tái dựng `Reproduced-Code-Based` / Contract**:
  - Khai báo model `publishers/qwen/models/qwen3-coder-480b-a35b-instruct-maas` qua Google Vertex AI SDK.
  - Tích hợp thêm transport `fpt_provider.py` kết nối FPT AI Factory (`https://token-api.fpt.ai/v1`) đọc từ file `.env` chung (`D:/JUNIOR/LabThayTho/.env`).

### 1.2. Vấn đề cốt lõi về Chế độ Thinking (Suy luận ngầm)
- Các model thế hệ mới (DeepSeek-V4-Flash, Qwen 3.6/3.8 Thinking) có cơ chế sinh chuỗi suy luận nội bộ (reasoning tokens).
- Nếu bật thinking: Với ngân sách `max_tokens: 256`, toàn bộ token bị chuỗi suy luận tiêu thụ hết trước khi kịp sinh nhãn `0` hoặc `1` ở dòng cuối. Kết quả dẫn đến response bị cắt cụt giữa chừng và evaluator ghi nhận lỗi `invalid_exhausted`.
- Do đó, **bắt buộc phải tắt hoàn toàn thinking** để model trả lời trực diện đáp án.

### 1.3. Quyết định chuẩn hóa cho Baseline
1. **Multi-provider Client**: Hỗ trợ đồng bộ 3 phương thức thực thi:
   - **FPT Cloud API** (OpenAI-compatible) thông qua file `.env` tại `D:/JUNIOR/LabThayTho/.env` (`FPT_API`, `FPT_MODEL`, `FPT_BASE_URL`).
   - **Google Vertex AI** thông qua `VERTEX_PROJECT` và `VERTEX_LOCATION`.
   - **Mock Engine** (`--mock`) cho phép chạy kiểm thử offline 100%, không phụ thuộc mạng hay API key.
2. **Thinking Mode**: Tắt hoàn toàn (`chat_template_kwargs: {"thinking": False}` cho DeepSeek, `{"enable_thinking": False}` cho Qwen).
3. **Tham số suy luận cố định theo Contract**:
   - `temperature = 0.0` (tuyệt đối xác định).
   - `seed = 42`.
   - `max_tokens = 256`.
   - `retry_policy`: 5 lượt thử lại với cơ chế Exponential Backoff (5s đến 120s); sau 5 lượt thất bại thì đánh dấu trạng thái `invalid_exhausted`.

---

## 2. Sai Khác & Thống Nhất về Cách Xây Dựng Prompt

### 2.1. Hiện trạng sai khác
- **Mã nguồn tác giả công bố**:
  - Cắt cứng theo số ký tự Python: `inputCode[:4000]`, `inputnode[:2000]`, `inputedge[:2000]`, `inputex[:4000]`.
  - Nối chuỗi thô: `format(inputCode) + templates[1] + templates[2] + format(inputnode) + templates[3] + format(inputedge) + templates[4] + format(inputex)`.
  - Mẫu template hướng dẫn: `output either 'Vulnerable' or 'Non-vulnerable'`. Nhưng khi parse lại kiểm tra `if prediction == "0" or prediction == "1"`.
- **Baseline của Hiếu**:
  - Giới hạn: Target code 3000 ký tự, Demo code 1500 ký tự, max 25-30 nodes, max 25-30 edges.
  - Output requirement: `You must output ONLY a single character: '1' if Vulnerable, or '0' if Non-vulnerable. Do not output any explanation.`
- **Contract & Reproduced-Code-Based**:
  - Trước đây tăng lên 24.000 bytes. Theo chỉ đạo mới nhất, **hạ và chốt chuẩn 8.192 bytes UTF-8** (tương đương cửa sổ ngữ cảnh 8.192 tokens của GPT-4 trong bài báo gốc).
  - Graph budget: `graph_nodes_max: 40`, `graph_edges_max: 80` (theo sửa đổi ngân sách đồ thị đã kiểm chứng bao quát 100% mẫu CPG).

### 2.2. Thứ tự cắt xén (Truncation Policy) khi vượt giới hạn
Để đảm bảo thông tin quan trọng nhất không bị mất ngẫu nhiên, quy trình cắt xén tuân thủ nghiêm ngặt theo thứ tự ưu tiên sau:
1. **Cắt Demo Code trước**: Rút ngắn dần mã nguồn của ví dụ mẫu cho đến khi vừa ngân sách. Nếu demo code bị rút về 0 mà prompt vẫn vượt 8.192 bytes:
2. **Cắt Graph Context**: Rút ngắn danh sách cạnh (edges) và nút (nodes) của đồ thị hàm mục tiêu. Nếu graph bị xóa hết mà vẫn vượt ngân sách:
3. **Cắt Target Code**: Cắt từ đuôi hàm mục tiêu, bảo toàn phần đầu hàm (`preserve_prefix: true`).

### 2.3. Hướng dẫn xuất đáp án (Output Contract)
- Định dạng yêu cầu xuất đáp án được chuẩn hóa ở cuối prompt:
  ```text
  ### OUTPUT CONTRACT
  Analyze the target function carefully. You may reason internally, but do not
  write an explanation in the response. The last non-empty line of your response
  must contain exactly one character: `1` if the target is Vulnerable, or `0` if
  the target is Non-vulnerable. Do not output any other label or score.
  ```
- Không thêm các câu lệnh mâu thuẫn yêu cầu nhãn chữ `Vulnerable / Non-vulnerable`.

---

## 3. Sai Khác & Thống Nhất về Evaluator và Chấm Điểm Benchmark

### 3.1. Sai sót nghiêm trọng trong parser cũ cần loại bỏ
Trong baseline cũ của Hiếu (`02_Baseline_Code_Author/baseline_code_text/evaluator.py`), hàm parser áp dụng Regex dự phòng và Heuristic Fallback:
```python
# CODE CŨ GÂY SAI LỆCH METRIC:
logger.warning(f"Không thể bóc tách chuẩn xác từ LLM: ... Áp dụng Default Fallback = 0 (Safe).")
return 0, "Fallback: Safe/0 by default"
```
**Tác hại**: Việc tự ý gán nhãn `0` cho các câu trả lời sai format, chuỗi rỗng hoặc lỗi mạng làm sai lệch hoàn toàn độ chính xác (Accuracy), thổi phồng True Negatives (TN) và làm méo mó chỉ số MCC, F1.

### 3.2. Quyết định chuẩn hóa cho Parser & Evaluator
1. **Strict Parser (`parser.py`)**:
   - Chỉ đọc dòng không rỗng cuối cùng (last non-empty line).
   - Nếu là `"1"` -> trả về `1` (Hợp lệ).
   - Nếu là `"0"` -> trả về `0` (Hợp lệ).
   - Mọi trường hợp khác (giải thích thừa sau nhãn, chuỗi rỗng, lỗi mạng) -> trả về `None` (`invalid`).
   - **Tuyệt đối không ép nhãn (No coercion)**.
2. **Evaluator tính toán theo Contract**:
   - Quần thể tính metric: Chỉ tính trên tập các phản hồi hợp lệ (`valid_predictions_only`).
   - Các chỉ số báo cáo đầy đủ:
     - Ma trận nhầm lẫn: `TP`, `TN`, `FP`, `FN`.
     - `Accuracy`, `Precision`, `Recall`, `F1-Score`.
     - `Balanced Accuracy` = `(Recall + Specificity) / 2`.
     - `MCC` (Matthews Correlation Coefficient).
     - Tỷ lệ dự đoán dương tính: `Predicted Vulnerable Rate`.
   - Giám sát toàn cục:
     - Tổng số mẫu `N_total`, số mẫu hợp lệ `N_valid`, số mẫu không hợp lệ `N_invalid`.
     - Tỷ lệ lỗi format: `Invalid Rate = N_invalid / N_total`.
     - Tỷ lệ bao phủ: `Coverage = N_valid / N_total`.
   - Trivial Baselines (Baseline mù đối chứng):
     - `Always Predict Vulnerable` (Dự đoán toàn bộ 1).
     - `Always Predict Non-vulnerable` (Dự đoán toàn bộ 0).

---

## 4. Sai Khác & Thống Nhất về Tech Stack & Thuật Toán Từng Bước

### 4.1. Bước 1: Trích xuất và biểu diễn đồ thị (CPG Extraction)
- **Chuẩn hóa**: GRACE gốc sử dụng toàn bộ CPG (Whole CPG gồm AST + CFG + PDG), không sử dụng phương pháp verbalize câu văn (GraphVerb) và không cắt lát điểm chìm (Sink Slice).
- Cấu trúc biểu diễn trong prompt tuân thủ Fig. 5 và Fig. 6 của bài báo:
  - Danh sách nút: `Node {id}: ({type}) '{code_snippet}'` (tối đa 40 nút).
  - Danh sách cạnh: `Edge: Node {src} -> {type} -> Node {dst}` (tối đa 80 cạnh).

### 4.2. Bước 2: Embedding và giảm chiều ngữ nghĩa
- **Mô hình**: `Salesforce/codet5-base` (768 chiều), pooling Masked Mean Pooling.
- **Hồ sơ mặc định (Code-based profile)**:
  - Khớp mã nguồn tác giả `genexample.py`: Sử dụng BERT-Whitening fit trên tập Train để chuẩn hóa và giảm từ 768 chiều xuống 256 chiều.
  - Tìm kiếm tương đồng ngữ nghĩa: FAISS Inner Product / Cosine Similarity.
- **Hồ sơ đối chứng (Paper-based profile)**:
  - Hỗ trợ tùy chọn `--profile paper` sử dụng t-SNE 2 chiều + khoảng cách L2 như mô tả trong bài báo.

### 4.3. Bước 3: Reranker Lai ghép (Hybrid Reranking) & Chọn Demonstration
- **Ngân hàng ứng viên ban đầu (Candidate Pool)**:
  - Tuân thủ contract: Cố định Top 50 ứng viên train tương đồng ngữ nghĩa nhất.
  - Chọn Top 5 ứng viên ngữ nghĩa cao nhất để đưa vào bước reranking.
- **Công thức Reranking của tác giả**:
  $$\text{Score} = 0.7 \times \text{Jaccard}_{\text{Code}} + 0.3 \times \text{Sim}_{\text{AST}}$$
  - $\text{Jaccard}_{\text{Code}}$: Tính trên tập từ vựng tách bởi khoảng trắng (`code.split()`).
  - $\text{Sim}_{\text{AST}}$: Tính tỷ lệ Levenshtein / SequenceMatcher trên chuỗi node types của AST.
- **Số lượng Demonstration**:
  - Chọn duy nhất **1 demonstration tốt nhất** (kèm mã nguồn và nhãn Ground Truth 0/1).
  - Không phân tầng đa lớp (No Stratified Demos), không đa dạng hóa MMR (No MMR).

---

## 5. Tổng Kết Kiến Trúc Baseline Chuẩn

| Thành phần | GRACE Gốc Thống Nhất (01_Author_Baseline_Unified) |
|---|---|
| **Cửa sổ ngữ cảnh** | 8.192 bytes UTF-8 |
| **Giới hạn đồ thị** | Max 40 nodes, 80 edges (Whole CPG) |
| **Số lượng Demonstration** | Đúng 1 mẫu (tốt nhất từ Hybrid Reranker) |
| **Công thức Reranker** | $0.7 \times \text{Jaccard} + 0.3 \times \text{AST\_Sim}$ trong Top 5 từ Pool 50 |
| **Embedding Backbone** | CodeT5-base (768d) + Whitening (256d) |
| **LLM Inference** | Qwen / DeepSeek-V4-Flash / Vertex AI / Mock |
| **Thinking Mode** | Disabled (`thinking: False`) |
| **Nhiệt độ / Seed** | Temperature 0.0, Seed 42, Max tokens 256 |
| **Quy tắc Parser** | Strict exact last line binary (0 hoặc 1, không fallback) |
| **Báo cáo Metric** | Tính trên tập Valid, tách bạch Invalid Rate |
