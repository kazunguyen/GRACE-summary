# Nghiệm thu sáu arm và điều kiện tiếp tục — 08/11/2026

Đã truy cập đúng ba tài khoản, kiểm trạng thái và tải lại bằng chứng vào thư mục mới; đối chiếu với `Runs-management/kernel_outputs_harvest/`. **59/59 artifact được chọn trên cloud đã có local và khớp SHA-256 nguyên byte**. Chỉ đọc cloud; không upload, cancel, push hay khởi chạy run.

Snapshot kiểm cloud hoàn tất UTC `2026-11-08T00:07:38.737833+00:00` (**07:07:38 GMT+7**). Chi tiết mỗi request và hash trong `network_verified/collection.json`.

## Kết luận từng arm

| Arm | Trạng thái cloud | Record local | Nghiệm thu dữ liệu | Runtime lock | Có thể tiếp tục? |
|---|---|---:|---|---|---|
| B2-labelonly test | COMPLETE | 5.006/5.006 | Đạt các kiểm tra record, input và metric | Core settings/package khớp; thiếu full-offload/sdist/build provenance | Không còn mẫu để resume; giữ output với giới hạn provenance |
| B2-nolabel test | COMPLETE | 5.006/5.006 | Đạt; có 1 raw response-invalid nhưng score vẫn hợp lệ | Như B2-labelonly | Không còn mẫu để resume |
| B2-rep test | COMPLETE | 5.006/5.006 | Đạt; prompt trùng B2 đúng phiên, cờ repeat/tag đúng | Core settings/package khớp; thiếu provenance đầy đủ | Không còn mẫu để resume |
| B1-full test | ERROR | 2.850/5.006 | Record đã lưu toàn vẹn, nhưng prompt không đạt budget giao thức | Thiếu provenance đầy đủ | Chưa resume nguyên trạng; phải xử lý lỗi dựng prompt |
| B3 + B3-nodiff validation | COMPLETE kernel, batch timed_out | 4.029/10.010 | Các record đã có khớp; checkpoint đầy đủ và toàn vẹn | Package/hardware/offload có bằng chứng, chưa fully runtime-locked | Có thể tiếp tục phiên lịch sử cùng cấu hình; không tự đổi sang amended |
| B1-shuf test, 3 seed | ERROR | 0/15.018 | Chưa inference; input qua preflight | Nạp model đúng, gate đọc log false-negative | Đã chuẩn bị notebook sửa guard; chạy mới từ đầu |

Kernel COMPLETE không đồng nghĩa đủ census: B3 dừng theo wall-clock và export checkpoint đúng, còn B3-nodiff chưa chạy mẫu nào.

## Ba arm đã hoàn tất

Đã kiểm từng record với frozen test manifest và prompt thực trong bundle: exact ID census, không thiếu/thừa/trùng ID, nhãn, arm/dataset/split/seed, model SHA, hash prompt được tính lại từ text, token ID 0/1, score hữu hạn, score–logprob/probability, pred_argmax/pred_tau, threshold đã khóa, timestamp và elapsed. Tính lại AUROC/MCC/BA/F1 từ record, không lấy metric từ bảng ảnh và không refit threshold trên test. Cả sáu evaluation.json đều khớp.

| Arm | Dataset | tau | AUROC tính lại | MCC tính lại | BA tính lại | F1 tính lại |
|---|---|---:|---:|---:|---:|---:|
| B2-labelonly | Devign | 0.99 | 0.546233 | 0.084851 | 0.532157 | 0.301275 |
| B2-labelonly | REVEAL | 0.02 | 0.600540 | 0.119907 | 0.598596 | 0.230958 |
| B2-nolabel | Devign | 0.98 | 0.526898 | 0.051784 | 0.525001 | 0.436444 |
| B2-nolabel | REVEAL | 0.21 | 0.572084 | 0.083533 | 0.569242 | 0.210291 |
| B2-rep | Devign | 0.70 | 0.530473 | 0.059708 | 0.529326 | 0.548465 |
| B2-rep | REVEAL | 0.12 | 0.566158 | 0.064484 | 0.553065 | 0.200531 |

