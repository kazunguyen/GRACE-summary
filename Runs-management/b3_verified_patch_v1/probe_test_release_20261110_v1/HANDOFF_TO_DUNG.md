# Handoff B3-swap / B3-flip cho Dũng

**Cập nhật 10/11:** B3-swap đã được submit trên `thanhduy9a4tv` theo chỉ đạo của Hiếu; xem [status](../../b3_swap_launch_20261110/STATUS.md) trước khi chạy thêm B3-swap. B3-flip vẫn ở trạng thái chuẩn bị local. B3 test base tiếp tục do Dũng đảm nhận như đã phân công.

Pull nhánh `docs/b1-shuf-runtime-b3-queue-20261109`. Thư mục dùng trực tiếp sau pull là `15_Arm_B3_Swap/` hoặc `16_Arm_B3_Flip/` ở repo root. Notebook, metadata và manifest đã được đặt sẵn tại đó:

```text
b3_swap/ hoặc b3_flip/
├── kaggle_kernel/
│   ├── kernel-metadata.json
│   └── notebook.ipynb
└── kaggle_dataset/
    ├── dataset-metadata.json
    ├── test_release_manifest.json
    ├── test_release_manifest.sha256
    └── kaggle_input.zip   # nhận qua gói ZIP chuyển riêng, không commit Git
```

ZIP chuyển riêng: `B3_SWAP_FLIP_TEST_READY_20261110_v1.zip`, SHA-256 `27ce96bab4ac8bab5c318e641f820fec5c38fe1fc3fdd8a4381640819eb336cc`. Mỗi thư mục arm ở repo root có sẵn Kaggle notebook và metadata. Input ZIP được chuyển riêng; đặt ZIP tương ứng vào `kaggle_dataset/kaggle_input.zip` rồi xác minh SHA-256 theo manifest. Không sửa notebook hoặc nội dung input sau khi kiểm checksum.

Mỗi `kaggle_input.zip` trong dataset có SHA-256 ở manifest tương ứng và chỉ chứa prompt/pool/threshold/runtime lock, không có nhãn target. Upload riêng từng `kaggle_dataset/` thành Kaggle dataset private cùng tên metadata. Sau đó kiểm tra ID nguồn dữ liệu trong kernel metadata; kernel hiện trỏ `lznt123`. Model source hiện trỏ notebook `lznt123/qwen3coder30b-prepare-notebook`.

Trên Kaggle chọn 2×Tesla T4 và bật Internet. Đọc lại toàn bộ code cell từ phiên bản remote; so từng source với notebook trong Git trước khi chạy. Notebook dừng nếu thiếu input, hash sai, model sai hoặc GPU không đạt lock. Lưu output hoàn chỉnh và logs/provenance. Runtime chưa được nghiệm thu cho hai arm trước khi có chứng cứ hai T4, 49/49 offload và census đầy đủ 2.732 Devign + 2.274 REVEAL.

Threshold dùng nguyên khóa B3: Devign 0,99; REVEAL 0,01. Không tính lại trên probe/test. Khi output đủ, đánh giá ở local bằng `scripts/evaluate_b3_probe_test_20261110.py` cùng target labels local.
