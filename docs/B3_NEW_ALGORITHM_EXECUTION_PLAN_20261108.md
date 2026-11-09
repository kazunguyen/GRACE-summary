# Kế hoạch triển khai B3 với thuật toán verified patch pair

Ngày lập: 08/11/2026. Mốc mã nguồn: nhánh `hieu`, sau merge commit `46e6f4ab9d0ff2c9ecac124d3a6f2bdb72524bd9`.

**Mục tiêu:** tạo một run B3 sử dụng đúng `b3-verified-patch-v1`, từ dữ liệu nguồn có thể kiểm chứng đến validation đầy đủ, tính ngưỡng mới và chạy test. Kế hoạch này chưa tạo pair được duyệt, chưa khóa đầu vào và chưa khởi chạy notebook.

**Phạm vi thực thi trước mắt chỉ có B3.** Các arm B3-nodiff, B3-swap và B3-flip được giữ trong ma trận nghiên cứu nhưng không được tự thêm vào lịch GPU của đợt này. Việc helper hiện dựng cả bốn biến thể để kiểm tra CPU không đồng nghĩa với cho phép chạy bốn arm.

## 1. Hiện trạng và các điểm phải giải quyết

Các số liệu dưới đây lấy từ bằng chứng local đã lưu, không phải cập nhật trạng thái Kaggle trực tiếp tại thời điểm đọc tài liệu.

| Hạng mục | Hiện trạng có bằng chứng | Hệ quả cho bước tiếp theo |
|---|---|---|
| Thuật toán mới | Có `VerifiedPairSelector` trong `amended_b3.py`; method ID `b3-verified-patch-v1` | Dùng module này làm nguồn triển khai, không dùng lại selector lịch sử |
| Devign clean train | 21.691 donor; 26.700 tổ hợp khác nhãn cùng project/function hint | Đây là tổ hợp cần điều tra, chưa phải patch pair |
| REVEAL clean train | 17.636 donor; 33.947 tổ hợp heuristic; cả 17.636 thiếu commit ID | Phải phục hồi nguồn gốc trước khi xác minh before/after |
| Pair đủ điều kiện | 0 pair được xác thực và duyệt trong kết quả discovery hiện có | Chưa đủ điều kiện tạo bundle inference mới |
| Thu thập nguồn Devign | 16 request trước đó đều lỗi xác minh issuer TLS | Sửa trusted CA rồi tạo lượt thu thập mới; lỗi mạng không chứng minh không tồn tại pair |
| B3 trên Kaggle | Snapshot 09:11:33 GMT+7 ngày 08/11 ghi nhận run B3-only dùng prompt lịch sử | Điểm số/checkpoint đó thuộc phương pháp cũ, không chuyển sang run phương pháp mới |
| Runtime mới nhất trong repo | Đã có SciPy 1.16.3 cùng sáu package còn lại | Bundle mới phải dùng bản contract đã chọn và được đóng dấu, không chép hash runtime cũ |
| Notebook mang tên amended | Có bản thử nghiệm và builder cũ nhúng lại một selector rút gọn | Tên notebook không chứng minh đã kiểm tra pair; phải xây delivery mới qua các cổng bên dưới |

Hai vấn đề về giao thức cần chốt bằng văn bản trước khi phát hành đầu vào:

1. **Phân loại phương pháp và ngưỡng mới.** Mã hiện ghi đây là phương pháp cho proposed amendment. Cần đối chiếu đúng bản OSF cập nhật và quyết định của PI để xác định cách báo cáo B3 mới. Chỉ ghi nhận user đã cập nhật OSF chưa đủ để kết luận nội dung phương pháp này đã được đăng ký. Bằng chứng xác nhận, phiên bản và phạm vi áp dụng phải vào hồ sơ release. Nếu chưa xác nhận, có thể tiếp tục chuẩn bị dữ liệu; chưa trình bày run mới là confirmatory đã được OSF chấp thuận.
2. **Ngân sách demonstration của B3.** `AGENTS.md` ghi demo ≤1.500 token; renderer hiện gọi `render_demos(..., budget_each=1500)` cho từng hàm và cấp thêm tối đa 500 token cho `Key difference`. Vì thế cờ `truncated=False` hiện chưa chứng minh tổng demo ≤1.500. Phải xác định cách hiểu được giao thức cho phép và ghi quyết định trước prompt freeze. Cho tới khi làm rõ, dùng tổng khối demonstration ≤1.500 làm cổng bảo thủ; nếu không đạt thì dừng để xử lý, không tự tăng budget hoặc âm thầm chia lại ngân sách. Nếu văn bản có thẩm quyền quy định 1.500 cho mỗi demo, lưu bằng chứng và cập nhật tiêu chí audit tương ứng trước khi chạy.

## 2. Chuỗi công việc và điều kiện qua từng mốc

