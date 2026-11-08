# B3 mới — nghiệm thu CPU Devign và REVEAL sau duyệt người thật

Ngày08/11/2026, sau xác nhận của người dùng về hai review REVEAL lúc22:50+07:00. Không launch GPU trong bước này.

**Cả Devign và REVEAL đã có pool được duyệt, full validation prompt census và delivery đạt CPU integration.** Gate review REVEAL đã đóng. Hai tập đủ phần chuẩn bị để chuyển sang kiểm kỹ thuật GPU khi có quota phù hợp; **chưa phải native runtime PASS hoặc đã đủ score validation**.

## 1. Review và admission REVEAL

- Đọc đúng `review_hieu.json`4.198 bytes và `review_dung.json`4.224 bytes, sao nguyên bytes vào thư mục final forms riêng; không đọc nhầm template hay metadata phụ trợ.
- Hai reviewer Hieu/Dung, approve, cả4 tiêu chí true; timestamp thật `2026-11-08T22:50:00+07:00` hợp lệ so với thời điểm nạp. Cùng giờ giữa hai người khác nhau không phải duplicate-review conflict.
- Payload tính lại: `537b1732aa7cc6dbc3821044275e1364568c6a0893999262b9e5f1264a1c71a7`; C lexical tokens tính lại166 trước/181 sau, khớp thông tin người dùng.
- Validator kiểm payload/forms/consensus, membership clean-train, C token mapping và actual patch/source. Pair đã được nạp atomic vào [pool REVEAL mới](../reveal_reviewed_pool_20261108/pool_manifest.json), trạng thái `ACTIVE_VERIFIED_POOL`,1 pair. Pool SHA `37bb24c5be0e36c9f6c03a046e17687265461abeb1873fe399c9232c7e761203`.
- Independence là xác nhận của hai reviewer qua phiếu và lời xác nhận trực tiếp của người dùng; không tuyên bố đã kiểm chữ ký số bằng khóa mật mã. Không tạo nội dung review thay hai người.

## 2. Full validation prompt REVEAL

Đã dựng và audit **2.273/2.273 target** từ frozen specs, đối chiếu frozen validation population/code; selector chỉ nhận ID/code/graph. Census SHA `fe3e026a8c6db6e08718d1cdaa45138ea4a79169f19225db7734522027c62676`.

| Kiểm tra | Kết quả |
|---|---:|
| ID đúng population, unique | 2.273 |
| Prompt rendered/audited | 2.273 |
| Code lớn nhất | 3.000 tokens |
| Graph lớn nhất | 1.500 tokens |
| Demo lớn nhất | 697 tokens |
| Tổng chat lớn nhất | 5.280 tokens |
| Tổng cộng reserve | 5.344 ≤8.192 |

Mọi prompt hash, label join ngoài prompt, Figure6 flags và toàn bộ token caps được kiểm lại trong test dataset-specific. Census mới được render thật; không dùng Devign audit thay REVEAL. Trong lúc render, draft guard demo được siết từ3.000 xuống1.500; lượt acceptance sau đó kiểm lại **toàn bộ**2.273 record theo cap1.500, max thực697. Sự thay đổi guard không đổi prompt text hoặc chọn pair.

Do pool mỗi dataset hiện chỉ có1 pair, mọi target trong tập đó chọn cùng pair; chưa thể tuyên bố đã đánh giá adaptive retrieval trên pool đa dạng. Không dùng pair Devign thay REVEAL.

## 3. Hai delivery, cùng thuật toán/runtime

| Dataset | Input release | N validation | Trạng thái CPU |
|---|---|---:|---|
| Devign | [v6](../release_20261108_v6/release_manifest.json) | 2.732 | PASS, giữ nguyên artifact đã nghiệm thu |
| REVEAL | [v7 REVEAL](../release_20261108_v7_reveal/release_manifest.json) | 2.273 | PASS, delivery mới riêng |

`method_id=b3-verified-patch-v1` giống nhau. Version khác là các snapshot input/delivery, không phải đổi thuật toán giữa datasets. Mỗi root pin đúng pool/census/labels/model/tokenizer/runtime/code của tập đó. Experiment index kèm hashes nằm tại [experiment_index.json](experiment_index.json).

REVEAL input-root SHA: `3255dfa600e191c874560fbcd285a22337b8546e1a510c3f6804c46ff2cfc8fc`.

Ba tests mới chạy trên **bundle/notebook REVEAL thật**, đều PASS: full population/labels/prompt hashes/caps; loader ZIP và unpacked; config đúng REVEAL/count2.273/model kernel source/T4 shape. [Log](delivery_integration.log), [acceptance](acceptance.json). IO/helper/contract byte-identical với v6; các suite101-pass và regression checkpoint/scoring đã có được tái sử dụng sau kiểm source hashes không đổi, không cộng thành101 tests chạy lại trong lượt này.

## 4. Kaggle đã chuẩn bị

Cùng account `huuhieu3333`, không phân tán sang account khác:

- [Devign private inputs](https://www.kaggle.com/datasets/huuhieu3333/grace-b3-v6-devign-inputs): ready, private đã đọc lại từ server ở lượt trước.
- [REVEAL private inputs](https://www.kaggle.com/datasets/huuhieu3333/grace-b3-v7-reveal-inputs): mới upload, server xác nhận **ready và is_private=true**; [receipt](private_dataset_upload.json), [readback](private_dataset_visibility.json).
- Model kernel source `huuhieu3333/qwen3coder30b-prepare-notebook`, version1, đã xác nhận truy cập được.
- [SDK request REVEAL](prepared_launch_request.json) và request Devign ở acceptance v6 đều đã chuẩn bị; không gửi kernel/GPU request trong bước này. Với Devign dùng prepared SDK request thay base metadata template; SDK request giữ T4 shape/model source.

## 5. Còn chặn bởi quota và native evidence

Lần kiểm account lúc15:45UTC ghi quota còn1.417,606 giây, khoảng23,6 phút; không đủ request9h. API trả refresh `2026-11-14T00:00:00Z`. Đây là số đo tại thời điểm đó, không bảo đảm wall time cho mọi accelerator/session hoặc tình trạng account ở thời điểm launch tương lai. Phải kiểm lại trước chạy.

**Bước tiếp theo:** có đủ quota trên account đã chốt → upload/push notebook bằng SDK giữ machine shape → đọc lại tất cả cell sources/shape/input mounts → nghiệm thu native build/model/tokenizer/scoring/offload/provenance → full validation Devign2.732 và REVEAL2.273. Có thể chạy tuần tự trên cùng account và checkpoint/resume theo đúng identity; không cần cùng một session.

Chưa có native runtime bằng chứng của hai delivery mới, score validation mới hoặc threshold mới. Sau đủ census từng tập mới tính/kiểm và khóa τ* riêng, rồi dựng/audit test delivery. Không áp historical B3 scores/thresholds, không mở test hoặc arm khác ở đây.

**Kết luận gate:** review/source/pool/prompt/CPU delivery hai tập đã đạt; native GPU/full validation vẫn PENDING. Gate review REVEAL đã được giải quyết, không cần ký lại cùng payload này.
