# Khóa SciPy 1.16.3 cho notebook inference Kaggle

Ngày 07/11/2026, Dũng chốt `scipy==1.16.3` vào runtime lock chung. Đây là phiên bản ghi trong các log Kaggle sau cài đặt đã đối chiếu. Lần seed 44 báo `Runtime contract file SHA-256 mismatch` đã dừng ở setup. Danh sách package trong log lỗi đó là phiên bản của ảnh nền Kaggle trước bước cài theo lock.

- Lock: [configs/inference_runtime_lock.json](../configs/inference_runtime_lock.json). SHA-256 file `bf1f859dc786e206a3c11d655b04b528dc68f59a15a82d4db894ac5944b0ac2e`. SHA-256 canonical payload `d79396de5d37ca6c3123ac05ea122d665f5f9b252aa0b32ac2b5c464b68e338f`.
- Bảy phiên bản được kiểm tra sau cài đặt: `llama-cpp-python==0.3.16`, `transformers==4.57.1`, `huggingface-hub==0.36.2`, `tokenizers==0.22.2`, `numpy==2.1.3`, `scipy==1.16.3`, `scikit-learn==1.5.2`.
- Đồng bộ 23 file notebook Kaggle của 13 arm có notebook trong cây làm việc, gồm các bản validation và test được dùng để chạy tiếp. Tạo [ZIP mới cho Hiếu](../Runs-management/kaggle_validation_6arms_20261104/grace_hieu_5arms_runtime_locked_scipy1163_20261107.zip) chứa năm notebook có kiểm tra toàn bộ runtime lock. SHA-256 ZIP `1a1706c0bf8e232e63f97e4c48078122c0b44a268d3c75911bb948923511aa31`. ZIP trước được lưu làm lịch sử bàn giao.
- Khôi phục cell cài đặt riêng của B2-rand validation và test seed 42–44 sau khi phát hiện lần đồng bộ trước đã ghép hai đoạn mã gây lỗi cú pháp. Giữ cách nhận input test dạng ZIP hoặc thư mục đã giải nén và quy tắc kiểm tra danh tính checkpoint của runner. Với notebook có kiểm tra SHA runtime trong checkpoint, checkpoint tạo với SHA lock cũ thuộc một runtime khác.
- Phạm vi là phiên bản package cho lần chạy Kaggle tiếp theo. Một số notebook chỉ áp dụng phần package. Các cấu hình khác như GPU split, seed và provenance cần được kiểm tra riêng trước khi tuyên bố toàn bộ runtime tuân thủ lock. Trong cây làm việc chưa tìm thấy notebook Kaggle riêng cho B3-swap và B3-flip. Colab dùng profile khác. Kết quả lịch sử giữ provenance của phiên thực thi, gồm `tokenizers==0.23.1` ở một số phiên cũ.

Kiểm tra local gồm cú pháp Python của cell, byte lock nhúng, SHA helper và hash notebook trong manifest. Chưa chạy cài đặt hoặc inference trên GPU Kaggle.

B2-rand seed 44: local input loading verified 2,732 Devign and 2,274 REVEAL prompts with the original ZIP, the outer ZIP unpacked, and both inner ZIPs unpacked. The loader accepts an unpacked directory even if its name ends in .zip. The seed 44 test bundle SHA-256 remains e8bf81b3d5355a19221f7e61bbe19af81a31c953fd929c8e642918f67659590d.
