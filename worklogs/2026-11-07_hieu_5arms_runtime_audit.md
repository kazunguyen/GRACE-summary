# Đối chiếu runtime của năm arm Hiếu — 07/11/2026

Đối chiếu `GRACE_5ARMS_EXECUTED_NOTEBOOKS_AND_LOGS.zip` với `configs/inference_runtime_lock.json` và năm notebook validation cùng tên trong `Runs-management/kaggle_validation_6arms_20261104/`. ZIP có SHA-256 `ba5831bc387c25d831bce43363493a01d44ed6f408c92219c17f0aa8143c2e4a`. Cả 17 mục trong manifest khớp kích thước và SHA-256. SHA-256 của file lock là `85d8770839f80260cdc7c27b27b6cce6bf8815675c8593db68fb102589c5cbd6`.

## Bằng chứng inference

| Arm | Prompt seed | Validation theo log | SHA-256 wheel llama-cpp-python từ log build |
|---|---|---|---|
| B1-full | 42 | Devign 2.732/2.732, REVEAL 2.273/2.273 | `1c3440ae73a37cea0369a86cfcc6b61ec61c75cb38702dfc4cd270fb2f20fe86` |
| B1-shuf | 43, 44 | Seed 43 đủ hai tập, gồm 1.125 mẫu Devign resume. Seed 44 dừng ở Devign 2.113/2.732, chưa thấy scoring REVEAL. | `9f4da8fd0ac02a975294ddbda913d83e79f3b84d24bc8421dbcce626af51a422` |
| B2-rep | 42 | Devign 2.732/2.732, REVEAL 2.273/2.273 | `4c5e26de5dcf97ab7ab3e6b95f5b7269c93166b69aec0572d6821f9812203990` |
| B2-nolabel | 42 | Devign 2.732/2.732, REVEAL 2.273/2.273 | `259e0fb2f93473794675541f83fb59a090fd4c9e4a4dfe9e25f752f368ec9a14` |
| B2-labelonly | 42 | Devign 2.732/2.732, REVEAL 2.273/2.273 | `d5b7dcfc9aedd25d126215ba1c4fe718d85f31e16ac50af745da84072635c43a` |

Số mẫu lấy từ `validation_seed_*.log` và cell điều phối cuối. ZIP có bằng chứng validation cho cả năm arm, thiếu output test và thiếu record/checkpoint để kiểm kê độc lập. Với B1-shuf, ZIP thiếu log inference seed 42 và log của phiên tạo 1.125 record Devign đã resume. Metadata notebook B1-shuf ghi Python `3.13.15` và thời điểm 01–02/11 UTC, còn `events.log` có timestamp 05/11 UTC và Python `3.13.16`, cùng dấu thời gian và lệnh chạy seed 43/44 với cell output. Dùng log trực tiếp cho phiên seed 43/44. Provenance của phần checkpoint cũ vẫn chưa xác minh.

## Phiên bản trong log

| Package | Lock | Quan sát sau cài, cả năm arm | Pin trực tiếp trong cả năm notebook |
|---|---|---|---|
| NumPy | `2.1.3` | `2.1.3` | Không |
| huggingface-hub | `0.36.2` | `0.36.2` | Không |
| tokenizers | `0.22.2` | `0.22.2` | Không |
| transformers | `4.57.1` | `4.57.1` | Có |
| llama-cpp-python | `0.3.16` | `0.3.16` | Có, runner cũng kiểm tra khi import |
| scikit-learn | `1.5.2` | `1.5.2` | Có |

- `events.log` ghi phiên bản sau build trước khi gọi runner. `install_dependencies.log` xác nhận `tokenizers 0.22.2`. SciPy `1.16.3` và pip `26.2.2` cũng trùng trong các log được cung cấp.
- Cả năm phiên có log dùng Python `3.13.16`, CUDA nvcc `13.0.88`, driver `580.178.04`, GNU GCC `13.3.0`. `cmake.log` ghi CMake hệ thống `3.31.10`, còn `install_llama_cuda.log` ghi build wheel thực tế dùng CMake `4.4.4` trong môi trường build của pip. Wheel của năm arm có năm hash khác nhau. Lock cho phép build trên Kaggle và yêu cầu lưu provenance.
- Sáu log runner có hai Tesla T4, offload `49/49`, context/batch/microbatch `8192/256/256` và `flash_attn=0`. Các cờ build CUDA, SM75, đường dẫn thư viện, parallel level và `FORCE_CMAKE` khớp lock theo cell cài đặt.

## Source đã khóa gì và còn thiếu gì

- Cả năm notebook trong ZIP và cả năm bản bàn giao local đều chưa nạp hoặc xác thực `inference_runtime_lock.json`. Các bản local có cell output trống. Source các cell cài đặt, probe, chọn model, runner và điều phối giống bản trong ZIP ở từng arm. Ba pin hiện có đều đúng. Ba package chưa ghim là NumPy, huggingface-hub và tokenizers. Chưa có kiểm tra toàn bộ sáu phiên bản trước scoring hoặc xác minh SHA-256 sdist trước build.
- Runner kiểm tra SHA-256 model Q4_K_M trước `Llama()`. Các bundle validation local khớp SHA khai báo trong source và manifest thành phần đều khai báo đúng repo/revision tokenizer cùng context `8192`. Log xác nhận các bundle được nạp và qua kiểm tra SHA. Runner kiểm tra token ID HF/GGUF, label đơn token, hash prompt và context budget.
- Constructor truyền `n_batch=256`, `n_gpu_layers=-1` và `logits_all=True`. Inference seed và chia GPU dựa vào mặc định của backend đã pin (`4294967295`, layer/auto VRAM theo audit mặc định trong worklog runtime). `--seed 42/43/44` là prompt seed. Microbatch hiệu dụng được log xác nhận là `256`. Các notebook chưa thực thi gate bắt buộc `49/49` và chưa ghi đủ số CPU thread hiệu dụng, UUID/thứ tự GPU, hash backend đã cài, dependency freeze và contract SHA. Resume kiểm tra identity cũ nhưng chưa buộc cùng runtime contract.
- Cùng đường scoring trong source: reset, eval, logits vị trí cuối, chuẩn hóa toàn vocab bằng `float64`, tính score với `logaddexp`, lấy argmax toàn vocab cho raw token và giữ score hợp lệ khi raw ngoài `0/1`. B2-rep thêm `repeat=True` và `tag='repeat'` vào identity/record và kiểm tra khi resume. Phần đối chiếu scoring dựa trên source, chưa chạy kiểm chứng số học GPU độc lập.

Không thấy notebook test riêng cho năm arm trong phạm vi ZIP và bộ bàn giao đã đối chiếu. Các bản validation local chưa có output đều có cùng lỗ hổng pin trước khi dùng cho phiên mới. Không có pin trực tiếp nào đặt sai phiên bản. Kết quả này bổ sung bằng chứng cho mục năm arm còn thiếu log trong worklog runtime trước đó.
