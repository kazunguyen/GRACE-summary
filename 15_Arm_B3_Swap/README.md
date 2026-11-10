# B3-swap — Kaggle test delivery

Đây là thư mục chạy chính thức của arm B3-swap. Sau khi pull nhánh `docs/b1-shuf-runtime-b3-queue-20261109`, các file cần xem nằm ngay dưới đây:

```text
15_Arm_B3_Swap/
├── kaggle_kernel/
│   ├── notebook.ipynb
│   └── kernel-metadata.json
└── kaggle_dataset/
    ├── dataset-metadata.json
    ├── test_release_manifest.json
    ├── test_release_manifest.sha256
    └── kaggle_input.zip  # ZIP prompt được chuyển riêng, không commit Git
```

`notebook.ipynb` là bản B3-swap đã kiểm tra. Manifest chứa SHA-256 của `kaggle_input.zip`; kiểm tra hash trước khi upload dataset. ZIP đã chuyển riêng có SHA-256 `27ce96bab4ac8bab5c318e641f820fec5c38fe1fc3fdd8a4381640819eb336cc` (gói bàn giao ngoài; bên trong có ZIP input riêng cho từng arm). Đặt đúng ZIP B3-swap vào `kaggle_dataset/kaggle_input.zip`; không sửa nội dung prompt hay manifest.

## Đặc tả arm

- Mỗi test prompt dùng chính target, graph và cặp donor mà B3 đã chọn. Thay đổi duy nhất là đảo thứ tự hai khối demonstration; nhãn vẫn đi cùng đúng mã nguồn. `Key difference` được giữ nguyên.
- Census: Devign 2.732; REVEAL 2.274; seed 42. Nhãn target không nằm trong input Kaggle.
- Kế thừa nguyên khóa threshold B3 từ validation: Devign 0,99; REVEAL 0,01. Không tối ưu lại threshold.
- Dùng cùng evaluator, exact tokenizer, cắt tỉa, worker và runtime lock với notebook B3 v6. Model Qwen3-Coder-30B-A3B-Instruct GGUF Q4_K_M; contract yêu cầu hai Tesla T4, context 8192, batch/ubatch 256 và offload 49/49.

## Trước khi chạy

1. Kiểm tra SHA-256 của ZIP khớp `test_release_manifest.json`, rồi tạo Kaggle dataset **private** theo `dataset-metadata.json`.
2. Tạo kernel từ `kaggle_kernel/`; kiểm tra account/dataset IDs trong `kernel-metadata.json` và quyền đọc model notebook được khai báo.
3. Chọn 2×Tesla T4, bật Internet; đọc lại remote notebook source và so với file trong Git trước Run All.
4. Sau chạy, tải toàn bộ output, status, logs và provenance. Chỉ nghiệm thu runtime khi xác nhận hai T4, offload 49/49, hash chain đúng và census đủ.

Hướng dẫn handoff chi tiết: [`HANDOFF_TO_DUNG.md`](../Runs-management/b3_verified_patch_v1/probe_test_release_20261110_v1/HANDOFF_TO_DUNG.md). Hồ sơ prompt/runtime: [`probe release README`](../Runs-management/b3_verified_patch_v1/probe_test_release_20261110_v1/README.md).

Trạng thái: **đã chuẩn bị và kiểm tra local; chưa upload hoặc nghiệm thu runtime Kaggle**. Arm thuộc amended/exploratory B3 protocol.
