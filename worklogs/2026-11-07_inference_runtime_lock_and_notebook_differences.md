# 2026-11-07 — Thống nhất runtime inference và ghi nhận notebook chưa đồng nhất

## Quyết định đã chốt

- Người dùng chọn inference seed 4294967295 cho các lần chạy mới. Đây là sentinel mặc định llama.cpp; không nhầm với seed chọn prompt 42/43/44 và không coi là cam kết RNG cố định. Đường scoring hiện tại không sampling.
- Chốt package: numpy==2.1.3, huggingface-hub==0.36.2, tokenizers==0.22.2, transformers==4.57.1, llama-cpp-python==0.3.16, scikit-learn==1.5.2.
- Người dùng chọn split_mode=layer, tensor_split=None: chia theo VRAM trống tại lúc load. Không random, cũng không bảo đảm tỷ lệ 1:1.
- Khóa model GGUF Q4_K_M SHA f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335 và tokenizer revision b2cff646eb4bb1d68355c01b18ae02e7cf42d120.
- Context 8192, batch 256, microbatch 256, GPU layers=-1, logits_all=True. Nguồn backend 0.3.16 khóa theo SHA-256 sdist từ PyPI.

## File và phạm vi áp dụng

File mới configs/inference_runtime_lock.json là contract khai báo. Notebook hiện chưa tự đọc/áp dụng file này; cần tích hợp riêng trước khi tuyên bố compliant. Không đổi notebook, prompt, threshold hoặc output cũ trong thay đổi này. Không tự resume output cũ dưới contract khác.
Chỉ stage/commit file JSON và worklog mới này; các thay đổi có sẵn trong working tree không thuộc commit.

## Audit từng notebook hiện có

| Notebook | Seed trong constructor | Tensor split | Thư viện chưa pin trực tiếp |
|---|---:|---|---|
| 01_Author_Baseline_Unified/notebooks/02_kaggle_qwen_q4_b2.ipynb | 4294967295 | auto free VRAM | numpy, huggingface-hub, tokenizers |
| 02_Arm_B0_Source_Only/notebooks/02_kaggle_qwen_q4_b0.ipynb | 42 | auto free VRAM | numpy, huggingface-hub, tokenizers |
| 03_Arm_B1_Graph_Only/notebooks/02_kaggle_qwen_q4_b1.ipynb | 42 | auto free VRAM | numpy, huggingface-hub, tokenizers |
| 03_Arm_B1_Graph_Only/notebooks/02_kaggle_qwen_q4_b1_executed_I08.ipynb | 42 | auto free VRAM | numpy, huggingface-hub, tokenizers |
| 04_Arm_B2_Flip/notebooks/02_kaggle_qwen_q4_b2_flip.ipynb | 42 | auto free VRAM | numpy, huggingface-hub, tokenizers |
| 06_Arm_B2_Rand/notebooks/02_kaggle_qwen_q4_b2_rand.ipynb | 4294967295 | auto free VRAM | Không |
| 06_Arm_B2_Rand/test_delivery_20261107/02_kaggle_qwen_q4_b2_rand_seed42_test.ipynb | 4294967295 | auto free VRAM | Không |
| 06_Arm_B2_Rand/test_delivery_20261107/02_kaggle_qwen_q4_b2_rand_seed43_test.ipynb | 4294967295 | auto free VRAM | Không |
| 11_Arm_B1H2_Evidence/kaggle_b1h2_test_20261106/02_kaggle_qwen_q4_b1_h2_test_20261106.ipynb | 4294967295 | 1:1 | Không |
| 11_Arm_B1H2_Evidence/notebooks/02_kaggle_qwen_q4_b1_h2_validation_20261106.ipynb | 4294967295 | 1:1 | numpy, huggingface-hub, tokenizers |
| Runs-management/kaggle_validation_6arms_20261104/02_kaggle_qwen_q4_b1_full_validation.ipynb | 4294967295 | auto free VRAM | numpy, huggingface-hub, tokenizers |
| Runs-management/kaggle_validation_6arms_20261104/02_kaggle_qwen_q4_b1_shuf_validation.ipynb | 4294967295 | auto free VRAM | numpy, huggingface-hub, tokenizers |
| Runs-management/kaggle_validation_6arms_20261104/02_kaggle_qwen_q4_b2_labelonly_validation.ipynb | 4294967295 | auto free VRAM | numpy, huggingface-hub, tokenizers |
| Runs-management/kaggle_validation_6arms_20261104/02_kaggle_qwen_q4_b2_nolabel_validation.ipynb | 4294967295 | auto free VRAM | numpy, huggingface-hub, tokenizers |
| Runs-management/kaggle_validation_6arms_20261104/02_kaggle_qwen_q4_b2_rand.ipynb | 4294967295 | auto free VRAM | Không |
| Runs-management/kaggle_validation_6arms_20261104/02_kaggle_qwen_q4_b2_rep_validation.ipynb | 4294967295 | auto free VRAM | numpy, huggingface-hub, tokenizers |

