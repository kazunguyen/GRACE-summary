# Nghiệm thu runtime và khóa threshold B3 mới — 09/11/2026

**Trạng thái: LOCKED.** Release chính thức cho ngưỡng của `b3-verified-patch-v1`, arm B3, seed prompt 42 là [threshold_release_20261109_v1](threshold_release_20261109_v1/release_manifest.json). Đây là ngưỡng riêng cho subprotocol sửa đổi sau đăng ký, phân loại `AMENDED_EXPLORATORY_SUBPROTOCOL`. Không gọi đây là ngưỡng đã đăng ký OSF hay xác nhận OSF đã được cập nhật.

## 1. Ngưỡng đã khóa

| Dataset | Validation hợp lệ / census | τ* | MCC validation | TP | TN | FP | FN |
|---|---:|---:|---:|---:|---:|---:|---:|
| Devign | 2.732 / 2.732 | **0,99** | 0,0501474890867987 | 491 | 982 | 563 | 696 |
| REVEAL | 2.273 / 2.273 | **0,01** | 0,06487856711606896 | 189 | 383 | 1.680 | 21 |

Đã đọc lại raw records, đối chiếu ID/label/prompt/model/runtime với bundle validation đã seal, kiểm đủ census và score/logprob. Quét lại đủ 99 điểm `τ=i/100`, dự đoán 1 khi `s>=τ`; tính TP/TN/FP/FN và MCC trực tiếp. Toàn bộ grid khớp candidate trước đó và khớp triển khai optimizer độc lập trong sai số MCC `1e-12`. Tie trong `1e-9` chọn gần 0,5 nhất, rồi ngưỡng thấp hơn; hai tập đều có nghiệm thắng duy nhất. Hai nghiệm ở biên grid được giữ đúng theo quy tắc đã định.

AUROC validation raw là 0,530426 (Devign) và 0,541851 (REVEAL). Nghiệm thu tính đầy đủ và đúng quy trình không đồng nghĩa mô hình có hiệu năng cao. Không thay pool, prompt hoặc phương pháp sau khi xem các metric này.

## 2. Thẩm quyền và thời điểm

Người dùng đã yêu cầu trực tiếp trong phiên hiện tại: “vậy thực hiện nốt các yêu cầu để chốt threshold đi, check kỹ runtime xem đã đúng cả chưa nhé”. [governance_record.json](threshold_release_20261109_v1/governance_record.json) ghi nguyên văn yêu cầu và thời điểm hệ thống thực sự tạo record. Đây là ủy quyền để hoàn tất khóa ngưỡng riêng sau kiểm tra kỹ thuật; không tạo chữ ký của Hiếu/Dũng, không sửa mốc ratification lịch sử và không xác nhận một thủ tục bên ngoài đã diễn ra.

Candidate và các root cũ được giữ nguyên để bảo toàn lịch sử. Các dòng “pending” trong chúng mô tả trạng thái lúc tạo; trạng thái hiện hành nằm trong release mới này.

## 3. Nghiệm thu runtime

Đã đọc trực tiếp embedded contract từ **cả năm notebook** trong `grace_hieu_5arms_runtime_locked_20261107.zip`, không thực thi notebook. Các phần model, tokenizer, backend source, constructor, GPU policy, threads, build, scoring và resume khớp contract đang dùng. Sáu pin package gốc giữ nguyên; contract mới bổ sung `scipy==1.16.3` theo kế hoạch runtime hiện hành. Vì vậy hai file contract không giống từng byte, nhưng core policy nêu trên khớp.

- Contract delivery SHA-256: `4c9c3bcff5e9fd32532d7edf85df7a961e45ec9c64bee3df8833d986a2eb276e`.
- Canonical contract seal đã tính lại: `d79396de5d37ca6c3123ac05ea122d665f5f9b252aa0b32ac2b5c464b68e338f`.
- Model: Qwen3-Coder-30B-A3B-Instruct GGUF Q4_K_M; SHA-256 `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`.
- Tokenizer revision: `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`; worker kiểm HF/GGUF token IDs trước scoring.
- Bảy package thực tế khớp contract và pip freeze. Backend cài từ sdist đã pin `34ed0f9bd9431af045bb63d9324ae620ad0536653740e9bb163a2e1fcb973be6`.

| Dataset/session ghi score | Records | Thiết bị | Layer GPU | Context / batch / ubatch | Kết quả |
|---|---:|---|---|---|---|
| Devign `seed_42_ramsrn8t` | 2.732 | 2 Tesla T4 | CUDA0:25, CUDA1:24; 49/49 | 8192 / 256 / 256 | PASS |
| REVEAL `seed_42_3dtwvzh5` | 1.713 | 2 Tesla T4 | CUDA0:25, CUDA1:24; 49/49 | 8192 / 256 / 256 | PASS |
| REVEAL resume `seed_42_x65ffo1l` | 560 | 2 Tesla T4 | CUDA0:25, CUDA1:24; 49/49 | 8192 / 256 / 256 | PASS |

