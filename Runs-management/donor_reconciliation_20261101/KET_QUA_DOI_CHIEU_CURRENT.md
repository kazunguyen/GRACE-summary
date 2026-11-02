# Đối chiếu prompt sau thống nhất donor — 01/11/2026

**Phạm vi lịch sử 01/11/2026:** snapshot này chỉ đối chiếu các nguồn trong downloaded_output_inventory.json. **66 mẫu cần inference mới nếu chuyển B2 sang kho donor đã thống nhất.** 19,956 kết quả còn tương thích về prompt với thay đổi donor này, nếu giữ nguyên model/tokenizer/backend/tham số/chính sách score.

| Arm | Dataset | Split | Output đã kiểm tra | Cần inference mới | Giữ kết quả cũ |
|---|---|---|---:|---:|---:|
| B0 | devign | test | 2,732 | 0 | 2,732 |
| B0 | devign | validation | 2,732 | 0 | 2,732 |
| B0 | reveal | test | 2,274 | 0 | 2,274 |
| B0 | reveal | validation | 2,273 | 0 | 2,273 |
| B2 | devign | test | 2,732 | 38 | 2,694 |
| B2 | devign | validation | 2,732 | 28 | 2,704 |
| B2 | reveal | test | 2,274 | 0 | 2,274 |
| B2 | reveal | validation | 2,273 | 0 | 2,273 |

## Cách kiểm tra

- **devign:** 21,750 → 21,691 donor; tái tạo đúng 5,464/5,464 demo cũ.
- **reveal:** 17,636 → 17,636 donor; kho cũ/mới giống hệt về thứ tự, ID, code, nhãn và AST.

1. Đọc từng `records.jsonl`, đối chiếu `prompt_sha256` và nhãn với đúng prompt gốc. Gộp bản sao bằng arm/dataset/split/seed/ID/hash prompt/hash model; kiểm tra không có score mâu thuẫn.
2. Tái dùng vector CodeT5 và AST/CPG đã cache; với kho thay đổi, fit lại whitening 256 chiều trên toàn bộ kho mới. Giữ thuật toán B2: top-50 ngữ nghĩa → top-5 → rerank 0,7 Jaccard code + 0,3 AST. Tái tạo kho cũ trước để kiểm tra attribution; mọi demo được nhận diện là đổi đều được kiểm tra lại bằng hàm retrieval scalar gốc.
3. Giữ nguyên phần code target, graph 40/80 và câu dẫn; chỉ thay payload demo/nhãn, cắt demo bằng đúng tokenizer Qwen và ngân sách 1.500 token. So SHA-256 của toàn bộ prompt cuối cùng. Đổi ID donor nhưng prompt cuối giống hệt không tạo thêm lượt inference.

Trong các prompt cần chạy lại: **21** dùng demo cũ không còn trong kho mới; **45** đổi lựa chọn retrieval dù demo cũ vẫn còn. Vì vậy không thể dùng riêng kiểm toán donor bị loại để quyết định danh sách chạy lại.

## Danh sách và đầu vào

- [Danh sách chính xác các mẫu cần inference lại (CSV)](mau_can_inference_lai_CURRENT.csv): ID target, demo cũ/mới, hash prompt trước/sau và đường dẫn output gốc.
- [Toàn bộ quyết định giữ/chạy lại (CSV)](downloaded_record_decisions.csv).
- [So sánh demo của toàn bộ B2 (CSV)](demo_comparison.csv).
- `rerun_inputs/B2/<dataset>/<split>/prompts.jsonl`: chỉ các prompt đổi, kèm manifest; **đầu vào để kiểm tra, chưa phải bundle Kaggle hoàn chỉnh**.
- `new_reference/B2/<dataset>/<split>/prompts.jsonl`: bộ prompt tham chiếu mới đầy đủ, xuất riêng, chưa thay bộ prompt đang dùng.
- [Tóm tắt máy đọc được](summary.json) và [nguồn output đã đối chiếu](downloaded_output_inventory.json).

## Cách dùng kết quả

Danh sách này áp dụng khi chuyển sang kho `research_freeze_20261101`; kết quả cũ vẫn mô tả đúng các prompt cũ. Không cần chạy lại B0 chỉ vì đổi donor. Chưa tìm thấy output inference thật đã tải về của B1, B2-flip, B2-rep hoặc B2-rand trong lần kiểm tra này; các arm đó không được tính thành lượt chạy lại trong snapshot này. B1 I-07 và B2-flip I-06 đã được xác minh sau đó; xem [hiện trạng](../HIEN_TRANG.md).

