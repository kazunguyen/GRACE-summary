# B2 — inference lại 66 mẫu sau thống nhất donor

Bundle để upload lên Kaggle: **`output/grace_b2_devign_donor_rerun_66_20261102.zip`**.

| Dataset | Arm | Split | Prompt cần inference |
|---|---|---|---:|
| Devign | B2 | validation | 28 |
| Devign | B2 | test | 38 |
| Tổng | | | **66** |

`prompts.jsonl` trong ZIP chứa đúng 66 prompt đã thay demo, giữ nguyên ID, nhãn target, code target, graph 40/80, câu dẫn và hash prompt đã đối chiếu. Đây là một phiên bổ sung của **arm B2**, không phải arm mới. REVEAL và B0 không có trong bundle.

## Nội dung ZIP

- `prompts.jsonl`: 66 prompt, sắp validation trước test; notebook lọc theo `row['split']`.
- `splits/devign/validation/prompts.jsonl`: riêng 28 prompt validation.
- `splits/devign/test/prompts.jsonl`: riêng 38 prompt test. Hai file này là cách chia cùng 66 prompt ở trên, không phải thêm lượt inference.
- `bundle_manifest.json`: số mẫu, hash file, phiên donor và model/tokenizer/backend cần giữ để ghép với kết quả cũ.
- `rerun_audit.jsonl`, `mau_can_inference_lai.csv`: ID target, demo cũ/mới, hash trước/sau và nguồn output đã có.
- `validation_support/reusable_records.jsonl`: **2.704 score validation cũ** còn tương thích, chỉ để ghép kết quả.
- `validation_support/expected_full_validation.jsonl`: ID, nhãn và hash prompt của toàn bộ **2.732 mẫu validation phiên mới**.
- `validation_support/original_run_manifest.json`: cấu hình inference của kết quả cũ.
- `validation_lock.py`: helper CPU chọn/khóa ngưỡng từ validation đầy đủ, giống công cụ hiện có.
- `verify_bundle.py`: đọc và kiểm tra bundle bằng Python chuẩn, không cần GPU.
- `provenance/`: snapshot kiểm toán và dấu vết retrieval của lần đổi donor.

## Yêu cầu cho notebook inference riêng

1. Tìm ZIP dưới `/kaggle/input` bằng tên hoặc `bundle_id` trong manifest; không phụ thuộc username Kaggle. Chạy `verify_bundle.py` hoặc kiểm tra các hash tương đương trước inference.
2. Dùng đúng model GGUF Q4_K_M với SHA-256 trong manifest, tokenizer Qwen đã pin và `llama-cpp-python==0.3.16`. Giữ seed 42, context 8.192, cách lấy score `unconstrained_first_token_logits_v1` và chat template gốc. Không sinh lại prompt hoặc chọn lại demo trên Kaggle.
3. Inference **28 validation**; ghép với **2.704** `reusable_records` theo ID/hash để có đủ **2.732 validation**. Dùng helper `make_lock` và `persist_lock` tạo `thresholds.json` **riêng cho phiên mới**, với `full_validation_prompt_set_sha256` trong manifest. Không fit ngưỡng trên riêng 28 mẫu.
4. Sau khi khóa ngưỡng phiên mới, inference **38 test**. Lưu output tại thư mục riêng, giữ `arm='B2'`, `dataset='devign'`, split/ID/hash prompt mới và hash model đúng. Checkpoint phải so cả ID/hash prompt/model; prompt cũ của 66 ID này không được coi là đã hoàn thành prompt mới.
5. Tải về `records.jsonl` validation/test, `run_manifest.json` và khóa ngưỡng mới để ghép với phần output cũ còn tương thích. Số lượt LLM bổ sung là **66**; score validation kèm theo không cần inference lại.

Ví dụ đọc ZIP trong notebook sau khi xác định đường dẫn:

```python
import json, zipfile
from pathlib import Path

matches = list(Path('/kaggle/input').rglob('grace_b2_devign_donor_rerun_66_20261102.zip'))
assert len(matches) == 1, matches
bundle = matches[0]
with zipfile.ZipFile(bundle) as z:
    exec(compile(z.read('verify_bundle.py'), 'verify_bundle.py', 'exec'), ns := {'__name__': 'bundle_verifier'})
manifest, rows = ns['load_bundle'](bundle)
validation = [r for r in rows if r['split'] == 'validation']
test = [r for r in rows if r['split'] == 'test']
assert (len(validation), len(test)) == (28, 38)
```

Folder này chuẩn bị bundle; chưa tạo notebook inference hoặc gọi LLM. Không ghi đè prompt/output/threshold của chiến dịch cũ.

Đóng gói lại bằng `python build_bundle.py`. Kiểm tra bằng `python verify_bundle.py output/grace_b2_devign_donor_rerun_66_20261102.zip`.

Nguồn danh sách: [báo cáo đối chiếu donor](../Runs-management/donor_reconciliation_20261101/KET_QUA_DOI_CHIEU.md).