```text
Chốt giao thức + snapshot nguồn
  → sửa TLS / phục hồi provenance
  → xác minh source before/after trong clean train
  → tạo hồ sơ pair chưa duyệt
  → hai người duyệt thật
  → khóa eligible pair pool theo dataset
  → dựng và audit toàn bộ prompt validation
  → khóa bundle + chuẩn bị notebook runtime mới
  → kiểm tra kỹ thuật GPU
  → chạy đủ validation
  → tính, kiểm tra và khóa ngưỡng riêng cho phương pháp mới
  → dựng/audit/khóa prompt test
  → chạy đủ test và nghiệm thu kết quả
```

Devign và REVEAL có thể xử lý provenance song song. Dataset nào chưa có pool hợp lệ thì giữ trạng thái blocked riêng; không lấy pair từ dataset còn lại. Chạy xong một dataset chưa phải hoàn thành B3 trên cả hai dataset.

## 3. Tổ chức hồ sơ và phân công

Tạo thư mục release mới, ví dụ `Runs-management/b3_verified_patch_v1/release_<timestamp>/`. Đây là **cấu trúc dự kiến**, hiện chưa phải bộ artifact đã tồn tại:

```text
release_<timestamp>/
  governance/                 # quyết định phạm vi, ngân sách, phân loại phân tích
  inputs_manifest.json        # hash tất cả nguồn đọc
  discovery/{devign,reveal}/   # index, candidate, trạng thái điều tra; local
  source_archive/<case_id>/    # commit, parent, file, patch, URL, hash, request log
  candidates/                 # pair chưa duyệt, lịch sử loại và lý do
  review_packets/             # phiếu và bằng chứng cho hai người duyệt
  reviews/                    # quyết định thật, thời gian, payload hash
  pools/                      # eligible_pairs.<dataset>.jsonl và pool manifest
  validation/<dataset>/       # prompt, selection, token audit, inference output
  thresholds/                 # grid MCC, candidate, lock đã được cho phép
  test/<dataset>/             # chỉ tạo sau mốc khóa ngưỡng
  runtime/                    # contract, helper, worker, notebook, build provenance
  delivery/                   # ZIP, manifest, metadata và source readback Kaggle
  acceptance/                 # biên bản kiểm tra và các vấn đề còn mở
```

File lớn chứa donor/source/index để local theo quy tắc dữ liệu hiện có. Chỉ đưa artifact được phép công bố lên Git; kiểm tra credential, token, URL tải có chữ ký và quyền công bố nguồn trước khi stage. Text mới dùng UTF-8 không BOM. Hash nguồn tính trên byte gốc; phép chuẩn hóa dùng để chẩn đoán không được ghi đè artifact nguồn.

| Người thực hiện | Công việc |
|---|---|
| Mô hình chính | Chốt đặc tả từ tài liệu, giao việc, xem mã, đánh giá bằng chứng, kiểm tra hash/census và nghiệm thu |
| AGY workers | Sinh công cụ theo schema, bộ kiểm tra độc lập, biểu mẫu và báo cáo kỹ thuật trong phạm vi được giao |
| Công cụ chạy local | Đọc bank, lập index, đối chiếu byte/hash, tải nguồn công khai bằng HTTPS đã xác thực, tạo packet |
| Hai reviewer là người thật | Xác nhận cùng hàm, quan hệ sửa lỗi bảo mật, revision, nội dung giải thích và quyết định pair |
| PI/người có thẩm quyền | Giải quyết vấn đề giao thức, cách diễn giải budget, phân loại phân tích và việc phát hành ngưỡng mới |

Giữ mô hình AGY đã dùng hoặc chọn lại sau khi kiểm tra danh sách CLI. Không gọi GPT subagent. AGY chỉ nhận schema và tác vụ sinh mã theo workflow đã chấp nhận; không gửi bank, index, candidate riêng tư hoặc credential cho worker. SUCCESS của AGY chỉ được nghiệm thu khi có artifact và đã kiểm tra; `denied_actions` hoặc output rỗng phải ghi blocked. Xem [quy tắc AGY](AGY_ORCHESTRATION.md).

## 4. Bước 1 — Lập snapshot nguồn và kiểm tra các ràng buộc

1. Ghi commit, trạng thái working tree, ngày giờ và phiên bản Python dùng cho chuẩn bị dữ liệu.
2. Ghi hash các module selector, token normalization, renderer, token counter, runtime contract và công cụ chuẩn bị.
3. Kiểm SHA freeze manifest `e1d3c6b17c3a0b5c1e05203794d48a33825e0ea00a55deaaef565af25efe0448`; kiểm tiếp file hash được khai báo bên trong.
4. Kiểm `train_raw.jsonl` và `train_manifest.jsonl` cho hai dataset: ID duy nhất, code hash và label đúng, `split=train`, `keep_in_bank=true`.
5. Xác nhận đúng 21.691 Devign và 17.636 REVEAL donor; ghi danh sách/hash vào manifest local.
6. Xác định tokenizer snapshot đúng revision `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`, lưu hash từng file cần dùng.
7. Lưu quyết định về hai vấn đề ở mục 1. Không sửa các file preregistration, arm, frozen specs, bank và threshold bị đóng băng để giải quyết chúng.

**Đầu ra:** input manifest có seal, governance record, danh sách nguồn chuẩn. **Qua bước khi:** hash/census đúng và không có nguồn chưa xác định. Sai hash phải dừng, tìm đúng artifact gốc trước khi tiếp tục.

