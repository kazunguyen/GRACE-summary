# Đối chiếu runtime theo phiên — 10/11/2026

**Đã đối chiếu lại artifact hiện có, không chỉ đọc kết luận audit trước.** Inventory có 265 file records và 88 hash file khác nhau. Bản sao/snapshot không được tính là phiên inference mới. Ledger và bằng chứng tính toán nằm trong [SESSION_RECONCILIATION.json](SESSION_RECONCILIATION.json), bảng tra trong [SESSION_LEDGER.csv](SESSION_LEDGER.csv).

## Kết luận

| Phạm vi | Kết luận của lượt đối chiếu này |
|---|---|
| B2-nolabel / B2-labelonly / B2-rep test | Gắn được đủ 15.018 record vào sáu tiến trình. Đạt kiểm tra records, model, score, process log và thời gian; **chưa chứng nhận full runtime lock** do thiếu native placement và provenance của chính tiến trình test. |
| Validation của ba arm trên và B1-full | Native log có T4×2, offload 49/49 và context/batch/ubatch khớp, thời gian record gắn đúng phiên; thiếu source/build/contract provenance đầy đủ. |
| B1-shuf validation | Log phiên seed44 gắn được 619 Devign + 2.273 REVEAL. 2.113 Devign carry-over cùng toàn bộ seed42/43 chưa có process log tương ứng trong gói đang kiểm. |
| B2-rand test | 15.018 final record gán được về bốn phiên head/tail bằng equality toàn record. Phục hồi source/lock đúng byte từ Git blob. Provenance khớp; native/build log gốc chưa có để replay hash nên chưa chứng nhận lại full lock. |
| B3 thuật toán lịch sử | **Nghiệm thu runtime theo launch contract cho đúng 29 + 947 = 976 record resume**. 4.029 record lịch sử không có session provenance vẫn chưa được chứng nhận. |
| B0 / B1 / B2 / B2-flip / B1-H2 | Đã đối chiếu saved notebook outputs và raw record hiện còn; giới hạn theo từng phiên được ghi ở mục 6. Chưa đủ căn cứ tuyên bố toàn bộ kết quả của các arm này tuân thủ lock mới. |
| B1-full test / B1-shuf test / B3-new validation | Giữ nguyên các biên bản nghiệm thu riêng đã có; không mở rộng phạm vi chứng nhận từ test sang validation hoặc từ một phiên sang toàn bộ lịch sử. |

Không tự kết luận phải rerun vì thiếu chứng cứ. Giữ nguyên output; phục hồi artifact còn thiếu và chốt cách báo cáo giới hạn trước khi quyết định một đợt GPU khác.

## 1. Chuẩn và cách kiểm

Đối chiếu với ZIP `grace_hieu_5arms_runtime_locked_20261107.zip`, SHA-256 `76a49a770897b7d0832ee87aa7d7e308ebbca57fdd7aaaf02f0f07f2400f156c`, cùng amendment pin SciPy 1.16.3 đã ghi trong worklog ngày 07/11.

Mỗi phiên được kiểm theo đúng contract lúc launch:

- Sáu package, Linux LF: `85d8770839f80260cdc7c27b27b6cce6bf8815675c8593db68fb102589c5cbd6`.
- Bảy package, Linux LF: `bf1f859dc786e206a3c11d655b04b528dc68f59a15a82d4db894ac5944b0ac2e`.
- Bảy package, CRLF đã được niêm phong cho B3-new: `4c9c3bcff5e9fd32532d7edf85df7a961e45ec9c64bee3df8833d986a2eb276e`.

Kiểm hash source/lock, model/tokenizer identity, package/constructor, native GPU/offload, source/build provenance, dependency freeze và effective threads. Records được gắn vào đúng tiến trình bằng cửa sổ `events.log`, ID/score trong process log hoặc provenance reference/hash. Tính lại `s=sigmoid(logprob_1-logprob_0)`; không fit threshold.

`PARTIAL` có nghĩa chỉ đóng được các mục có chứng cứ. Cấu hình source, install log, wheel hash và native execution log là các mức bằng chứng khác nhau. Không dùng native log validation để chứng nhận test. Model hash và compiled-library hashes do verified runner ghi là attestation của phiên; không tuyên bố đã đọc lại GPU memory hoặc tái dựng binary giống từng byte.

## 2. Ba arm ưu tiên: sáu tiến trình test

| Phiên | N | Timestamp nằm trong process window | ID + score hiển thị trong process log | Hash records khớp manifest |
|---|---:|---:|---:|---|
| B2-nolabel / seed42 / Devign test | 2.732 | 2.732 | 2.732 | Có |
| B2-nolabel / seed42 / REVEAL test | 2.274 | 2.274 | 2.274 | Có |
| B2-labelonly / seed42 / Devign test | 2.732 | 2.732 | 2.732 | Có |
| B2-labelonly / seed42 / REVEAL test | 2.274 | 2.274 | 2.274 | Có |
| B2-rep / seed42 / Devign test | 2.732 | 2.732 | 2.732 | Có |
| B2-rep / seed42 / REVEAL test | 2.274 | 2.274 | 2.274 | Có |

