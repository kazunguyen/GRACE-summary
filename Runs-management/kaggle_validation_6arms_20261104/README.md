# Kaggle validation cho sáu arm

**B2-rand cập nhật 07/11:** dùng [notebook resume hiện hành](02_kaggle_qwen_q4_b2_rand.ipynb) và checkpoint I-15 tại `Runs-management/kaggle_outputs_20261107/b2_rand_latest/grace_b2_rand_checkpoint.zip`. Seed 42/43 đã đủ validation; seed 44 có 2.426/2.732 Devign và 0/2.273 ReVeal, còn 2.579 lượt. Thêm checkpoint này làm Kaggle Input; notebook xác minh lineage I-11, bỏ qua ID cũ, chỉ inference validation seed44. Giới hạn **9 giờ tính từ cell đầu**, gồm setup; dừng mẫu mới trước hạn 10 phút. Runner chặn test. Threshold seed42/43 đã khóa riêng ở `../../06_Arm_B2_Rand/config/threshold.json`; seed44 phải chờ validation đủ. Manifest lịch sử I-11: [delivery manifest](../../06_Arm_B2_Rand/validation_resume_20261106/delivery_manifest.json).

Dùng prompt từ manifest validation-only đã audit. Chỉ chạy validation, lưu score và logprob 0/1. Khóa ngưỡng là bước riêng.

| Arm | Notebook | Bundle | Số prompt validation |
| --- | --- | --- | ---: |
| B1-full | [02_kaggle_qwen_q4_b1_full_validation.ipynb](02_kaggle_qwen_q4_b1_full_validation.ipynb) | [grace_b1_full_validation_inputs.zip](grace_b1_full_validation_inputs.zip) | 5.005 |
| B1-shuf | [02_kaggle_qwen_q4_b1_shuf_validation.ipynb](02_kaggle_qwen_q4_b1_shuf_validation.ipynb) | [grace_b1_shuf_validation_inputs.zip](grace_b1_shuf_validation_inputs.zip) | 15.015 |
| B2-nolabel | [02_kaggle_qwen_q4_b2_nolabel_validation.ipynb](02_kaggle_qwen_q4_b2_nolabel_validation.ipynb) | [grace_b2_nolabel_validation_inputs.zip](grace_b2_nolabel_validation_inputs.zip) | 5.005 |
| B2-labelonly | [02_kaggle_qwen_q4_b2_labelonly_validation.ipynb](02_kaggle_qwen_q4_b2_labelonly_validation.ipynb) | [grace_b2_labelonly_validation_inputs.zip](grace_b2_labelonly_validation_inputs.zip) | 5.005 |
| B2-rep | [02_kaggle_qwen_q4_b2_rep_validation.ipynb](02_kaggle_qwen_q4_b2_rep_validation.ipynb) | [grace_b2_rep_validation_inputs.zip](grace_b2_rep_validation_inputs.zip) | 5.005 |
| B2-rand | [02_kaggle_qwen_q4_b2_rand.ipynb](02_kaggle_qwen_q4_b2_rand.ipynb) | [grace_b2_rand_inputs.zip](grace_b2_rand_inputs.zip) | 15.015 |

1. Import notebook của arm muốn chạy. Chọn GPU T4 và bật Internet để cài thư viện và tải tokenizer revision đã pin.
2. Trong notebook inference, chọn **Add Input** và gắn hai nguồn riêng:
   - **Bundle prompt:** gắn đúng ZIP của arm trong bảng trên.
   - **Model:** chọn notebook [Qwen3Coder30B Prepare Notebook](https://www.kaggle.com/code/quangdung1111/qwen3coder30b-prepare-notebook) và dùng phiên đã lưu output chứa `qwen_gguf/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf`. Nếu chưa có phiên lưu output, chạy notebook chuẩn bị model rồi lưu phiên có output trước khi gắn.

   Runner tìm đúng một file GGUF theo tên trong các thư mục con của `/kaggle/input` và kiểm SHA-256 `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335` trước khi nạp model.
3. B2-rand cần thêm [checkpoint I-11](../../06_Arm_B2_Rand/output/kaggle_run_02/grace_b2_rand_checkpoint.zip) hoặc bản tiếp nối mới hơn chứa nguyên lịch sử I-11. Notebook giữ 7.789 record validation và chạy 7.226 lượt còn thiếu. Nếu gắn cả I-09 và I-11, notebook chọn bản chứa đầy đủ lịch sử; checkpoint khác lineage bị từ chối. Bundle lịch sử có cả input test nhưng notebook chỉ materialize validation và runner từ chối yêu cầu test trước khi load model.
4. Năm arm còn lại chạy lần đầu với bundle và model. Để tiếp tục ở session sau, Add Input chứa checkpoint ZIP mới nhất của chính arm đó. B2-rep dùng checkpoint riêng, cùng prompt B2 và gọi inference mới.
5. Tải checkpoint ZIP và log từ Kaggle Output. Mỗi phiên đặt ngân sách inference 9 giờ và dành 5 phút cuối để đóng gói checkpoint.

[Manifest và SHA-256](delivery_manifest.json)

## Backend áp dụng cho các lượt Kaggle

Dùng `llama-cpp-python==0.3.16` với Qwen3-Coder-30B-A3B-Instruct GGUF Q4_K_M đã pin SHA-256, tokenizer revision đã pin, hai GPU T4, context 8.192, batch 256 và full logits ở token đầu. Score là sigmoid(logit_1 − logit_0). Top-5 dùng cho chẩn đoán. Đây là đường chạy Kaggle được ghi trong preregistration của gói OSF và trong protocol vận hành. Mục serving của YAML trong ZIP đóng băng còn liệt kê llama-server/vLLM. Hai backend đó là phương án riêng và không dùng cho gói Kaggle này.

B2-rep ghi `repeat: true` và `tag: repeat` trong run manifest và records. Resume yêu cầu checkpoint B2-rep mang đủ hai trường. Nếu có checkpoint từ notebook cũ, giữ riêng để kiểm provenance.