Ba arm dùng đúng cùng target code/graph trên 5.006 ID; demo code nolabel giữ nguyên so với rep. Graph và demo code không vượt 1.500 token, target không vượt 3.000, tổng context với reserve đều đạt. Không bỏ record raw-invalid duy nhất của B2-nolabel REVEAL vì binary score/logprob vẫn hợp lệ.

Final/checkpoint ZIP của ba arm mở được, CRC đạt và mọi trường của mọi record khớp file rời; không chỉ so số dòng. Source thực đã tải cũng có direct reset/eval/logits/float64, model/tokenizer đúng và ngưỡng đúng.

### B2-rep và tính mới của lượt gọi

So với B2 donor mới được tái dựng bằng 38 test rerun Devign, 5.006 prompt hash trùng đúng. Mọi record rep có repeat=true và tag=repeat, timestamp khác B2 và elapsed dương. Exported runner thực gọi reset/eval cho từng ID, log có hai tiến trình suy luận độc lập, không có dòng resume từ B2 hay API đọc response cache. Tất cả score trùng B2 trong đường deterministic hiện tại; điều đó riêng lẻ không phải bằng chứng dùng cache và cũng không chứng minh không dùng cache. Bằng chứng code/process/timestamp ủng hộ một lượt thực thi mới; không gọi cờ repeat là bảo đảm tuyệt đối ngoài những gì đã quan sát.

### Giới hạn runtime của ba run hoàn tất

Log chính phiên xác nhận hai T4, Linux/Python 3.13.16, cài đúng sáu package (bao gồm NumPy 2.1.3 và llama-cpp-python 0.3.16), model SHA đã được kiểm. Exported runner khớp context/batch/microbatch 8192/256/256, layer split/default tensor_split=None và inference seed sentinel. Record cũng ghi seed đúng.

Tuy nhiên source dùng verbose=False; không tìm được native model-load log 49/49 của chính ba run. Không có sdist origin verification, contract hash, compiled backend hashes và full provenance như runtime-locked notebook. Vì vậy **nghiệm thu dữ liệu và core settings đạt, nhưng chưa chứng nhận runtime lock đầy đủ**. Không lấy log validation trước đó hoặc log B1-shuf để bổ sung hồi tố. Các khẳng định worklog cũ về events.log chứng minh 49/49 cho B2-labelonly không được chứng minh bởi artifact đã kiểm.

Không tự loại kết quả hoặc rerun cả ba arm chỉ vì thiếu provenance. Giữ output và khai báo giới hạn; việc đòi lại một phiên fully locked là quyết định riêng, không được sửa metadata cũ thành chứng nhận mới.

## B1-full: không chỉ một prompt quá dài

Quét đúng pinned tokenizer và chat template trên cả 5.006 prompt:

- `reveal:test:118`: tổng context **10.200**, target code **6.571** token. Resume nguyên trạng sẽ dừng lại ở đúng ID đó.
- Target code vượt 3.000: **37 Devign + 47 REVEAL = 84 prompt**, trong đó **42 đã inference** (37 + 5).
- Đếm lại theo `grace_diag.probes.split_blocks`: graph vượt 1.500 token ở **2.559 Devign + 2.138 REVEAL**.
- Hợp các ID vượt code hoặc graph: **4.745/5.006**; trong đó **2.693/2.850 record đã có** thuộc prompt vượt ít nhất một budget thành phần. Đây là vi phạm budget đã đăng ký dù nhiều prompt vẫn dưới 8.192 tổng context.

Không được coi chỉ sửa/cắt một ID là đủ nghiệm thu. Cần khôi phục bộ dựng đúng budget và cùng target input giữa các arm, audit candidate riêng, ghi thay đổi sau prereg và xác định rerun đúng các ID có prompt thay đổi. Không tăng n_ctx, skip ID, chỉnh frozen specs hoặc chọn lại threshold theo test. Những record cũ vẫn giữ nguyên làm bằng chứng lịch sử.

### Checkpoint B1-full bị chậm bốn record

File rời có **2.732 + 118 = 2.850** record, nhưng ZIP periodic gốc chỉ có **2.732 + 114 = 2.846**. Mọi record trong ZIP khớp file rời; bốn record cuối chỉ có trong file rời đã được xác minh cloud/input.