Ngày/giờ bắt đầu và kết thúc từng tiến trình nằm trong ledger JSON/CSV, lấy từ log, không lấy mtime. Mỗi arm chạy hai tiến trình load model riêng. B2-rep có `repeat=true`, `tag=repeat` ở mọi record; command thực có `--repeat --tag repeat`.

Tìm lại được session log gốc và diagnostics ZIP, đóng thêm các mục build sau:

| Arm | Wheel SHA-256 được pip ghi sau build | CMake build |
|---|---|---|
| B2-nolabel | `f677541ab72fdf8204d91761ffaa5d0809ed2df1adab2c7a7a4c913ac015ded5` | 4.4.4 |
| B2-labelonly | `799e8bf3abd74447f4b6c3edc3fff0780d3ff6276c695c5ff7eaa63645d1c172` | 4.4.4 |
| B2-rep | `4783fc2f00294b645144baced114d5cea1eef7ca42bc25f546a801a41bf83cab` | 4.4.4 |

Sáu pin có trong đường cài và log cài thành công; backend 0.3.16 được import trước inference, model SHA được kiểm. GPU probe cùng notebook nhận hai T4. Wheel hash trên là thông tin pip ghi; không thay thế hash thư viện thực được load.

**Các mục chưa đóng cho cả sáu tiến trình:** native 49/49 và phân bổ layer thực; GPU UUID/thứ tự/free VRAM lúc load; xác minh SHA source archive trước build; hash loaded backend; effective threads/constructor và dependency freeze/contract-bound provenance. Source thực dùng `verbose=False`, không gọi `assert_runtime/load_locked_model/provenance` của gói lock mới. Hai test log mỗi arm chỉ có inference progress và context warning, không có native offload report. Không thể tạo hồi tố các dữ liệu đó bằng cách thêm metadata vào output.

Kết luận từng tiến trình: **PARTIAL_CORE_MATCH_NOT_FULL_LOCK**. Không có bằng chứng cho thấy model đã bị chuyển sang CPU, nhưng cũng chưa có chứng cứ đủ để xác nhận full placement theo lock.

## 3. Các phiên validation lịch sử

| Phiên có native log | Tổng record trong file cuối | Record thực tạo trong cửa sổ phiên | Kết luận |
|---|---:|---:|---|
| B1-full seed42 | 5.005 | 5.005 | Native/core khớp; thiếu full provenance |
| B2-nolabel seed42 | 5.005 | 5.005 | Native/core khớp; không gán sang test |
| B2-labelonly seed42 | 5.005 | 5.005 | Native/core khớp; không gán sang test |
| B2-rep seed42 | 5.005 | 5.005 | Native/core khớp; không gán sang test |
| B1-shuf seed44 | 5.005 | 2.892 = 619 Devign + 2.273 REVEAL | 2.113 Devign kế thừa không thuộc log phiên này |

Các native log trên có offload 49/49, hai CUDA T4 và 8192/256/256. Gói `GRACE_5ARMS_EXECUTED_NOTEBOOKS_AND_LOGS.zip` còn các notebook executed và diagnostics gốc; audit ghi hash từng member thay vì dùng notebook bàn giao chưa chạy.

**Đính chính phạm vi chứng cứ B1-shuf:** bộ diagnostics và notebook executed trong ZIP được kiểm hiện thuộc phiên seed44 ngày 07/11. Session log trong gói cũng không chứa seed43. Vì vậy phát biểu cũ rằng gói này chứng minh đầy đủ seed43 không được xác nhận lại từ artifact hiện có. Cần lấy phiên gốc seed42, seed43 và phiên tạo 2.113 record Devign seed44 đã kế thừa. Tổng phần chưa gắn được log: **12.123/15.015 validation record**. Điều này không thay đổi biên bản runtime test B1-shuf đã nghiệm thu riêng.

## 4. B2-rand test: phân rã đủ bốn phiên

| Phiên | Raw records của phiên | Đóng góp vào final census | Contract |
|---|---:|---:|---|
| Seed42 head / I-18 | 4.749 | 4.749 | Sáu package |
| Seed43 head / I-19 | 4.760 | 4.760 | Sáu package |
| Seed44 head / I-21 | 4.661 | 4.661 | Bảy package LF |
| Three-seed tail / I-20 | 877 | 848 | Bảy package LF |
| **Final** | Không cộng raw trùng | **15.018** | Theo từng record |