## 5. Bước 2 — Sửa đường truy cập nguồn HTTPS

1. Chẩn đoán Python SSL, CA bundle, cấu hình proxy và trusted certificate store đang được sử dụng. Khi ghi log chỉ ghi cấu hình cần thiết; che thông tin xác thực.
2. Chọn CA tin cậy hoặc cấu hình HTTPS hợp lệ theo môi trường máy; giới hạn thay đổi trong tiến trình/công cụ thu thập khi có thể.
3. Xác nhận request HTTPS tới nguồn công khai thành công với kiểm tra chứng chỉ và hostname bật. Không dùng `verify=False` hay SSL context bỏ xác minh.
4. Giữ nguyên folder 16 request lỗi cũ. Chạy lượt mới trong folder mới, ban đầu giới hạn như lượt trước: tối đa 16 request cho nhóm nhỏ Devign.
5. Lưu URL công khai, thời gian UTC, HTTP status, hash response, lỗi, giới hạn request và phiên bản công cụ. Dừng khi gặp rate limit theo chính sách công cụ.
6. Đọc response thật, xác định đã lấy được commit metadata/patch hay chỉ là trang lỗi hoặc dữ liệu bị cắt.

**Đầu ra:** lượt recon có response kiểm tra được hoặc báo cáo blocker rõ ràng. **Qua bước khi:** đã có dữ liệu nguồn dùng được. HTTP 200, commit message và quan hệ parent riêng lẻ chưa đủ để duyệt pair.

## 6. Bước 3 — Điều tra pair Devign

1. Dùng candidate inventory local làm chỉ mục điều tra. Các tổ hợp cùng tên hàm chỉ giúp tìm nguồn; tên giống nhau không xác lập quan hệ before/after.
2. Với mỗi case, tìm đúng repository, đường dẫn file, function và revision. Kiểm tra quan hệ giữa commit trong dữ liệu với fix commit; không mặc định donor commit chính là fix commit.
3. Tải commit sửa lỗi, parent tương ứng và patch thực. Với merge commit phải chỉ rõ parent đang đối chiếu và lý do chọn.
4. Lấy file nguồn đầy đủ ở parent và fix, rồi trích đúng hàm. Giữ bản file đầy đủ bên cạnh phần trích để reviewer có thể kiểm tra ranh giới hàm.
5. Tìm hai donor trong clean train khớp chính xác phần hàm trước/sau: trước nhãn 1, sau nhãn 0, khác ID, cùng dataset.
6. Đối chiếu byte/hash với bank. Nếu upstream và bank khác whitespace, tiền xử lý hay macro, ghi `UNRESOLVED_SOURCE_MAPPING`; chưa đưa vào pool. Không tự chuẩn hóa bank để tạo khớp.
7. Xác minh patch thật có các dòng thay đổi được hiển thị trong function diff; không dùng diff tự sinh từ hai hàm bất kỳ để thay patch nguồn.
8. Thu thập nguồn hỗ trợ lý do sửa lỗi bảo mật: commit, advisory, issue hoặc tài liệu nguồn phù hợp. Không suy luận chỉ từ từ khóa như `NULL`, `memcpy`, `sizeof`.
9. Ghi một trạng thái cho mỗi case: đang điều tra, thiếu nguồn, không cùng hàm, không có đủ hai donor, không chứng minh được sửa lỗi bảo mật, hoặc sẵn sàng tạo packet.

Nếu tìm được upstream patch nhưng một phía không nằm trong bank thì loại case khỏi pool hiện tại. Việc bổ sung donor ngoài bank là thay đổi phương pháp cần quyết định riêng. Không được coi việc điều tra vài case không thành công là kết luận toàn Devign không có pair.

**Đầu ra:** source archive, bảng ánh xạ donor ↔ source revision và nhật ký quyết định. **Qua bước khi:** từng case đưa sang review có đủ hai phía trong clean train và bằng chứng nguồn thực.

## 7. Bước 4 — Phục hồi provenance REVEAL

1. Xác định đúng phiên bản dữ liệu gốc và pipeline đã tạo export đóng băng. Giữ `source_id` dưới dạng chuỗi; không ép về integer nếu làm mất dấu hay định dạng.
2. Tìm metadata gốc/manifest/mã chuẩn bị có thể ánh xạ `source_id` tới repo, path, revision và function. Ghi hash nguồn ánh xạ, phiên bản và cách join.
3. Kiểm tra join có duy nhất không. Case thiếu mapping hoặc có nhiều mapping phải giữ unresolved, không chọn một kết quả tùy ý.
4. Kiểm tra lại code hash và nguồn dataset để chứng minh mapping thuộc đúng donor. Trường project chung như `debian` không thay thế URL repo hoặc revision.
5. Tạo provenance sidecar trong release mới; không điền lại vào frozen `train_raw.jsonl` hay `train_manifest.jsonl`.
6. Khi phục hồi đủ thông tin cho một case, thực hiện quy trình xác minh source before/after như bước 3.
7. Báo cáo số donor mapping được/không được, số case đủ hai phía và nguyên nhân loại. Chỉ dùng nguồn gốc thật; không suy revision từ tương đồng code đơn thuần.