Đã tạo `resume_delivery/grace_b1_full_test_recovered_2850.zip` từ nguyên byte file rời, giữ 2.850 record và metadata có thật. Không tạo giả manifest cho REVEAL vốn không được xuất khi lỗi. Gói này là phục hồi dữ liệu, **chưa phải gói đủ điều kiện resume inference**.

## B3: checkpoint tốt, có thể tiếp tục cùng phiên lịch sử

Đủ 2.732 Devign B3 và 1.297 REVEAL B3; tất cả record đã kiểm đúng ID/label/prompt/model/score. ZIP checkpoint 851.502 byte CRC đạt, có đủ 4.029 record khớp toàn bộ trường với file rời. Không mất record khi graceful exit.

Log batch và status xác nhận wall-clock timed_out, không phải dừng theo kết quả metric. Còn **976 REVEAL B3** và **5.005 B3-nodiff**, tổng **5.981** lượt. Toàn bộ 10.010 prompt validation hai arm qua preflight context/reserve và target code, không thấy blocker tương tự B1-full.

Package đúng và log nạp model có hai T4/offload 49/49. Runner vẫn là phiên lịch sử, chưa có đủ source/build/resume provenance để gọi fully runtime-locked; cũng chưa có bằng chứng cặp patch đáp ứng phương pháp amended. Có thể tiếp tục cùng input/model/runner và checkpoint đúng hash dưới cùng phân loại lịch sử. Không đưa checkpoint này vào notebook amended/runtime-locked rồi coi toàn bộ record cũ đã được chứng nhận.

Đã chuẩn bị bản notebook lịch sử clear output và bản sao checkpoint nguyên byte trong `resume_delivery/`. Chưa upload hay chạy GPU. Sau khi đủ validation mới chọn/khóa ngưỡng theo quy tắc; không bắt đầu test trong bước này.

## B1-shuf: sửa guard, không thay cách chia GPU

Log thật trong checkpoint cho thấy CUDA0/CUDA1 là T4, offload 49/49 và context/batch/microbatch đúng. Provenance có đúng contract SHA, sáu package, constructor, source sdist và compiled backend hashes. Lỗi xảy ra ở gate nhận diện GPU: phần log được capture có `using device CUDA0 (Tesla T4)`, còn regex chỉ tìm header `Device 0: ... T4` vốn không nằm trong đoạn capture đó.

Chưa có record inference nào. Đã tạo notebook sửa **chỉ bộ đọc log**: chấp nhận cả hai định dạng, dùng tập ID GPU duy nhất và ưu tiên device thực được model loader dùng. Vẫn từ chối thiếu GPU, duplicate CUDA0, 48/49, context sai và GPU không phải T4; không bỏ assertion. Sáu kiểm tra replay log thật bằng fake model đều đạt.

Đã preflight đủ 15.018 prompt của ba seed: không vượt tổng 8.192, reserve 64 hay target 3.000. Dùng input/threshold/contract nguyên trạng, nên có thể chạy mới từ đầu bằng notebook sửa; không có record cũ để resume. Notebook nằm ở `resume_delivery/02_kaggle_b1_shuf_test_gpu_log_guard_fixed.ipynb`. Các lần resume sau cần checkpoint của chính run mới.

## Bằng chứng và tái lập

- `acceptance.json`: record-level checks, metric, token preflight 45.052 prompt, archive CRC và hash.
- `additional_integrity.json`: token IDs, probability, inference seed, full-field archive equality, repeat vs frozen-donor B2.
- `b1_full_component_audit.json`: mọi ID B1-full vượt budget code/graph, gồm cờ đã inference.
- `completed_component_audit.json`: ba arm complete giữ chung code/graph, demo nolabel không đổi, graph/demo budgets đạt.
- `network_verified/collection.json`: trạng thái cloud, hash artifact và đối chiếu local; 59/59 selected files match.
- `resume_delivery/delivery_manifest.json` và README: file phục hồi/bản tiếp tục cùng hash và giới hạn.

Script chính: `scripts/accept_six_arm_outputs_20261108.py`; các verifier bổ sung nằm cùng thư mục báo cáo. Các dữ liệu inference lớn bị ignore có thể không đi theo Git clone. Không có GPU inference, threshold refit trên test hoặc thay đổi cloud trong lượt kiểm toán này.