29 record overlap seed44 dùng bản head; tail đóng góp 257 REVEAL seed42, 246 REVEAL seed43 và 345 REVEAL seed44. Không có final record nào không gán được hoặc bị gán mơ hồ. Phép gán so toàn bộ JSON record, gồm timestamp/provenance, không chỉ ID hoặc score.

REVEAL seed42 gồm **2.017 record contract sáu package + 257 bảy package**; REVEAL seed43 gồm **2.028 + 246**. Không gọi hai nhóm đó là một runtime hash đồng nhất. Đây là các phiên head/tail đã được công bố; không đổi hash lịch sử thành contract hiện tại.

**Sai khác raw hash do checkout:** source và lock trong cây Windows có CRLF, trong khi provenance ghi hash Linux LF. Đã đọc Git blob gốc và phục hồi được **đúng byte**, khớp cả bốn cặp worker/lock. Các bản phục hồi ở `recovered_sources/`, kèm hash và đường dẫn Git trong ledger. Không sửa file lịch sử để ép hash khớp; normalized LF chỉ dùng chẩn đoán, Git blob mới là bằng chứng phục hồi độc lập.

Contract canonical seal, package, constructor, source runner, hai T4 UUID trước/sau load, CPU threads và source archive claim đều khớp; pip freeze và compiled-library hashes có ghi trong provenance. Tuy nhiên native `model_load_offload.log` của từng phiên và build/install log gốc không có ở các thư mục đang kiểm. Có hash native được ghi, chưa có bytes để replay. Kết luận **PROVENANCE_MATCH_NATIVE_LOG_NOT_REPLAYABLE**, không xóa kết luận audit lịch sử nhưng chưa cấp lại full-lock certificate trong lượt này.

Việc tiếp theo: lấy đúng native/build logs từ output/checkpoint gốc I-18/I-19/I-20/I-21, so với hash provenance đã ghi; không cần chạy lại model để tìm các log đó.

## 5. B3 thuật toán lịch sử: đóng được runtime phần resume

| Session provenance | Record tham chiếu | Native/source/build hash | Kết luận |
|---|---:|---|---|
| `locked_vti6l7nv` | 29 | Đều khớp | PASS launch runtime cho 29 record |
| `locked_rt3jkftt` | 947 | Đều khớp | PASS launch runtime cho 947 record |
| Legacy không có session reference | 4.029 | Chưa đủ chain | Không chứng nhận hồi tố |

Đã so record → provenance SHA → đúng source/helper hash → đúng native/build-log hash → lock sáu package, model SHA, constructor/threads/GPU và native 49/49/8192/256/256. Các build logs và source đã đối chiếu được sao chép nguyên byte vào `verified_legacy_b3_evidence/` để người pull Git có thể kiểm tiếp; native/provenance gốc ở hồ sơ completion được trỏ bằng ledger.

Runtime pass này chỉ áp dụng **976 record của đúng hai phiên**, không nâng toàn bộ 5.005 legacy validation thành fully locked; không đánh đồng thuật toán lịch sử với verified-patch B3 mới và không chứng nhận thiết kế contrastive hoặc threshold ngoài phạm vi. Đã gắn lại được 4.029 record gốc vào cửa sổ tiến trình `validation_B3_seed_42` và native log 49/49 trong diagnostics ZIP; phần gốc đó đạt core/native evidence nhưng vẫn thiếu contract-bound provenance.

## 6. Các arm còn lại: điều gì thực sự kiểm lại được?

