# B3-swap và B3-flip — bộ test verified-patch v1

Ngày chuẩn bị: 10/11/2026 (Asia/Saigon). Phạm vi: mỗi arm gồm Devign test **2.732** và REVEAL test **2.274**, prompt seed **42**. Hai arm thuộc cùng `AMENDED_EXPLORATORY_SUBPROTOCOL` với B3 verified-patch; không thay thế hồ sơ OSF gốc.

Trạng thái nghiệm thu local nằm trong `PREPARATION_AUDIT.json`, đối chiếu runtime trong `REFERENCE_RUNTIME_AUDIT.json`, kết quả kiểm thử trong `TEST_RESULTS.txt`. Chỉ coi bộ local sẵn sàng khi cả ba hồ sơ đều đạt. Chưa upload, chưa launch, chưa chứng nhận runtime GPU cho hai arm này.

## Nguồn chuẩn và cách dựng prompt

- Nguồn B3: `../test_release_20261109_v1/`, manifest niêm phong và đủ census test. Bản notebook mẫu là B3 v6 đã sửa mount dạng nested/symlink và `INPUT_DIR`.
- Dùng **cùng** `VerifiedPairSelector.render_family`, `grace_diag.probes.render_arm`, `TokenCounter.fit` và snapshot tokenizer revision `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`. Không có thuật toán cắt tỉa riêng trong notebook.
- Dựng lại B3 từ frozen specs và reviewed pools; yêu cầu prompt và selection khớp chính xác bản B3 niêm phong trên từng target, rồi mới nhận biến thể của cùng family.
- B3-swap: đổi thứ tự hai demonstration, nhãn đi cùng đúng code gốc; giữ nguyên `Key difference`.
- B3-flip: giữ thứ tự và code của hai demonstration, đảo nhãn hiển thị; **đảo các từ chỉ nhãn trong `Key difference` bằng `_flip_words`**, đúng renderer hiện có. Ghi chú trước đây yêu cầu giữ nguyên mọi chữ của `Key difference` cho flip đã không mô tả đúng renderer và được thay bằng quy tắc này.
- Các khối role/target/question/graph/answer, pair ID và payload hash phải giống B3. Donor function và giải thích đầy đủ; không cắt mất bằng chứng của pair. Target/graph được cắt bằng chính renderer chung.
- Kiểm tra toàn census: Figure 6, code ≤3.000, graph ≤1.500, demo ≤1.500, chat +64 ≤8.192 token. Không dùng xấp xỉ. Target labels giữ bên ngoài Kaggle input.

## Tệp bàn giao

| Đường dẫn | Công dụng |
|---|---|
| `b3_swap/kaggle_kernel/notebook.ipynb` | Notebook B3-swap, hai tập test |
| `b3_flip/kaggle_kernel/notebook.ipynb` | Notebook B3-flip, hai tập test |
| `<arm>/kaggle_kernel/kernel-metadata.json` | Private kernel, T4, timeout 9 giờ, nguồn input/model |
| `<arm>/kaggle_dataset/kaggle_input.zip` | Prompt, reviewed pool, threshold locks và runtime lock; không chứa target labels |
| `<arm>/kaggle_dataset/test_release_manifest.json` | Niêm phong inventory, prompt/worker/runtime/threshold identity |
| `shared_worker/` | Cùng worker chấm điểm và helper cho cả hai notebook |
| `PREPARATION_AUDIT.json` | Kết quả dựng và kiểm tra prompt theo từng arm/dataset |
| `REFERENCE_RUNTIME_AUDIT.json` | So sánh trực tiếp ZIP năm arm và evaluator |

Hai notebook dùng chung format **1 cell Markdown + 5 cell code** của B3 v6: bootstrap → preflight input/model → cài/build → kiểm tra môi trường → inference. Hai cell cài/build và kiểm tra môi trường giống nguyên source với B3 v6; worker nhúng của swap và flip giống nguyên byte. Chỉ đổi arm, prompt release, manifest hash, input/output identity. Các notebook validation lịch sử trong ZIP năm arm có thêm các cell checkpoint/diagnostics; không sửa các bản lịch sử để thay đổi bằng chứng đã chạy.

## Runtime và evaluator chung

ZIP đối chiếu: `Runs-management/grace_hieu_5arms_runtime_locked_20261107.zip`, SHA-256 `76a49a770897b7d0832ee87aa7d7e308ebbca57fdd7aaaf02f0f07f2400f156c`.

Lock mới dùng nguyên byte của B3: `4c9c3bcff5e9fd32532d7edf85df7a961e45ec9c64bee3df8833d986a2eb276e`. Model/tokenizer/backend/constructor/GPU/scoring/threads/build/decoding/resume khớp ZIP cũ. Package bổ sung so với bản ZIP sáu package là `scipy==1.16.3`, theo `worklogs/2026-11-07_kaggle_package_lock_standardization.md`.

