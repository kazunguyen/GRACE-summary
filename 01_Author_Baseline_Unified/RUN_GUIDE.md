# Hướng dẫn chạy baseline GRACE

## Môi trường được khóa

Lockfile dành cho **Linux x86-64, CPython 3.11.0**, dùng các gói PyPI có hash SHA-256 trong `requirements.lock`. Các phụ thuộc trực tiếp và gián tiếp được khóa; không cài từ `requirements.in` cho thực nghiệm. PyTorch 2.7.1 là bản PyPI Linux với các gói CUDA được khóa trong lockfile. Máy GPU cần driver NVIDIA tương thích và GPU hỗ trợ BF16. Driver, GPU, hệ điều hành, BLAS và trạng thái môi trường không được khóa bởi pip: ghi lại chúng khi công bố kết quả. Qwen BF16 chiếm khoảng 61 GB trên đĩa, còn bộ nhớ chạy phụ thuộc cấu hình.

Tạo môi trường sạch với Python 3.11.0 có sẵn, tại thư mục này:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --require-hashes -r requirements.lock
python -m pip check
python test_baseline.py
```

Lockfile được giải bằng `uv 0.11.17` cho Linux x86-64; không dùng nó làm lockfile Windows hoặc môi trường Kaggle có sẵn. Cài đặt cần truy cập PyPI; lần chạy thật đầu tiên cần Hugging Face. Không tự nâng cấp thư viện trong cùng một thí nghiệm.

## Chạy thử offline

```bash
python run_pipeline.py --mock --dataset mock --max-targets 10 --experiment-name smoke_test
```

Mock dùng dữ liệu tổng hợp, embedding TF-IDF và bộ sinh giả; không dùng kết quả này để đối chứng model thật.

## Chạy thực nghiệm

```bash
python run_pipeline.py --dataset devign --max-targets 50 --experiment-name devign_qwen_run1
```

Cả tokenizer và weights của Qwen và CodeT5 được tải theo commit ghi trong `evaluation_contract.yaml`; lỗi tải CodeT5 hoặc dataset không tự chuyển sang mock. Lựa chọn `--profile code` là mặc định; `--profile paper` là nhánh t-SNE riêng. Tham số sinh dùng greedy decoding, tối đa 256 token; prompt tối đa 8.192 byte.

**Dữ liệu CPG:** loader ưu tiên các file local được liệt kê trong `data_loader.py` trước Hugging Face. Những file local đó chưa có hash hoặc quy trình tạo CPG được khóa trong kho này; cần lưu SHA-256, nguồn, phiên bản công cụ tạo đồ thị và xác minh cùng một file trước khi so sánh. Bản tải dataset từ Hugging Face có revision được khóa trong contract nhưng không bảo đảm có CPG tương đương file đã xử lý. Nếu không có dữ liệu đồ thị phù hợp, không coi kết quả là đối chứng GRACE đã xác nhận.

Kết quả nằm trong `output/<experiment-name>/`; checkpoint trong `checkpoints/`. Dùng tên experiment mới khi đổi model, dữ liệu, mã, môi trường hay tham số: checkpoint cũ được nối lại theo ID và không tự kiểm tra cấu hình. Lưu revision git của mã, lockfile, hash dữ liệu, phần cứng/driver và toàn bộ artifacts cho mỗi lần chạy. Khóa phiên bản không đảm bảo kết quả giống từng bit giữa phần cứng hoặc runtime khác nhau.