**Qua bước khi:** có case REVEAL đáp ứng cùng tiêu chuẩn nguồn và donor như Devign. Nếu vẫn không có pool, giữ REVEAL blocked và trình PI các lựa chọn phương pháp; không dùng pair Devign hoặc tạo evidence giả để lấp chỗ trống.

## 8. Bước 5 — Tạo pair candidate đúng schema

Dùng `make_pair_candidate` từ module chuẩn để tạo candidate **chưa duyệt**. Các trường dưới đây phải có trong record hoặc nguồn tương ứng:

| Nhóm | Trường chính |
|---|---|
| Danh tính | `dataset`, `pair_id` ổn định, `vulnerable_id`, `patched_id` |
| Byte/hash | `before_sha256`, `after_sha256`; hai hàm khớp đúng donor |
| Nguồn | `source.repository`, `path`, `function`, `source_url`, `fix_commit`, `parent_commit` |
| Nội dung bằng chứng | `source.before`, `after`, `fix_diff`, `diff`, `security_rationale` |
| Giải thích | `changed_lines`, `key_difference` được sinh từ thay đổi thực và rationale |
| Review | `reviews: []` ở giai đoạn candidate |

Fix/parent dùng SHA đầy đủ 40 ký tự hex, khác nhau. `source.fix_diff` phải là patch nguồn thực, có header `--- a/<path>` và `+++ b/<path>` phù hợp; `source.diff` là function diff do helper tạo. Hai trường này có nhiệm vụ khác nhau.

Chạy `validate_pair(..., require_reviews=False)` để kiểm tra cấu trúc và tính nhất quán local. Cổng này không xác nhận nguồn thật hay ý nghĩa bảo mật. Nếu parser `function_hint` không nhận đúng macro/tên hàm, ghi blocker và xử lý bằng thay đổi mã được review; không tự ghi tên khác vào evidence để vượt validator.

**Đầu ra:** candidate JSONL, hồ sơ nguồn và lỗi validation. Mỗi lần thay bằng chứng phải tạo phiên bản/payload mới có thể truy vết.

## 9. Bước 6 — Hai người duyệt thật và khóa eligible pool

1. Tạo packet cho từng case: hai donor ID/label/hash, nguồn parent/fix, file đầy đủ, hai hàm, actual patch, function diff, changed lines và `Key difference`.
2. Tính `payload_hash(pair)` trên toàn record trừ `reviews`, theo UTF-8 JSON với `sort_keys=True`, `ensure_ascii=False`, `separators=(',', ':')`.
3. Hai reviewer khác nhau kiểm tra độc lập bốn nội dung: cùng hàm, sửa lỗi bảo mật, revision nguồn và giải thích được evidence hỗ trợ.
4. Mỗi review có `reviewer`, `reviewed_at`, `decision`, `payload_sha256` và bốn boolean `same_function_verified`, `security_fix_verified`, `source_revisions_verified`, `explanation_supported`.
5. Chỉ record có đúng hai review approve, bốn kiểm tra đều true và payload hash hiện hành mới đi qua `validate_pair` mặc định.
6. Bất đồng/chưa đủ bằng chứng: giữ unresolved hoặc reject. Nếu sửa rationale, code hay evidence sau review, phải tính lại payload và duyệt lại; không dùng chữ ký cũ.
7. Tạo pool riêng cho Devign và REVEAL; kiểm tra pair ID duy nhất, donor membership, nhãn, source hashes và absence of synthetic fixtures.
8. Khóa pool manifest: hash JSONL, danh sách pair/payload hash, quyết định loại, phiên bản tiêu chí chọn pool, nguồn mã và thời điểm freeze.

Không đặt ra một số pair tối thiểu tùy ý để gọi đủ chất lượng. Pool không rỗng là điều kiện kỹ thuật cần; PI cần đánh giá thêm độ phủ/độ đại diện và các giới hạn của pool trước inference. Tiêu chí xây pool phải được chốt dựa trên dữ liệu nguồn/train, trước khi xem validation score. Không thay pool sau khi biết accuracy/MCC.

**Đầu ra:** pool đã seal và biên bản dual review. **Dừng nếu:** pool rỗng, review giả/thiếu/cũ hoặc bất kỳ pair nào không còn hợp lệ.

## 10. Bước 7 — Kiểm tra selector và renderer trước khi mở GPU

1. Dùng trực tiếp `VerifiedPairSelector` trong module chuẩn, không viết lại phiên bản đơn giản trong notebook.
2. Kiểm lại ranking cho target bằng trung bình hai token-set Jaccard:

   `score(q,pair) = (J(q,before) + J(q,after)) / 2`.

   Dùng normalization hiện hành, duyệt toàn bộ eligible pool, số hữu tỉ `Fraction`, hòa thì `pair_id` tăng dần. Lưu tử số/mẫu số; số float chỉ phục vụ hiển thị.