Nếu validation B2 thay đổi, ghép score mới của các mẫu đổi với score cũ còn tương thích để có **toàn bộ validation phiên mới**, rồi tính/khóa ngưỡng cho phiên đó. Không chọn ngưỡng chỉ trên phần chạy lại, không dùng test để chọn ngưỡng và không ghi đè ngưỡng lịch sử. Các score test giữ được có thể chấm lại offline bằng ngưỡng phiên mới.

Lần đối chiếu này không gọi LLM, không sửa prompt/output đang dùng, không đổi `thresholds.json` và không sửa snapshot/tag đã niêm phong.

## Kiểm tra đầu ra

Đã kiểm tra đủ mẫu từng split, không trùng ID quyết định, mọi hash prompt mới khớp nội dung, và tập `rerun_inputs` trùng chính xác tập quyết định cần inference mới. Hash đầu vào/nguồn retrieval nằm trong các JSON provenance đi kèm.

## ID của các mẫu cần inference mới

| Dataset | Split | ID target | Demo cũ | Demo mới | Lý do |
|---|---|---|---|---|---|
| devign | test | `devign:test:11383` | `devign:train:24468` | `devign:train:23322` | Demo cũ bị loại |
| devign | test | `devign:test:11527` | `devign:train:10445` | `devign:train:13981` | Đổi thứ hạng retrieval |
| devign | test | `devign:test:11646` | `devign:train:1825` | `devign:train:4663` | Đổi thứ hạng retrieval |
| devign | test | `devign:test:12429` | `devign:train:24816` | `devign:train:1580` | Đổi thứ hạng retrieval |
| devign | test | `devign:test:13172` | `devign:train:1399` | `devign:train:15079` | Đổi thứ hạng retrieval |
| devign | test | `devign:test:14108` | `devign:train:15712` | `devign:train:3212` | Đổi thứ hạng retrieval |
| devign | test | `devign:test:1426` | `devign:train:21650` | `devign:train:21758` | Demo cũ bị loại |
| devign | test | `devign:test:14476` | `devign:train:27172` | `devign:train:26289` | Demo cũ bị loại |
| devign | test | `devign:test:1473` | `devign:train:12467` | `devign:train:8115` | Demo cũ bị loại |
| devign | test | `devign:test:17807` | `devign:train:23477` | `devign:train:21486` | Đổi thứ hạng retrieval |
| devign | test | `devign:test:18324` | `devign:train:6876` | `devign:train:9431` | Đổi thứ hạng retrieval |
| devign | test | `devign:test:19075` | `devign:train:25438` | `devign:train:12737` | Demo cũ bị loại |
| devign | test | `devign:test:20970` | `devign:train:27091` | `devign:train:4357` | Đổi thứ hạng retrieval |
| devign | test | `devign:test:21511` | `devign:train:8753` | `devign:train:140` | Demo cũ bị loại |
| devign | test | `devign:test:2195` | `devign:train:17605` | `devign:train:1179` | Đổi thứ hạng retrieval |
| devign | test | `devign:test:22392` | `devign:train:15477` | `devign:train:15364` | Demo cũ bị loại |
| devign | test | `devign:test:2246` | `devign:train:26169` | `devign:train:18188` | Demo cũ bị loại |
| devign | test | `devign:test:22693` | `devign:train:24980` | `devign:train:23091` | Đổi thứ hạng retrieval |
| devign | test | `devign:test:22959` | `devign:train:14632` | `devign:train:9136` | Đổi thứ hạng retrieval |
| devign | test | `devign:test:23465` | `devign:train:25579` | `devign:train:17530` | Đổi thứ hạng retrieval |
| devign | test | `devign:test:24205` | `devign:train:11585` | `devign:train:2388` | Đổi thứ hạng retrieval |
| devign | test | `devign:test:24291` | `devign:train:9520` | `devign:train:2926` | Demo cũ bị loại |
| devign | test | `devign:test:24433` | `devign:train:12812` | `devign:train:25420` | Đổi thứ hạng retrieval |
| devign | test | `devign:test:24484` | `devign:train:26519` | `devign:train:8974` | Đổi thứ hạng retrieval |
| devign | test | `devign:test:24855` | `devign:train:6182` | `devign:train:5175` | Đổi thứ hạng retrieval |
| devign | test | `devign:test:26038` | `devign:train:15638` | `devign:train:2476` | Đổi thứ hạng retrieval |
| devign | test | `devign:test:26468` | `devign:train:26815` | `devign:train:2070` | Đổi thứ hạng retrieval |
| devign | test | `devign:test:27254` | `devign:train:23001` | `devign:train:6329` | Đổi thứ hạng retrieval |
| devign | test | `devign:test:3158` | `devign:train:23060` | `devign:train:25678` | Demo cũ bị loại |
| devign | test | `devign:test:321` | `devign:train:7488` | `devign:train:1613` | Đổi thứ hạng retrieval |
| devign | test | `devign:test:4685` | `devign:train:11652` | `devign:train:18168` | Đổi thứ hạng retrieval |
| devign | test | `devign:test:5908` | `devign:train:6623` | `devign:train:4527` | Demo cũ bị loại |
| devign | test | `devign:test:6519` | `devign:train:11561` | `devign:train:10408` | Demo cũ bị loại |
| devign | test | `devign:test:7048` | `devign:train:6623` | `devign:train:4527` | Demo cũ bị loại |
| devign | test | `devign:test:7420` | `devign:train:20267` | `devign:train:23297` | Đổi thứ hạng retrieval |
| devign | test | `devign:test:9162` | `devign:train:8708` | `devign:train:23294` | Demo cũ bị loại |
| devign | test | `devign:test:9176` | `devign:train:19594` | `devign:train:25904` | Demo cũ bị loại |
| devign | test | `devign:test:9896` | `devign:train:922` | `devign:train:17890` | Demo cũ bị loại |
| devign | validation | `devign:validation:11825` | `devign:train:17432` | `devign:train:13680` | Demo cũ bị loại |
| devign | validation | `devign:validation:13552` | `devign:train:11044` | `devign:train:25790` | Đổi thứ hạng retrieval |
| devign | validation | `devign:validation:13758` | `devign:train:16034` | `devign:train:24032` | Đổi thứ hạng retrieval |
| devign | validation | `devign:validation:13833` | `devign:train:17919` | `devign:train:18106` | Đổi thứ hạng retrieval |
| devign | validation | `devign:validation:14254` | `devign:train:11068` | `devign:train:1652` | Đổi thứ hạng retrieval |
| devign | validation | `devign:validation:15476` | `devign:train:22501` | `devign:train:15437` | Đổi thứ hạng retrieval |
| devign | validation | `devign:validation:17056` | `devign:train:20383` | `devign:train:27139` | Đổi thứ hạng retrieval |
| devign | validation | `devign:validation:17157` | `devign:train:23534` | `devign:train:20572` | Đổi thứ hạng retrieval |
| devign | validation | `devign:validation:17338` | `devign:train:538` | `devign:train:17988` | Demo cũ bị loại |
| devign | validation | `devign:validation:18419` | `devign:train:21140` | `devign:train:5067` | Demo cũ bị loại |
| devign | validation | `devign:validation:188` | `devign:train:26716` | `devign:train:19694` | Đổi thứ hạng retrieval |
| devign | validation | `devign:validation:19666` | `devign:train:25438` | `devign:train:20261` | Demo cũ bị loại |
| devign | validation | `devign:validation:20098` | `devign:train:5316` | `devign:train:23915` | Đổi thứ hạng retrieval |
| devign | validation | `devign:validation:21372` | `devign:train:11904` | `devign:train:18783` | Đổi thứ hạng retrieval |
| devign | validation | `devign:validation:22895` | `devign:train:17432` | `devign:train:13680` | Demo cũ bị loại |
| devign | validation | `devign:validation:23071` | `devign:train:25964` | `devign:train:18920` | Đổi thứ hạng retrieval |
| devign | validation | `devign:validation:2326` | `devign:train:14097` | `devign:train:4131` | Đổi thứ hạng retrieval |
| devign | validation | `devign:validation:420` | `devign:train:21051` | `devign:train:9992` | Đổi thứ hạng retrieval |
| devign | validation | `devign:validation:4381` | `devign:train:8867` | `devign:train:23013` | Đổi thứ hạng retrieval |
| devign | validation | `devign:validation:443` | `devign:train:8206` | `devign:train:4657` | Đổi thứ hạng retrieval |
| devign | validation | `devign:validation:6557` | `devign:train:13144` | `devign:train:19316` | Đổi thứ hạng retrieval |
| devign | validation | `devign:validation:6960` | `devign:train:2481` | `devign:train:17886` | Đổi thứ hạng retrieval |
| devign | validation | `devign:validation:7484` | `devign:train:4620` | `devign:train:2058` | Đổi thứ hạng retrieval |
| devign | validation | `devign:validation:795` | `devign:train:9143` | `devign:train:14924` | Đổi thứ hạng retrieval |
| devign | validation | `devign:validation:9334` | `devign:train:18826` | `devign:train:17706` | Đổi thứ hạng retrieval |
| devign | validation | `devign:validation:9408` | `devign:train:1663` | `devign:train:27042` | Đổi thứ hạng retrieval |
| devign | validation | `devign:validation:9515` | `devign:train:21337` | `devign:train:26370` | Đổi thứ hạng retrieval |
| devign | validation | `devign:validation:9659` | `devign:train:10663` | `devign:train:26028` | Đổi thứ hạng retrieval |