## Phát hiện

- 16 runner chính, 5 ghim đủ sáu package. Audit local trước còn tìm 16 bản sao trong worktree/delivery/tmp; một số B2-rand cũ chưa có pin mới. JSON lưu hash từng file chính tại thời điểm audit.
- B0/B1/B2-flip dùng seed 42, lệch contract mới 4294967295; cần thay khi tích hợp cho các lần chạy mới.
- B1-H2 validation/test dùng tensor_split=[1,1], lệch chính sách mới None.
- Đính chính audit: split_mode mặc định đã là layer. n_ubatch mặc định 512 được clamp min(n_batch,n_ubatch), nên n_batch=256 cho microbatch hiệu dụng 256. Thiếu đối số này không chứng minh đã có sai khác batching.
- Tất cả constructor bỏ trống n_threads/n_threads_batch; backend tính theo CPU count. JSON giữ công thức hiện có và yêu cầu lưu giá trị thực tế, chưa tự chọn số thread tuyệt đối.
- Log thực chạy có ở B0/B1/B2/B2-flip/B2-rand/B1-H2 đều khớp NumPy 2.1.3, Hub 0.36.2, tokenizers 0.22.2 sau cài đặt. Các phiên bản mới hơn của image ban đầu được pip thay trước inference. Năm arm B1-full/B1-shuf/B2-rep/B2-nolabel/B2-labelonly chưa có log thực chạy để xác nhận.
- Runner B2 ghi SHA model nhưng thiếu guard đối chiếu với hash frozen vô điều kiện trước load mới; JSON yêu cầu thêm khi tích hợp.
- Không có khóa chung CUDA/compiler/CMake, Python patch hoặc binary wheel. Pin sáu package/source backend không đồng nghĩa environment binary đầy đủ đã giống nhau.
- Chưa có runner Kaggle Qwen hiện hành riêng cho họ B3 trong GRACE-summary. Hai host server lịch sử bên HuuHieu03 dùng backend không pin và batch=2048; không chứng nhận chúng theo contract này.
- AGENTS.md mô tả llama-server b3920/seed42, trong khi source notebook dùng llama-cpp-python 0.3.16 và một số dùng sentinel mặc định. Đây là chênh lệch tài liệu cần đối chiếu protocol frozen, không tự sửa prereg.

## Quyết định bổ sung và bằng chứng còn thiếu

1. Người dùng chốt chỉ chạy Kaggle: giữ build theo Kaggle và bắt buộc lưu đầy đủ provenance. Không yêu cầu container chung; exact CUDA/compiler/CMake/Python patch được ghi theo từng phiên, không tuyên bố binary giống nhau.
2. Người dùng chọn cách đa số notebook dùng: cả 16 bản đều dùng default CPU-count formulas, nên chốt giữ công thức hiện tại và lưu số thread thực tế. Đây không còn là câu hỏi mở.
3. Cần log thực chạy từ người đang chạy năm arm còn thiếu.

## Kiểm tra và nguồn

Parse JSON, kiểm tra checksum canonical, sáu package, seed/tensor_split đã chốt và inventory 16 file. Không chạy GPU; không chỉnh kết quả lịch sử.
- https://pypi.org/pypi/llama-cpp-python/0.3.16/json
- https://raw.githubusercontent.com/abetlen/llama-cpp-python/v0.3.16/llama_cpp/llama.py
- https://raw.githubusercontent.com/ggml-org/llama.cpp/4227c9be4268ac844921b90f31595f81236bd317/src/llama-model.cpp

Phạm vi contract sau trả lời cuối: Kaggle T4×2. Các cấu hình seed/package/GPU distribution/CPU threads/build policy đã được người dùng chốt; câu hỏi còn lại chỉ là thu thập bằng chứng từ các arm thiếu log và runner họ B3. Notebook chưa tự đọc JSON nên chưa được coi đã đồng bộ theo contract.

## Cập nhật đối chiếu log thực chạy — 2026-11-07

Bằng chứng chi tiết, hash file và vị trí dòng/cell: worklogs/2026-11-07_inference_runtime_log_evidence.json. Bảng bên dưới cập nhật tình trạng bằng chứng, không sửa chính sách hoặc checksum của configs/inference_runtime_lock.json (hai notebook B2-rand test đang nhúng contract này).

ĐÃ CHỐT là kết luận cho từng mục của từng phiên có log; không đồng nghĩa toàn bộ notebook hoặc binary runtime lịch sử đã được chứng nhận giống hệt.

