# B2-rand validation notebook: package runtime lock — 07/11/2026

Đã cập nhật notebook tiếp tục validation [02_kaggle_qwen_q4_b2_rand.ipynb](../06_Arm_B2_Rand/notebooks/02_kaggle_qwen_q4_b2_rand.ipynb) để nguồn cài đặt và kiểm tra phiên bản đọc trực tiếp từ [`configs/inference_runtime_lock.json`](../configs/inference_runtime_lock.json).

## Các kiểm tra khi chạy

- Notebook nhúng bản JSON đã khóa, xác minh SHA-256 của file và `integrity.sha256`; dừng nếu working directory có bản lock khác.
- Cài đúng các package đã khai báo: NumPy 2.1.3, huggingface-hub 0.36.2, tokenizers 0.22.2, Transformers 4.57.1, llama-cpp-python 0.3.16 và scikit-learn 1.5.2. Phiên bản thực tế được so sánh chính xác với lock trước inference.
- Tải source archive llama-cpp-python theo metadata PyPI, kiểm tra SHA-256 đã khóa trước khi build.
- Ghi `pip freeze --all` vào gói diagnostics để giữ danh sách package transitives; lưu runtime-lock SHA và danh sách package trực tiếp trong run manifest và record mới.
- Cập nhật SHA notebook trong delivery manifest. Xóa outputs cũ gắn với source trước khi sửa; output Kaggle lịch sử vẫn nằm trong Runs-management.

## Phạm vi

Các phiên bản package được ghi sẵn trong notebook trước đó vốn trùng với sáu phiên bản trong lock; thay đổi này làm lock thành nguồn cấu hình duy nhất và biến sai lệch thành lỗi dừng sớm. Notebook chưa được chạy lại trên Kaggle sau khi sửa. Các khóa ngưỡng và checkpoint không bị thay đổi.

## Sửa lỗi resume từ notebook Kaggle mới tải về

Traceback mới cho thấy bundle và model đã được tìm thấy, runner đã khởi động, rồi dừng tại kiểm tra `run_manifest.json` với `Existing output has different model/run settings for devign/validation`. Nguyên nhân là lần tích hợp package lock trước đã thêm `runtime_lock_sha256` và `runtime_packages` vào phần identity dùng để so sánh resume; manifest I-15 cũ không có hai trường provenance mới. Đây không phải lỗi đọc nhầm file input.

Đã tách hai trường runtime lock khỏi identity suy luận ổn định. Manifest sau khi qua kiểm tra sẽ ghi riêng runtime lock, package versions và trạng thái adoption. Cho phép tiếp tục duy nhất cặp I-15 seed44/Devign validation đã xác thực bằng SHA-256: manifest `1f7fa83e76b56e6a20179ebf4701dd0e83f26fe4dc00f9e9375007e5fc40c574`, records `2f5a5297d4060c7235f950c21355d4675dbc41b17b50e86bc72d300dc15dffd7`. Log I-15 xác nhận sáu package, model, backend version, context/batch và offload phù hợp; các record lịch sử vẫn giữ provenance gốc, record mới sẽ mang hash lock. Checkpoint legacy khác hoặc có nội dung đổi sẽ bị từ chối.

Hai notebook test dùng kiểm tra hash cho từng file và hỗ trợ ZIP Kaggle tự giải nén. Cách đọc input đó xử lý lỗi archive-layout; traceback validation lần này xảy ra sau khi đã chọn đúng model và bundles. Test notebooks chạy mới từ đầu nên giữ kiểm tra runtime identity nghiêm ngặt, còn notebook validation có allowlist riêng cho cặp I-15 đã kiểm chứng để resume.