- Bảy pin: llama-cpp-python 0.3.16, transformers 4.57.1, huggingface-hub 0.36.2, tokenizers 0.22.2, numpy 2.1.3, scipy 1.16.3, scikit-learn 1.5.2.
- T4 ×2; layer split theo free VRAM, `tensor_split=null`, `main_gpu=0`, `n_gpu_layers=-1`, offload **49/49**. Không ép tỷ lệ cố định 25/24; tỷ lệ thực tế phải ghi trong native log.
- Context/batch/ubatch **8192/256/256**. Constructor seed sentinel **4294967295** theo lock; prompt seed 42. Scoring đọc logits trực tiếp, không sampling.
- Xác minh model SHA, tokenizer HF/GGUF token IDs, source archive SHA trước build, package versions, runtime integrity và helper/worker hashes trước scoring.
- `binary_scores` có AST giống cả năm runner trong ZIP: reset → eval → last-position full-vocabulary logits → float64 log-softmax → `s=exp(lp1-logaddexp(lp0,lp1))`. Giữ score hữu hạn khi raw argmax không phải `0/1` theo policy chung.
- Worker chạy prompt đã niêm phong, không format/cắt lại; checkpoint identity có arm, release, prompt/model/runtime/threshold hash. Không dùng cache/kết quả của B3 làm output probe.
- Threshold kế thừa nguyên byte B3 validation: Devign **0,99**, REVEAL **0,01**; không fit lại trên variant hoặc test.

## Cách triển khai

1. Dùng đúng thư mục của arm. Metadata hiện trỏ tới `lznt123`, như bản B3 mẫu. Tạo dataset **private** từ `kaggle_dataset/`; kiểm tra quyền đọc model notebook `lznt123/qwen3coder30b-prepare-notebook`. Nếu đổi account, phải cập nhật metadata/mount và kiểm tra lại trước launch.
2. Gắn đúng dataset của arm, bật Internet và chọn **2×T4**. Metadata bật GPU chưa chứng minh Kaggle cấp đúng hai GPU; preflight bắt buộc kiểm số lượng và loại GPU.
3. Upload notebook từ `kaggle_kernel/`, đọc lại source remote đối chiếu với file/hash local; chỉ chạy sau khi khớp. Không thay worker nhúng thủ công.
4. Run All từ phiên sạch. Worker dừng an toàn trước hạn chín giờ với reserve 300 giây. Đây là giới hạn hạ tầng, không phải dừng theo kết quả. Thư mục output có sẵn bị từ chối ghi đè. Nếu cần resume, thu checkpoint và kiểm cùng identity rồi chuẩn bị revision resume riêng.
5. Thu toàn output, status, records, run manifests, runtime provenance, native offload log và build/install logs sau phiên. Đối chiếu mỗi phiên tạo record với runtime lock; chỉ nghiệm thu khi đủ 49/49 offload, đúng hai T4, đầy đủ hashes và census 2.732/2.274.
6. Sau khi kiểm tra records và runtime, ghép nhãn **ở local**. Adapter chung: `scripts/evaluate_b3_probe_test_20261110.py`; nó gọi `grace_diag.evaluate_final.table_a`, đọc lock B3 và từ chối census thiếu. Không chỉnh `configs/thresholds*.json` để đưa threshold amended vào hồ sơ gốc.

Ví dụ đánh giá sau khi tải output (chạy từ repo):

```powershell
python scripts/evaluate_b3_probe_test_20261110.py --release Runs-management/b3_verified_patch_v1/probe_test_release_20261110_v1/b3_swap --output-root <thu_muc_output_worker> --labels Runs-management/b3_verified_patch_v1/test_release_20261109_v1/private_evaluation_only/test_labels.json --out <thu_muc_metrics_moi>
```

Đổi `b3_swap` thành `b3_flip` cho arm còn lại. Kết quả metrics không tự chứng nhận runtime; biên bản runtime theo từng session vẫn bắt buộc.

## Kiểm tra local và tái lập

Script dựng: `scripts/build_b3_probe_delivery_20261110.py`. Script đối chiếu ZIP: `scripts/audit_b3_probe_reference_20261110.py`. Bộ kiểm tra thực: `tests/test_b3_probe_delivery.py`, kiểm đủ census, biến đổi demonstration, threshold tamper, nhầm arm khi resume, helper/scoring identity và notebook nhúng.

B3-nodiff: người dùng xác nhận Dũng đã chạy ngày 10/11/2026. Cần đối chiếu output và nghiệm thu runtime/threshold riêng; trạng thái đó không được coi là bằng chứng đã nghiệm thu.
