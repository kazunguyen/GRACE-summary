# Chuẩn bị B3 validation cho Google Colab - 05/11/2026

## Yêu cầu và phạm vi

Theo yêu cầu người dùng, tạo folder tương tự các arm hiện có trong GRACE-summary, chuẩn bị notebook chạy inference B3 validation và upload bundle bằng gdrive trên PowerShell. Sau đó người dùng yêu cầu dùng notebook/script tải model trực tiếp vào Drive, tương tự notebook chuẩn bị model trên Kaggle; áp dụng cách này thay chuyển toàn bộ model qua máy local.

Folder mới: ../09_Arm_B3_Contrastive/. Không commit/push, không chạy test inference, không sửa dữ liệu frozen, arm config, PDF/ZIP OSF hay khóa 14 ngưỡng. Workspace vốn có thay đổi chưa commit; giữ các thay đổi đó. Bổ sung mục riêng vào CHANGES_AFTER_PREREG.md theo AGENTS.md.

## Nguồn đã đọc và đối chiếu

- ZIP người dùng chỉ định: D:/JUNIOR/LabThayTho/grace_15arms_prompts_and_clean_specs (1).zip; SHA-256 9db0d3eebb66a2f83c1f9803ceb0192954a3dfe2c3de9515188a996ede84ed7b.
- PDF: D:/JUNIOR/LabThayTho/tmp/grace_worklog_push_20261104/Runs-management/osf_registration_draft_20261102/output/pdf/GRACE_OSF_PREREGISTRATION_20261102.pdf; đọc 10 trang, hash khớp 22648ead896baf5c1032de700c12fb97bd6dc44f0a8049292532ae6c0468b14c. Mục 5 và 7.2 xác nhận llama-cpp-python 0.3.16 full-logit scoring, không thay bằng llama-server/vLLM của bản nháp YAML.
- Notebook Kaggle B1-full và B2-rand, worklog audit B3 ngày 04/11, AGENTS.md trong repo.

## Artifact đã tạo

- notebooks/01_colab_download_preregistered_model_to_drive.ipynb: chạy Colab CPU, tải thẳng GGUF vào Drive, hỗ trợ resume .partial bằng HTTP Range, kiểm size + full SHA-256 rồi mới đổi tên. Không cần model đi qua máy cá nhân.
- notebooks/02_colab_qwen_q4_b3_validation.ipynb: validation Devign 2.732 + ReVeal 2.273, seed 42; mount Drive, xác minh bundle và runtime, kiểm GPU, build backend CUDA SM75, copy model vào /content để inference, checkpoint Drive mỗi khoảng 3 phút và finally.
- scripts/colab_inference.py: kế thừa logic Kaggle full-logit runner; thêm preflight đúng 2 T4, provenance môi trường, scope B3/validation/42, reserve token, smoke 20 prompt x 2, kiểm identity khi resume, checkpoint bền vững và phân biệt raw/score validity.
- scripts/finalize_validation.py: chỉ chọn tau sau đủ census cả hai dataset; lưới 0.01..0.99, tối ưu MCC, hòa gần 0.5 rồi ngưỡng nhỏ hơn; bỏ MCC không xác định. Xuất thresholds_B3_validation_candidate.json riêng cùng hash, không ghi đè configs/thresholds.json.
- scripts/download_model_to_drive.py, build_bundle.py, package_runtime.py, drive_helper.py, invoke_gdrive.ps1; README và delivery_manifest.json.
- Bundle input: output/bundles/grace_b3_validation_inputs.zip, 13.547.165 byte, SHA-256 5c86bcc4bcdc58e3e537941b98d73ce97c6f9d823002df7abca4474cc20b47bc. Gồm đúng hai validation split; không chứa test. Mỗi split giữ cả source_prompts.jsonl nguyên byte, normalized prompts có nhãn target metadata và manifest. Không thay đổi nội dung prompt.
- Runtime ZIP SHA và hash từng split nằm trong delivery_manifest.json. Notebook nhúng hash của bundle/runtime và abort khi lệch.

## Model và hợp đồng inference

Model ggml-org/Qwen3-Coder-30B-A3B-Instruct-GGUF / Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf; 17.988.419.552 byte; SHA-256 f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335. Đã đối chiếu metadata LFS của Hugging Face, ghim revision kho GGUF 0ca51122012fe4a20dc82988ee58780b008ce4e3 cho URL tải. Revision này là nguồn tải đối chiếu ngày 05/11, không nhầm với tokenizer revision b2cff646eb4bb1d68355c01b18ae02e7cf42d120 đã đăng ký. Identity chính vẫn là full SHA-256.

Giữ llama-cpp-python==0.3.16, transformers==4.57.1, n_ctx=8192, n_batch=256, n_gpu_layers=-1, logits_all=True, greedy và seed 42. Sử dụng logits của 0 và 1 ở token đầu để tính s; lưu top5 chỉ chẩn đoán. Score hợp lệ được giữ ngay cả khi raw greedy không phải chữ số. Tokenizer HF/GGUF kiểm từng prompt, context cộng reserve 64 token; không tự cắt lại prompt.