3. Selector chỉ nhận code target; interface render chỉ nhận `id`, `query_code`, `nodes`, `edges`. Tách target label và demo cũ ra khỏi đường dựng prompt.
4. Kiểm lỗi chủ đích: pool rỗng, pair hỏng, source/hash/review sai, tie, target label lọt interface, demo/explanation bị cắt và prompt vượt context phải bị phát hiện.
5. Dùng tokenizer đúng revision, `counter.approx=False`; kiểm cả chat template và token IDs cuối cùng đưa vào backend.
6. Đối chiếu ngân sách theo quyết định ở mục 1: target ≤3.000, graph ≤1.500, demo theo diễn giải đã được chốt, reserve 64 và toàn prompt sau template + reserve ≤8.192.
7. Pair được selector chọn mà không vừa ngân sách thì dừng và ghi lỗi. Không chọn pair đứng thứ hai, không cắt donor/changed lines/giải thích để tiếp tục.

Các kiểm tra cần chạy khi triển khai mã, không phải chỉ ghi “đã test” trong manifest:

```powershell
python -m pytest tests/test_amended_b3.py
python -m pytest tests/test_preregistration_integrity.py
python -m pytest 01_Author_Baseline_Unified/diagnostic_kit/tests/test_probes.py
python -m pytest 01_Author_Baseline_Unified/diagnostic_kit/tests/test_stats_and_complementarity.py
```

Script kiểm tra dữ liệu thật hiện có:

```powershell
python Runs-management/b3_amended_20261106/check_b3.py --pairs PATH_TO_REVIEWED_PAIRS.jsonl --tokenizer PATH_TO_PINNED_SNAPSHOT --samples 3 --out PATH_TO_NEW_CHECK_FOLDER
```

Đây là lệnh **CPU sample check**, chưa tạo full bundle. Đổi các placeholder thành đường dẫn thật; output folder phải mới. Script hiện dùng `hashlib.file_digest`, cần Python ≥3.11 hoặc sửa helper có review để chạy trên Python 3.10 local. Nó dựng cả family để kiểm tra renderer; lịch GPU vẫn chỉ chứa B3.

## 11. Bước 8 — Dựng và audit toàn census validation

1. Viết công cụ full-census builder mới hoặc mở rộng công cụ sample đã review. Không coi `--samples 3` là xác nhận đủ tập validation.
2. Đọc ID/code/graph validation từ specs đóng băng, kiểm code và census với validation manifest gốc; không dùng demo cũ hay label để chọn pair.
3. Dựng B3 cho đúng **2.732 Devign + 2.273 REVEAL = 5.005 target**. Nếu một dataset blocked thì báo cáo trạng thái riêng; không lấp hàng bằng prompt thuật toán cũ.
4. Mỗi record giữ method ID, dataset/split/seed, target ID, prompt SHA, pool SHA, pair ID/payload SHA, selection score chính xác, tokenizer/renderer SHA và token audit.
5. Audit 100% ID duy nhất, đúng tập ID, prompt order Figure 6: role → target code → question → node → edge → demonstration → answer.
6. Audit hai donor và `Key difference` hiển thị trọn vẹn; nhãn demo đúng; target label không được đưa vào prompt/selection. Không coi regex bắt từ “Vulnerable” của demo là rò nhãn target.
7. Dựng lại một lượt độc lập và so hash theo ID; prompt/order/selection phải tái lập.
8. Lập mẫu đọc thủ công có quy tắc chọn trước, bao gồm các pair được dùng, trường hợp gần giới hạn token, graph rỗng và case selector hòa. Ghi reviewer và lỗi thực; không tự đặt toàn nghiên cứu đạt chỉ từ CPU pass.
9. Chỉ sau khi không còn lỗi chưa giải quyết mới seal prompt manifest và bundle validation. Mọi thay đổi pool/renderer sau mốc này tạo version mới và phải audit lại trước inference.

Không khảo sát target test hoặc test score để sửa pool/renderer trước bước này. Việc preflight hình thức validation phát hiện prompt không vừa ngân sách cần được xử lý bằng quyết định được ghi trước inference; không lặp chọn pool theo kết quả mô hình.

## 12. Bước 9 — Chuẩn bị notebook B3-only và runtime release mới

**Không chạy trực tiếp builder `Runs-management/build_and_launch_b3_amended_kaggle.py` như delivery chuẩn.** Builder này có code nhúng riêng: constructor selector lấy donor từ ID mà không gọi đầy đủ `validate_pair`, renderer tự dựng prompt và có đường launch. Phải thay bằng delivery được kiểm tra, dùng module chuẩn ở CPU preparation và prompt đã freeze ở GPU.

Notebook mới cần có các khối sau:

1. Khai báo run ID mới, chỉ arm B3, method `b3-verified-patch-v1`, dataset/split/census và hash manifest kỳ vọng.
2. Tìm input Kaggle theo danh tính/hash, hỗ trợ ZIP hoặc thư mục đã giải nén; nhiều input khớp hoặc thiếu input phải dừng.
3. Xác minh bundle, prompt, pool, worker, helper và runtime contract trước nạp model; không tự dựng lại demo trên Kaggle.
4. Cài package đúng contract đã seal; kiểm phiên bản thực sau cài đặt.
5. Kiểm model/tokenizer, nạp model, thu log native và kiểm các gate runtime.
6. Preflight token IDs, chạy scoring, ghi record/checkpoint bền vững.
7. Graceful exit theo thời gian, đóng gói output, ghi manifest và provenance.

