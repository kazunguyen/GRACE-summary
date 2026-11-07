# Bộ notebook validation của Hiếu áp dụng runtime lock — 07/11/2026

[ZIP bàn giao](../Runs-management/kaggle_validation_6arms_20261104/grace_hieu_5arms_runtime_locked_20261107.zip) chứa đúng năm notebook. SHA-256 của ZIP là `76a49a770897b7d0832ee87aa7d7e308ebbca57fdd7aaaf02f0f07f2400f156c`.

| Arm | Notebook trong ZIP | SHA-256 |
|---|---|---|
| B1-full | `02_kaggle_qwen_q4_b1_full_validation_runtime_locked.ipynb` | `17081f875e144f9aba440e43f70f80cf0eb4331c4004fa478bc55070d1724a0e` |
| B1-shuf | `02_kaggle_qwen_q4_b1_shuf_validation_runtime_locked.ipynb` | `8dfdd0691f01a9c535f36f9e66c97575a0d3e5b544f5ed8c531cfe56fe5c681c` |
| B2-rep | `02_kaggle_qwen_q4_b2_rep_validation_runtime_locked.ipynb` | `da5cf396129c56af7e1147f633f76a130798af1148da6a4a27b3fc9c0e14db3b` |
| B2-nolabel | `02_kaggle_qwen_q4_b2_nolabel_validation_runtime_locked.ipynb` | `595617850b725490a5ce58da996fbc9fb5bf5ef5cb1f3e9309dc77c4b9ccb957` |
| B2-labelonly | `02_kaggle_qwen_q4_b2_labelonly_validation_runtime_locked.ipynb` | `12880126d1b9aef6d415f64c738df2fd2303c534b87162f1eb1d01b7da710ba9` |

Lấy source từ năm notebook đã chạy trong ZIP Hiếu gửi, theo [audit log lịch sử](2026-11-07_hieu_5arms_runtime_audit.md). Các bản mới bắt đầu với cell output trống và nhúng nguyên byte [runtime lock](../configs/inference_runtime_lock.json), SHA-256 `85d8770839f80260cdc7c27b27b6cce6bf8815675c8593db68fb102589c5cbd6`.

- Kiểm tra SHA file và checksum canonical của lock. Cài đủ sáu phiên bản từ lock, xác minh SHA source archive của llama-cpp-python trước khi build, rồi kiểm tra lại phiên bản đã cài và nguồn backend trước inference.
- Áp dụng constructor từ lock, gồm context/batch/microbatch `8192/256/256`, inference seed `4294967295`, layer split theo VRAM và công thức CPU threads đã chốt. Dừng trước scoring nếu log thiếu hai GPU T4, offload `49/49` hoặc kích thước batch hiệu dụng đúng. Ghi phiên bản build, dependency freeze, hash runner/backend, thông tin GPU và log load model theo từng phiên.
- Dùng model và bundle validation hiện có. Kiểm tra hash frozen manifest cả khi Kaggle bung ZIP, tokenizer revision, token ID và prompt hash. Scoring giữ nguyên, gồm isolation `repeat=True` và `tag='repeat'` cho B2-rep. Đây là bộ bàn giao validation, chưa sinh kết quả mới hoặc tác động phân tích confirmatory.
- Chọn Kaggle T4×2, bật Internet, gắn model và bundle của arm, rồi Run All. Lần đầu chạy từ đầu. Từ lần sau, dùng checkpoint `*_runtime_locked_checkpoint.zip` có cùng contract. Notebook ghi contract hash vào manifest và record, tách thư mục kết quả, từ chối checkpoint lịch sử và tính ngân sách chín giờ từ đầu phần setup để dành thời gian xuất checkpoint.

Kiểm tra local gồm schema notebook, biên dịch code cells và module nhúng, đối chiếu byte lock, nạp bundle thật dạng ZIP và thư mục Kaggle giải nén, từ chối checkpoint cũ và manifest sai hash, cùng kiểm tra constructor/offload bằng stub. Chưa build CUDA hoặc chạy GPU trên Kaggle. Ba bộ kiểm tra repo chạy trên HEAD trước khi staging cho kết quả 36 pass, một lỗi có sẵn ở `test_thresholds_json_synchronization` vì test đòi `reseal_reason` chứa B1-H2, trong khi metadata hiện tại ghi lần bổ sung B2-rand.