| Phiên có output | Sáu package | Context/batch/microbatch | Offload | Python | CUDA nvcc | GCC | CMake |
|---|---|---|---|---|---|---|---|
| B0 | ĐÃ CHỐT: khớp lock | ĐÃ CHỐT: 8192/256/256 | 49/49 | 3.13.15 | 12.8.93 | 13.3.0 | 3.31.10 |
| B1 I08 | ĐÃ CHỐT: khớp lock | ĐÃ CHỐT: 8192/256/256 | 49/49 | 3.13.15 | 12.8.93 | 13.3.0 | 3.31.10 |
| B2 | ĐÃ CHỐT: khớp lock | ĐÃ CHỐT: 8192/256/256 | 49/49 | 3.13.15 | 12.8.93 | 13.3.0 | 3.31.10 |
| B2-flip | ĐÃ CHỐT: khớp lock | ĐÃ CHỐT: 8192/256/256 | 49/49 | 3.13.15 | 12.8.93 | 13.3.0 | 3.31.10 |
| B2-rand validation 20261105 | ĐÃ CHỐT: khớp lock | ĐÃ CHỐT: 8192/256/256 | 49/49 | 3.13.15 | 12.8.93 | 13.3.0 | 3.31.10 |
| B2-rand validation 20261107 | ĐÃ CHỐT: khớp lock | ĐÃ CHỐT: 8192/256/256 | 49/49 | 3.13.15 | 12.8.93 | 13.3.0 | 3.31.10 |
| B1-H2 validation | ĐÃ CHỐT: khớp lock | ĐÃ CHỐT: 8192/256/256 | 49/49 | 3.13.16 | 13.0.88 | 13.3.0 | 3.31.10 |
| B1-H2 test | ĐÃ CHỐT: khớp lock | ĐÃ CHỐT: 8192/256/256 | 49/49 | 3.13.16 | 13.0.88 | 13.3.0 | 3.31.10 |

### Những mục đã đóng bằng bằng chứng

- Sáu package của các phiên trong bảng đều có log sau cài đặt khớp đúng bộ đã chốt; không tiếp tục đánh dấu chưa xác định chỉ vì source notebook không có pin trực tiếp.
- Context 8192, n_batch 256, n_ubatch 256 và offload 49/49 được log xác nhận trực tiếp ở các phiên trong bảng; không chỉ suy ra từ default.
- Các run manifest hiện có trong output B2/B2-flip/B2-rand/B1-H2 được đối chiếu riêng cho model SHA, Q4_K_M, tokenizer revision và scoring identity. Mục thiếu trong manifest vẫn ghi not_recorded, không tự lấp bằng giá trị mong đợi.
- Phương pháp reset/eval/logits cuối/float64/logaddexp được đối chiếu source runner. Manifest ghi unconstrained_first_token_logits_v1 là bằng chứng định danh; không phải kiểm chứng số học độc lập trên GPU.

### Phát hiện mới và những mục vẫn chưa được đóng

- Python/CUDA thực sự có hai nhóm: 3.13.15 + CUDA 12.8.93 và 3.13.16 + CUDA 13.0.88; GCC 13.3.0, CMake 3.31.10 khớp. Đây là provenance nền tảng được phép theo quyết định giữ build Kaggle; không được gọi là cùng binary/toolchain.
- Log build còn ghi SHA-256 wheel đã tạo và các wheel khác hash. Việc này không tự chứng minh sai logits, nhưng không được tuyên bố binary identical. Hash từng wheel nằm trong JSON.
- Seed 42 của B0/B1/B2-flip vẫn khác lock 4294967295 theo cấu hình source; B1-H2 vẫn dùng tensor_split=[1,1] thay vì auto. Không đóng hai khác biệt này chỉ vì package/context đã khớp. Seed record cũ đôi khi là prompt seed, không dùng nó để suy đoán inference seed.
- Chưa thấy log CPU thread count thực tế đầy đủ; giữ kết luận về công thức default ở mức source-derived, chưa xác nhận mọi phiên dùng cùng số thread.
- Chưa có source-sdist SHA đã kiểm chứng, full dependency freeze hoặc hash installed backend binaries cho mọi phiên lịch sử; package source version và wheel-build SHA không thay thế đầy đủ các bằng chứng này.
- B1-full/B1-shuf/B2-rep/B2-nolabel/B2-labelonly vẫn thiếu output thực chạy ở local. Đây là thiếu bằng chứng, không kết luận chúng sai lock.
- Hai notebook B2-rand test mới đã tích hợp JSON ở lượt trước; chúng được kiểm tra local nhưng chưa có log Kaggle mới để đóng bằng chứng thực thi.

Kiểm tra báo cáo: các mục đánh dấu confirmed_match phải có observed==expected và một vị trí bằng chứng. Giữ nguyên byte runtime lock, prompt, threshold và record inference lịch sử.

### Bổ sung checkpoint local ngoài GRACE-summary

Checkpoint B0 tại C:/MY-FILES/LAB-THAY-THO/tmp/b0_kaggle_20261101/grace_b0_checkpoint.zip và B1 tại C:/MY-FILES/LAB-THAY-THO/kaggle_stage_b1/grace_b1_checkpoint.zip có bốn run manifest mỗi arm. Chúng xác nhận model SHA, Q4_K_M, tokenizer repo/revision và scoring identity khớp lock: ĐÃ CHỐT các mục này cho output checkpoint có bằng chứng. JSON lưu hash archive/member và các dòng console phân bổ GPU/build flags khi có.