| Phạm vi | Artifact hiện có / gắn được vào phiên | Giới hạn và việc cần lấy thêm |
|---|---|---|
| B0 I-03 | Saved notebook có native 49/49; 5.005 validation record nằm trong cửa sổ phiên | Full test census có ghi trong worklog cũ nhưng raw test/checkpoint gốc không có tại đường dẫn local được kiểm. Phục hồi checkpoint/log I-03; không suy full lock từ source cập nhật sau này. |
| B1 I-08 / I-07 | Saved I-08 có native 49/49; 5.005 validation record hiện có đều nằm **ngoài** cửa sổ I-08 | Validation được kế thừa từ I-07; không gán native I-08 sang chúng. Cần checkpoint/log gốc cả I-07 và I-08, nhất là raw test census. |
| B2 I-02/I-04/I-05 | Raw cuối đủ 10.011; saved I-05 native 49/49 chỉ gắn thời gian với 1.297 REVEAL test mới | 8.714 record còn lại đến từ I-02/I-04. Cần log từng phiên đó. Bản donor reconciliation còn 28 validation + 38 test riêng; không tính chúng là B2-rand hoặc dùng log I-05 để chứng nhận. |
| B2-flip I-06/I-10 | Saved I-10 có native 49/49 và worklog báo đủ census | Raw records/checkpoint theo đường dẫn lịch sử hiện không có local. Cần phục hồi I-06/I-10 để gắn record theo phiên; chưa có full contract provenance. |
| B2-rand validation | Raw tổng đủ ba seed (15.015), cộng 66 correction B2 được lưu riêng | Saved notebook cuối chỉ gắn được 306 Devign + 2.273 REVEAL seed44 vào phiên I-17. 2.426 Devign seed44 và các seed trước là carry-over. Cần giữ reviewed-legacy status và phục hồi log I-09/I-11/I-15; native I-17 không chứng nhận toàn bộ validation. |
| B1-H2 Kaggle validation | 5.005 record trong cửa sổ saved notebook có native 49/49 | Không có full contract-bound chain. Cần nguồn/archive/build gốc; không trộn Colab. |
| B1-H2 Kaggle test | 5.006 record trong cửa sổ saved notebook có native 49/49 | Manifest thực ghi `tensor_split=[1.0,1.0]`, khác policy auto VRAM. Ghi profile deviation; chưa có cơ sở nói khác biệt đó đã làm thay đổi lớn score. |
| B1-H2 Colab | Các biên bản Colab đã công bố riêng | Ngoài profile Kaggle T4×2 của lock; không lấy log L4 để chứng nhận Kaggle và không gọi là confirmatory hardware-matched comparison. |
| B3-new test | Dũng đang nhận chạy theo thông tin người dùng | Chờ output/session manifests/provenance để nghiệm thu; không dùng trạng thái API làm bằng chứng runtime. |
| B3-nodiff | Người dùng xác nhận Dũng đã chạy | Chờ đúng version, validation threshold độc lập, test/validation output và logs. |
| B3-swap | Được launch mới trên Thanh Duy theo chỉ đạo trong lượt này | Xem `../b3_swap_launch_20261110/`; chưa có runtime certificate trước model load/inference. |
| B3-flip | Bộ prompt/notebook đã chuẩn bị | Chưa có phiên tạo score để nghiệm thu. |

Kiểm đường dẫn của audit 07/11: **52/60 artifact path** không còn file rời tại đúng vị trí cũ; một số nội dung vẫn còn trong ZIP hoặc saved notebook, như đã phục hồi ở trên. Đây là thống kê khả dụng của đường dẫn, không phải kết luận 52 artifact đã mất hoàn toàn. Bảy file hiện có khác raw hash cũ; cần đối chiếu version hoặc Git blob, không tự gọi đó là thay đổi runtime.

## 7. Quyết định và thứ tự xử lý tiếp

1. Giữ kết quả của ba B2 arm, gắn trạng thái partial theo sáu tiến trình; thiếu native report do `verbose=False` phải được khai báo. Tìm lại logs/provenance gốc nếu có; không tạo một report mới rồi coi như bằng chứng cũ.
2. Khôi phục native/build logs của bốn phiên B2-rand đã có provenance hash; đây là công việc ưu tiên vì có chain source/lock/record đủ rõ để đối chiếu tiếp.
3. Khôi phục checkpoints/log gốc cho các phần carry-over B1-shuf validation, B1 I-07, B2 I-02/I-04 và raw B0/B1/B2-flip test. Ghi riêng phiên còn thiếu; không đánh dấu cả arm pass vì một phiên khác pass.
4. Giữ chứng nhận 976 record B3 historical trong đúng phạm vi. Giữ nguyên biên bản B1-full test, B1-shuf test và B3-new validation đã có.
5. Thu output của B3-new/B3-nodiff từ Dũng; tiếp tục kiểm B3-swap mới theo runtime lock. Chỉ quyết định rerun khi đã nêu được artifact không thể phục hồi hoặc cấu hình thực tế không đáp ứng yêu cầu, kèm phạm vi mẫu/run rõ ràng.

## Bằng chứng và tái lập

- [SESSION_RECONCILIATION.json](SESSION_RECONCILIATION.json): kiểm từng process/record group, timestamps, native facts và giới hạn.
- [ARTIFACT_HASHES.json](ARTIFACT_HASHES.json): hash/size file và member ZIP thực đọc.
- [RECORD_ARTIFACT_INVENTORY.json](RECORD_ARTIFACT_INVENTORY.json): toàn bộ record-file candidates; không chứa label hoặc payload record.
- [PRIOR_ARTIFACT_AVAILABILITY.json](PRIOR_ARTIFACT_AVAILABILITY.json): đường dẫn lịch sử tồn tại/thiếu/thay version.
- [AUDIT_VALIDATION.json](AUDIT_VALIDATION.json): tám kiểm tra nhất quán scope, process binding và kết quả ghép; PASS không phải chứng nhận runtime cho các dòng partial.
- Script: `scripts/audit_runtime_sessions_20261110.py`. Chỉ đọc artifact cũ và xuất hồ sơ audit mới; không sửa record, threshold, prompt, config frozen hoặc đăng ký OSF.