Các package trong contract hiện tại:

| Package | Version |
|---|---|
| llama-cpp-python | 0.3.16 |
| transformers | 4.57.1 |
| huggingface-hub | 0.36.2 |
| tokenizers | 0.22.2 |
| numpy | 2.1.3 |
| scipy | 1.16.3 |
| scikit-learn | 1.5.2 |

Model GGUF Q4_K_M SHA-256: `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`. Backend sdist SHA-256: `34ed0f9bd9431af045bb63d9324ae620ad0536653740e9bb163a2e1fcb973be6`.

Lấy constructor, build, thread và platform policy từ **bản contract đã chọn để đóng gói**: Python 3.13/Kaggle Linux, hai Tesla T4, `n_ctx=8192`, `n_batch=n_ubatch=256`, `n_gpu_layers=-1`, layer split, `tensor_split=None`, `main_gpu=0`, logits toàn vocabulary, cấu hình flash/mmap/mlock/offload và seed đúng contract. Với scoring trực tiếp không sampling, không tự thay constructor seed sentinel bằng seed prompt 42. Lưu hai giá trị riêng và giải thích vai trò.

Ghi cả hash byte contract giao thực tế và seal canonical của payload; không so một file CRLF với hash LF rồi sửa hash để qua gate. Tạo trước bản delivery byte ổn định, tính hash trên đúng bản đó, pin bản đó trong notebook và manifest. Contract hiện có seal canonical `d79396de5d37ca6c3123ac05ea122d665f5f9b252aa0b32ac2b5c464b68e338f`; phải tính lại để kiểm tra thay vì chỉ chép chuỗi này.

Nguồn worker continuation cũ có thể tham khảo phần checkpoint/provenance nhưng không dùng nguyên xi: nó gắn workflow cũ và threshold lock khi chạy test. Adapter cho B3 mới phải hỗ trợ validation chưa có threshold, method/pool mới và cấm legacy score migration vào run mới. Ghi mọi sửa mã vào `CHANGES_AFTER_PREREG.md` khi thực hiện.

## 13. Bước 10 — Kiểm tra kỹ thuật GPU và lịch account

1. Kiểm quota và trạng thái account trước khi launch. Ưu tiên account đang được gom B3 cùng B1-full là `huuhieu3333`, nếu quota và số phiên cho phép; tránh tự phân tán sang account khác.
2. Một notebook yêu cầu một runtime **T4×2**; hai notebook đồng thời là hai runtime riêng. Ghi machine shape thực từ API/source readback; không suy số GPU từ tên notebook hoặc trạng thái RUNNING.
3. Tạo kernel slug/version mới cho amended B3; giữ source/output historical B3 riêng. Việc xử lý run lịch sử đang hoạt động cần quyết định lịch rõ ràng; không tự hủy để lấy slot.
4. Trước submit, kiểm notebook JSON/cell syntax, package lock nhúng, hash worker/helper, danh sách chỉ có B3 và input dataset version.
5. Sau submit, đọc lại notebook source/metadata trên Kaggle; đối chiếu hash/cell và machine shape với delivery đã ký.
6. Chạy thử kỹ thuật bằng synthetic fixture hoặc replay riêng; đánh dấu riêng output, không trộn với census. Nếu dùng những target validation đầu tiên làm kiểm tra vận hành, không chọn/sửa phương pháp theo score; chỉ giữ chúng trong census khi danh tính toàn bộ run khớp và policy đã cho phép.
7. Nghiệm thu model SHA, bảy package sau cài đặt, sdist trước build, Python/CUDA/driver/compiler/CMake/build flags, hash backend đã build và thread settings.
8. Native log phải xác nhận hai T4 và offload **49/49 layer**, context/batch đúng. Parser phải hiểu format thực nhưng vẫn từ chối thiếu GPU/thiếu layer; không bỏ assertion khi log khác mẫu.
9. Thử checkpoint/resume có kiểm danh tính, graceful exit và tải lại artifact trước khi cấp trạng thái sẵn sàng full validation.

**Qua bước khi:** source đúng và runtime gates có bằng chứng thực. T4×2 được request, RUNNING hay setup không lỗi đều chưa đủ để tuyên bố runtime-lock pass.

## 14. Bước 11 — Chạy full validation mới và resume

1. Bắt đầu census mới từ 0 score: Devign 2.732, REVEAL 2.273. Không nhập 4.029/4.058 score lịch sử hoặc threshold B3 cũ vào phương pháp mới.
2. Trước từng inference, kiểm prompt hash/token IDs theo delivery; reset/eval theo scoring chuẩn.
3. Lấy logits token `0` và `1`, tính ổn định bằng float64:

   `s = exp(logprob_1 - logaddexp(logprob_0, logprob_1)) = sigmoid(logit_1 - logit_0)`.

   Không lấy xác suất từ câu trả lời sinh tự do. Kiểm label token IDs và vị trí logits thật, không tự giả định hai token ID.