Các session được chọn bằng tham chiếu trong từng record, không bằng tên thư mục mới nhất. Một session Devign khác có provenance nhưng không tạo thêm score trong census; không dùng nó để chứng nhận thay session đã tạo records.

Constructor khớp toàn bộ: layer split, `tensor_split=None`, `main_gpu=0`, `n_gpu_layers=-1`, `flash_attn=False`, `logits_all=True`, mmap bật/mlock tắt, offload KQV bật. Chính sách chia theo VRAM trống không yêu cầu tỉ lệ cố định; 25/24 là phân bố quan sát được của lần này. CPU 4 luồng, `n_threads=2`, `n_threads_batch=4`, đúng công thức contract. Native log có CPU_Mapped/host buffers; 49/49 GPU layers vẫn được xác nhận, các buffer phụ này được contract cho phép.

Scoring thực hiện reset/eval từng prompt, logits vị trí cuối, normalization float64 và `s=exp(lp1-logaddexp(lp0,lp1))`; records đã được kiểm lại bằng công thức tương đương. Prompt seed 42 và constructor seed sentinel `4294967295` được ghi riêng; scoring trực tiếp không sampling.

Mỗi provenance có hash worker, native log, build log và các thư viện backend. Build log được tìm theo đúng hash, chứng minh CUDA build thành công cho SM75. Python 3.13.16, CUDA compiler 13.0.88, GNU 13.3.0; build isolation dùng CMake 4.4.4, còn probe CMake sau cài là 3.31.10. Đây là hai thời điểm/môi trường khác nhau và đã được ghi riêng, không đổi số để làm chúng giống nhau.

**Giới hạn chứng nhận:** đạt contract Kaggle platform build được người dùng chấp thuận; không chứng nhận binary giống hệt giữa các phiên. Hash thư viện đã được worker pin ghi nhận, nhưng không giữ binary từ xa để rehash độc lập. Backend thực tế là `llama-cpp-python==0.3.16`, không phải literal `llama-server b3920` trong mô tả cũ. Những khác biệt này phải được giữ khi báo cáo phương pháp. Chi tiết có hash và bằng chứng từng session: [runtime_acceptance.json](threshold_release_20261109_v1/runtime_acceptance.json).

## 4. Seal và kiểm tra trước sử dụng

| Artifact | SHA-256 byte để pin |
|---|---|
| [Devign lock](threshold_release_20261109_v1/devign_threshold_lock.json) | `53769b653d53a30f52ed815c34ce15778561ecb5e33f9cd4b09dc8e2c1d7d7f4` |
| [REVEAL lock](threshold_release_20261109_v1/reveal_threshold_lock.json) | `63556e5a135125b03b9931b8e9e91e035acfb09c87fe5674d2631f69a43c81d2` |
| [Release manifest](threshold_release_20261109_v1/release_manifest.json) | `e485dcb4e030339453a4e9c11421586b5aa73bcd45bd051a7c65a0399cddeafa` |

Đã kiểm readback hai lock. Với mỗi dataset, gate từ chối file đổi byte, payload sai canonical seal, pool khác và runtime khác: tổng 10 kiểm tra đúng/sai đều PASS. [verification.json](threshold_release_20261109_v1/verification.json) ghi kết quả. Loader [b3_threshold_lock.py](../../scripts/b3_threshold_lock.py) yêu cầu hash được pin từ delivery cùng danh tính method/pool/model/tokenizer/runtime/scoring/worker; không tin hash do chính file lock tự khai.

Hai file `*_full_grid.json` trong release là bản sao candidate giữ nguyên full grid và trạng thái lịch sử. Quyết định khóa nằm trong `*_threshold_lock.json`, không suy trạng thái từ bản sao candidate.

## 5. Bước tiếp theo

Threshold đã sẵn sàng để đưa vào delivery test. Còn phải dựng/audit/seal prompt test theo Bước 13: Devign 2.732 và REVEAL 2.274, giữ pool/selector/renderer/tokenizer/runtime đã dùng cho validation; sau đó pin lock SHA và gọi loader trước inference/evaluation. Việc tích hợp này chưa thực hiện trong lượt khóa ngưỡng; chưa tuyên bố notebook test đã sẵn sàng hoặc đã chạy.

Không đọc score/nhãn test để chọn ngưỡng. B3-flip/swap kế thừa lock B3 mới nếu triển khai sau này; B3-nodiff cần validation riêng. Các file ngưỡng preregistration không bị sửa; hash trước/sau có trong governance record.