Smoke chạy 10 prompt trải đều mỗi dataset, mỗi prompt gọi hai lần; ghi kết quả riêng khỏi records census. Yêu cầu agreement greedy >=98%. Việc inference finite full logits không bị top5-gating.

## Khác biệt Kaggle -> Colab

- Drive thay Kaggle Input, /content thay /kaggle/working. Không hardcode thư viện CUDA của Kaggle. Ghi manifest Python, platform, driver, GPU, backend và runner SHA. Giữ các giá trị model/scoring/context/batch.
- Colab hosted không có tùy chọn ép 2 T4; nguồn chính thức về GPU cấp theo phiên: https://research.google.com/colaboratory/faq.html. Người dùng hỏi có thể ép lên 2 không; đã trả lời không. Chưa có đồng ý chuyển sang 1 T4 + CPU. Notebook vì thế giữ yêu cầu đúng 2 T4 và dừng sớm nếu thiếu. Custom/local runtime phải có sẵn Drive mount/sync, có thể cần sửa DRIVE_ROOT; không giả định drive.mount hoạt động trên local runtime.
- Session budget 9 giờ, chừa 600 giây đóng checkpoint; resume theo ID/hash. Đây là cắt phiên vận hành, không phải dừng theo metric. Chưa đủ census thì không chọn ngưỡng.

## Provenance/nội dung B3

Dùng đúng file render B3 nguyên bản trong ZIP (1), không dùng candidate remediation hoặc selector sau freeze. Specs chỉ được đọc để ghép nhãn target theo ID, không dùng demonstrations_pair để dựng lại prompt. Giữ nguyên 3.418 câu Key difference chung (1.776 Devign, 1.642 ReVeal).

Worklog ngày 04/11 vẫn ghi bất nhất cặp donor giữa prompt và specs, nguồn selection plan trước freeze chưa xác minh đầy đủ và nghiệm thu nội dung chưa hoàn tất. Bundle/runner giữ nhãn validation_only_provenance_and_content_audit_unresolved. Việc chuẩn bị theo yêu cầu hiện tại không tự đưa B3 vào manifest confirmatory hoặc khẳng định đã đạt audit. Ngưỡng candidate sau full validation còn cần gắn đúng provenance trước khi freeze dùng cho test.

## Upload Drive và chuyển hướng model

Drive folder: https://drive.google.com/drive/folders/1XgteUysal0pDEKs2HL9eR54ElgXrgUd3 . Upload dùng gdrive 3.9.1 thông qua PowerShell Start-Process -WindowStyle Hidden, chờ kết thúc, đọc remote file info và kiểm MD5 so bản local. Receipt/hash/ID và log tại output/drive_upload_receipts.json, output/drive_logs/. Không thay permissions công khai.

Ban đầu đã thử tải model theo phần 1 GiB vì mỗi ổ local chỉ trống khoảng 13 GiB. Khi người dùng chuyển sang notebook tải thẳng Drive, đã dừng helper, xóa chunk local do lượt này tạo, xóa chunk part000 trên Drive và thư mục model_q4_k_m_parts rỗng do lượt này tạo. Không có bản model đầy đủ nằm lại ở máy local. Giữ log lịch sử thử chuyển trong output/.

Model đầy đủ chưa được tải/chạy trong lượt chuẩn bị. Người dùng chạy notebook 01 trên Colab CPU để tạo model/model_verified.json trước notebook inference.

## Kiểm thử và giới hạn xác minh

8/8 test local đạt (9,03 giây): notebook nbformat + compile AST; full-logit score khi 0/1 ngoài top5; undefined MCC; toàn bộ 5.005 prompt đối chiếu nguyên văn ZIP; đủ census trước ngưỡng; checkpoint giữ bytes; downloader resume; sai checksum không trở thành model hợp lệ. Một test newline ban đầu lệch CRLF trên Windows đã sửa fixture dùng write_bytes, không đổi runner để hợp test.

Dependency kiểm thử bị thiếu ở Python máy; cài bổ sung vào output/test_deps riêng, không sửa môi trường global. Chưa thực thi smoke/inference CUDA thật hoặc tải đầy đủ model trên Colab; notebook sẽ thực hiện các bước này trên runtime người dùng. Không có kết quả validation hay tau B3 mới được tuyên bố trong worklog này.


## 06/11/2026 - Tạm xóa folder B3 theo yêu cầu người dùng

Đã xóa folder local D:/JUNIOR/LabThayTho/GRACE-summary/09_Arm_B3_Contrastive/ cùng notebook, script và output chuẩn bị trong folder đó. Đã kiểm đường dẫn tuyệt đối trước khi xóa và xác minh folder không còn. Folder đang untracked, chưa commit; lượt này không commit/push. Giữ worklog này làm lịch sử. Không thao tác xóa bundle/notebook trên Google Drive; liên kết và mô tả chuẩn bị phía trên phản ánh trạng thái trước khi xóa local. Không xóa các artifact B3 lịch sử ở thư mục khác.