4. Lưu từng record: ID, score/logprobs, valid/reason, prompt/method/pool/model/runtime identity, session ID và thời gian. Không ghi accuracy hoặc chọn ngưỡng khi validation còn thiếu.
5. Flush/fsync từng record, checkpoint khoảng 60 giây và ở cuối phiên. Với lịch 9 giờ, giữ ít nhất 300 giây để đóng gói, đồng thời tính thời gian setup vào giới hạn phù hợp nền tảng.
6. Resume chỉ nhận record trùng phương pháp, prompt, pool, model, tokenizer, scoring và runtime release. Một ID có hai score khác nhau phải bị phát hiện và điều tra; không âm thầm lấy bản thuận lợi hơn.
7. Runtime đổi do sửa package/worker/constructor: tạo quyết định và provenance mới trước resume, không sửa nhãn provenance cũ. Đợt đầu nên giữ một release runtime nhất quán cho full validation và test.
8. Sau mỗi phiên tải loose records, checkpoint, log và manifest; kiểm CRC ZIP, hash và chênh số record. Chỉ tính tiến độ từ ID đã xác minh.

**Nghiệm thu validation:** đúng 5.005 ID kỳ vọng, không trùng/ngoài tập, nhãn đánh giá đúng manifest riêng, score kiểm lại được, mọi record có provenance. Record score-invalid phải được xử lý theo policy đã chốt; không tự điền 0,5 hoặc fit trên subset thuận tiện. Nếu không có quy tắc hợp lệ cho tình huống đó, dừng khóa ngưỡng để xử lý.

## 15. Bước 12 — Tính ngưỡng mới và phát hành lock riêng

Chỉ bắt đầu khi full validation đã nghiệm thu. Dùng score của **chính run B3 mới**, không lấy số từ tài liệu hay optimizer output của phương pháp cũ.

1. Đối chiếu ID/label/valid với validation manifest. Tách rõ raw response-invalid và numeric score-invalid; raw response không đúng định dạng không tự làm mất score logits hợp lệ.
2. Quét độc lập 99 ngưỡng `τ=i/100`, `i=1..99`; dự đoán 1 khi `s >= τ`.
3. Với mỗi ngưỡng lưu TP/TN/FP/FN và:

   `MCC = (TP·TN − FP·FN) / sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN))`.

4. Bỏ ngưỡng MCC không xác định. Chọn MCC lớn nhất; hòa trong `1e-9` thì gần 0,5 nhất, sau đó lấy ngưỡng thấp hơn. Nếu không còn ngưỡng hợp lệ thì dừng.
5. Đối chiếu toàn bộ grid bằng cách tính độc lập thứ hai với optimizer hiện hành, không chỉ so ngưỡng thắng.
6. Ghi candidate artifact riêng cho mỗi dataset: method/pool/prompt/model/runtime hashes, validation records hash, full census, valid count, grid, tie và τ được tính.
7. Review tính toán và xác nhận quyền áp dụng ngưỡng phương pháp mới theo governance record. Sau đó seal lock riêng trong release và pin nó cho evaluator test.
8. Không sửa `configs/thresholds.json`, `configs/thresholds_flat.json` hoặc mirror đóng băng. Nếu runner hiện chỉ đọc các file đó, bổ sung đường đọc lock riêng được kiểm hash thay vì sửa file lịch sử.

Chưa thể biết τ mới trước khi có score mới. Không lấy τ lịch sử làm mặc định để gọi run amended đã khóa. Nếu sau này triển khai probe, swap/flip kế thừa τ của B3 mới; nodiff cần validation riêng. Đó là công việc ngoài lịch GPU hiện tại.

## 16. Bước 13 — Dựng, khóa và chạy test

1. Sau khi phát hành lock validation, dùng nguyên pool/selector/renderer/tokenizer/runtime release để dựng test: **2.732 Devign + 2.274 REVEAL = 5.006 target**.
2. Chỉ dùng target ID/code/graph cho prompt; nhãn test được giữ trong đường đánh giá riêng.
3. Audit census, hash, Figure 6, source evidence và toàn bộ token budgets như validation. Có lỗi thì dừng trước inference và ghi deviation; không bỏ target để đạt census giả.
4. Nếu lỗi buộc đổi pool/renderer sau khóa validation, đánh giá ảnh hưởng và làm lại validation/threshold cần thiết trước khi chạy test với phiên bản mới. Không dùng test score để quyết định thay đổi.
5. Seal test bundle cùng threshold lock mới. Notebook/evaluator phải abort nếu threshold checksum hoặc method/pool identity không khớp.
6. Chạy B3-only fresh census, resume theo cùng quy tắc bước 11. Dừng theo thời gian hạ tầng rồi resume được phép; dừng theo metric trung gian không được phép.
7. Tải output sau từng phiên và nghiệm thu đủ 5.006 ID trước khi báo cáo final test. Không dùng score phương pháp cũ để bù số lượng còn thiếu.

## 17. Bước 14 — Nghiệm thu, báo cáo và lưu Git

Checklist nghiệm thu cuối:

- [ ] Bằng chứng giao thức/OSF và cách phân loại B3 mới đã được ghi rõ.
- [ ] Hai pool chỉ chứa clean-train donor của đúng dataset và hai review thật còn hiệu lực.
- [ ] Pool/selector/renderer/tokenizer/prompt/runtime release có hash và version rõ.
- [ ] Mỗi prompt truy ngược được tới pair, source patch, changed lines và review payload.
- [ ] Ngân sách demo đã được giải quyết bằng văn bản; 100% prompt đạt audit cuối.
- [ ] Bảy package, model SHA, build provenance, T4×2, 49/49 và scoring có bằng chứng thực.
- [ ] Validation đủ 5.005 ID; threshold được tính lại từ score mới, lưu full grid và seal riêng.
- [ ] Test đủ 5.006 ID; threshold áp dụng đúng lock mới; không trộn kết quả lịch sử.
- [ ] Metric được tính lại từ records; full official census và clean near-deduplicated partition được báo cáo theo quy định.
- [ ] Nếu đưa vào Table B: contrast đúng phiên bản, paired cluster bootstrap và Holm đúng protocol; chưa đủ điều kiện thì ghi pending, không gọi metric mô tả là kết luận confirmatory.
- [ ] Có nhật ký deviation, worklog, nguồn thời gian, account/kernel/version, checkpoint parent và acceptance report.
- [ ] Artifact công bố không chứa credential, signed download URL hoặc dữ liệu chưa được phép công bố; byte hash nguồn được giữ nguyên.

Khi triển khai, mọi sửa lỗi/công cụ/runtime và deviation phải ghi ngày, lý do, phân tích bị ảnh hưởng và phân loại trong `CHANGES_AFTER_PREREG.md`. Cập nhật run ledger theo bằng chứng thật, phân biệt prepared/running/checkpointed/complete/accepted. Chỉ commit/push artifact đã kiểm tra trên nhánh làm việc; giữ nguyên protected branch/tag.

## 18. Các việc làm ngay theo thứ tự ưu tiên

| Thứ tự | Việc cụ thể | Sản phẩm cần có trước khi chuyển bước |
|---|---|---|
| 1 | Chốt diễn giải budget demo và kiểm tra nội dung amendment áp dụng cho B3 mới | Governance record và tiêu chí audit |
| 2 | Lập snapshot release, kiểm bank/tokenizer/source hashes | Inputs manifest có seal |
| 3 | Sửa trusted CA; chạy lại nhóm Devign nhỏ trong output mới | Response nguồn đọc được, request log và hash |
| 4 | Song song phục hồi REVEAL source mapping bằng dữ liệu gốc | Provenance sidecar, báo cáo ambiguous/missing |
| 5 | Chứng minh case before/after thực trong clean train | Source archive và candidate pass kiểm tra local |
| 6 | Chuẩn bị packet và thu hai review thật | Eligible pair pool theo dataset |
| 7 | Xử lý budget/renderer, kiểm selector rồi dựng full validation | 5.005 prompt audit pass, manifest đóng băng |
| 8 | Tạo delivery B3-only với runtime bảy package và kiểm GPU | Source readback đúng và runtime acceptance |
| 9 | Chạy đủ validation, tính lại và phát hành ngưỡng riêng | Validation acceptance + threshold release |
| 10 | Dựng/audit test rồi chạy đủ census | Test acceptance và báo cáo kết quả mới |

Không cam kết ngày hoàn thành trước khi biết khả năng phục hồi provenance và lịch của hai reviewer. Có thể ước lượng GPU sau lượt kiểm tra runtime từ throughput thực, phần setup và quota; không lấy tốc độ notebook cũ làm bảo đảm cho release mới.

## 19. Tài liệu và mã nguồn đối chiếu

- [Đặc tả và giới hạn amended B3](../Runs-management/b3_amended_20261106/README.md).
- [Selector và schema kiểm tra pair](../01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/amended_b3.py).
- [Renderer và ngân sách hiện hành](../01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/probes.py).
- [Kiểm dữ liệu thật trên CPU](../Runs-management/b3_amended_20261106/check_b3.py).
- [Tests thuật toán B3 mới](../tests/test_amended_b3.py).
- [Runtime contract hiện hành](../configs/inference_runtime_lock.json).
- [Kết quả nghiệm thu AGY/discovery đã lưu](../Runs-management/agy_b3_safe_codegen_20261108/coordinator_review.json).
- [Handoff và trạng thái lịch sử ngày 08/11](../Runs-management/run_handoff_20261108/RUN_STATUS.md).
- [Quy tắc điều phối AGY](AGY_ORCHESTRATION.md).
- [Quy tắc tính threshold đã được audit](../scripts/audit_validation_thresholds_20261108.py).

Các tên thư mục release, manifest và artifact mới trong kế hoạch là đề xuất cần tạo khi thực thi. Chỉ các đường dẫn ở phần đối chiếu và các lệnh nêu rõ hiện có mới được coi là công cụ sẵn có; chưa có một lệnh tự động end-to-end đã được nghiệm thu cho quy trình B3 mới.
