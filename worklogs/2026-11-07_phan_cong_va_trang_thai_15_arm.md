# Phân công và trạng thái đủ 15 arm LLM — 07/11/2026

Phạm vi: 15 arm gọi LLM trong đề cương mục 6.3, không gồm các mốc sàn, supervised, meta-model và routing. Phân biệt đã bàn giao, có output inference và trạng thái cloud; code/bundle hoặc dry-run không phải bằng chứng đã inference.

| Arm | Người thực hiện/được giao | Trạng thái có bằng chứng |
|---|---|---|
| B0 | Dũng | Đủ 5.005 validation + 5.006 test trên Kaggle, output đã nhập. |
| B1 | Dũng | Đủ 5.005 validation + 5.006 test trên Kaggle, output đã nhập. |
| B1-full | Giao Hiếu | Đã có notebook/bundle bàn giao; chưa xác nhận Hiếu đã chạy hay chưa chạy bằng output/link runtime. |
| B1-H2 | Dũng | Colab đã đủ 5.005 validation + 5.006 test, giữ exploratory. Đã có thêm Kaggle validation 5.005/5.005 và khóa ngưỡng riêng; Kaggle test mới ở bước chuẩn bị, chưa có kết quả nhập. |
| B1-shuf | Giao Hiếu | Đã có notebook/bundle 3 seed; chưa xác nhận trạng thái thực thi của Hiếu. |
| B2 | Dũng | Đủ 5.005 validation + 5.006 test; phiên donor mới đã ghép 66 mẫu rerun theo ledger. |
| B2-rand | Dũng | Live Kaggle status RUNNING khi kiểm tra lượt này. Checkpoint đã xác minh gần nhất I-11 có 7.789/15.015 validation; chưa có số đếm checkpoint mới của phiên đang chạy. Test chưa có output được xác minh. |
| B2-nolabel | Giao Hiếu | Đã bàn giao; chưa xác nhận trạng thái thực thi của Hiếu. |
| B2-labelonly | Giao Hiếu | Đã bàn giao; chưa xác nhận trạng thái thực thi của Hiếu. |
| B2-flip | Dũng | Đủ 5.005 validation + 5.006 test trên Kaggle I-10, output đã nhập. |
| B2-rep | Giao Hiếu | Đã bàn giao notebook/bundle và checkpoint isolation; chưa xác nhận trạng thái thực thi của Hiếu. |
| B3 | Chưa ghi nhận người đã inference | Họ B3 cũ tạm hoãn sau audit; hướng sửa mới có implementation/smoke, chưa phải inference thật. |
| B3-nodiff | Chưa ghi nhận người đã inference | Như B3; chưa có output inference được ghi nhận. |
| B3-swap | Chưa ghi nhận người đã inference | Như B3; chưa có output inference được ghi nhận. |
| B3-flip | Chưa ghi nhận người đã inference | Như B3; chưa có output inference được ghi nhận. |

Số arm: 6 arm Dũng đã/đang chạy; 5 arm đã giao Hiếu nhưng chưa phân loại được đã chạy/chưa chạy; 4 arm họ B3 chưa có inference được ghi nhận. Không được suy từ thiếu output local thành Hiếu chưa chạy. Đã hỏi người dùng username hoặc URL Kaggle của Hiếu để xác minh hai nhóm này.

## Bằng chứng

- Phân công 5 arm Hiếu: `worklogs/2026-11-04_b2_flip_kaggle_inference.md`, mục Các notebook validation khác; danh sách và hash trong `Runs-management/kaggle_validation_6arms_20261104/delivery_manifest.json`.
- Phản hồi Hiếu lưu trong `worklogs/evidence_20261104_b3_osf_discussion/02_hieu_tinh_trang_du_lieu_arms.png` chỉ xác nhận nhóm 5 arm sẵn sàng chạy; nó không chứng minh các run đã hoàn tất.
- Output Dũng: `Runs-management/RUNS.md`, các ledger I-03/I-08/I-09/I-10/I-11/I-12/I-13/I-14 và các đường dẫn output tương ứng.
- B1-H2 Kaggle validation: `Runs-management/b1h2_kaggle_validation_audit_20261106.json`; 5.005 ID hợp lệ, runtime 2×T4, kết thúc UTC 2026-11-06T15:04:24.783897. Kernel `duchuynguyen1802/02-kaggle-qwen-q4-b1-h2-validation-20261106-ipynb` hiện báo COMPLETE.
- B1-H2 Kaggle test: `worklogs/2026-11-06_b1h2_kaggle_test_preparation.md` xác nhận chuẩn bị, không phải thực thi GPU.
- B2-rand live status: `duchuynguyen1802/02-kaggle-qwen-q4-b2-rand-ipynb` báo RUNNING. Số 7.789 là mốc I-11 đã kiểm, không phải số đếm trực tiếp của phiên đang chạy.
- Họ B3: `Runs-management/b3_amended_20261106/README.md` ghi rõ implementation/software smoke, không inference bundle được duyệt và không inference GPU.
