# Nhật ký sau analysis-lock-20261101-v1

## 02/11/2026 — Dry-run toàn validation cho các arm đủ đầu vào

Theo lựa chọn người dùng: chạy đủ 2.732 Devign + 2.273 REVEAL, giữ 5 arm thiếu H2/B3 blocked; B1-shuf giữ 3/27 target thiếu graph bằng graph trống/cờ missing ở mọi seed. Đã dựng 70.070 dòng/28 tập cho 10 arm, sau đối chiếu nguồn 28/28 đạt; kiểm độc lập ID/hash/budget/donor và phiếu chấm. Giữ nguyên bộ dò gốc (27 pass, 1 needs_review) cùng bằng chứng cảnh báo nhầm: node donor hiển thị cắt 40 ký tự, chuỗi Label là trường giao thức. 176 cờ demo/390 cờ graph thiếu được giữ, tỷ lệ demo rỗng mỗi tập ≤1%.

Thêm driver CPU dùng renderer chung, adapter scaffold và graph prefix cache đã kiểm, lazy donor graph index/process workers; lưu lượt thread dở riêng. Test probe 20 pass, test driver 4 pass. Chuẩn bị 60 mẫu và hai phiếu trống; chưa có hai người chấm, chưa hoàn thành Bước 3. Không inference, sinh score hoặc fit tau; hash threshold/snapshot niêm phong giữ nguyên, không sửa lịch sử test hoặc OSF. [Hồ sơ](dry_run_validation_20261102/README.md), [báo cáo](dry_run_validation_20261102/KET_QUA.md), [nguồn](dry_run_validation_20261102/source_hashes.json).

## 02/11/2026 — Audit hậu kiểm prompt/output và chuẩn bị hồ sơ chấm

Đã hoàn thành thực thi audit CPU 100.110 prompt/40 tập của 6 arm và đối chiếu 30.691 output; 106 nguồn hash khớp, 30.691 score tính lại từ logprob khớp, 0 score lỗi. Giữ cờ regex gốc và ghi riêng phân loại cú pháp C/C++; có 403 dòng demo dưới 25% (68 dòng đã inference: B2 46, B2-flip 22) cần xử lý, chưa sửa prompt hoặc inference lại. Báo riêng 1.135 raw response không hợp lệ (B0 1.132, B1 3). Theo quyết định người dùng: giữ tiêu chí 25%, ghi 9 arm thiếu là chưa chuẩn bị và tạo bộ 60 prompt/hai phiếu chấm trống. Chưa có hai người đánh giá hoặc nghiệm thu toàn nghiên cứu; không đổi donor/output/ngưỡng/snapshot/tag, lịch sử test trước khóa hoặc OSF. [Kết luận](prompt_audit_20261102/KET_QUA.md), [hồ sơ chấm](prompt_audit_20261102/README.md).


## 02/11/2026 — Dọn Runs-management và bổ sung flow bàn giao

Theo lựa chọn người dùng: gộp kiểm toán/biên bản đối chiếu vào TIEN_DO_PHUONG_AN_2.md; gộp giải thích ngưỡng vào TU_DONG_KHOA_NGUONG.md. Bỏ bốn Markdown trùng (KIEM_TOAN_DIEU_KIEN_TANG_1.md, KIEM_TRA_TICH_HOP_TUNG_ARM.md, DOI_CHIEU_CODE_20261102.md, KET_QUA_CHOT_NGUONG.md), năm script một lần (create_analysis_record.py, seal_analysis_record.py, install_threshold_pipeline.py, write_tier1_audit_report.py, write_threshold_explanation.py), test giả/cache Python/pytest và log watcher tạm. Bỏ test dành riêng cho hai generator đã nghỉ; giữ test coverage/identity/ngưỡng và lỗi tích hợp B2 đã biết.

Giữ nguyên helper đang import, thresholds, snapshot niêm phong/JSON kiểm toán gốc, bằng chứng I-06/I-07, donor new_reference/cache và các input còn phụ thuộc. Sửa liên kết sau khi gộp; thêm README gốc và mục lục quản lý, flow cấu hình từng arm, nơi lưu dữ liệu/checkpoint, protocol ghi run J/E/P/I, bảng đã chạy/việc tiếp theo và gói bàn giao ngoài Git.

Kiểm lại tiến độ từ artifact: B0/B2=10.011/arm, B1=5.434, flip=5.235; chưa có rep/rand hoặc GPU migration mới. Không tạo I-08. Group-aware/CI offline có thể tích hợp sớm nếu không đổi inference; cải tiến phương pháp chờ mốc Tầng1 được nghiệm thu, lưu phiên riêng. Chưa sửa runtime, tính khóa mới hoặc gọi LLM.

## 02/11/2026 — Đồng bộ tài liệu với code theo quyết định người dùng

Thêm current_status.json/HIEN_TRANG.md từ các output đã nhập; giữ nguyên snapshot JSON lịch sử và thresholds.json, chưa tính khóa mới. Sửa mô tả B2 chưa nhúng helper, watcher chưa xác minh đang chạy, bổ sung 12 bundle B2-rand và notebook chạy kèm B2 rerun-66; sửa liên kết script đã dọn. Generator giữ bảng hiện tại bên trên nội dung kiểm toán lịch sử; audit mới xuất *_CURRENT.json, không ghi đè snapshot. Reconciliation từ chối ghi đè export lịch sử; summarizer kiểm theo inventory lịch sử và xuất *_CURRENT. Không sửa runtime các arm. Commit chỉ Runs-management với code/tài liệu/bằng chứng nhỏ; cache và bản sao prompt giữ local. Xem [biên bản đối chiếu](TIEN_DO_PHUONG_AN_2.md).

**02/11/2026 — bổ sung bằng chứng B1 I-07:** xác minh 5.434 record đã chạy từ 01–02/11; cập nhật sổ run, ma trận và tiến độ. Hai validation đủ score, Devign test 429, REVEAL test 0; 0 invalid score, 3 invalid raw response. Đây là sửa thông tin quản lý, không chạy inference mới, không thay khóa ngưỡng hoặc bản ghi phân tích đã niêm phong. [Bằng chứng](b1_I07_20261102.json).

## 02/11/2026 — Nhập checkpoint B2-flip I-06

Đã tải output `quangdung1111/02-kaggle-qwen-q4-b2-flip-ipynb` về `04_Arm_B2_Flip/output/kaggle_20261102_quangdung1111_run1/`. I-06 chạy từ 01/11 21:46:02 đến 02/11 07:15:49 Asia/Bangkok, dừng do thời gian, đạt **5.235/10.011 (52,29%)**; còn **4.776** mẫu chưa chạy. Raw CM: **TP=913, TN=1.887, FP=1.819, FN=616; invalid response=0, invalid score=0**. Hai validation đã đủ; Devign test 230, REVEAL test 0. [Báo cáo và bằng chứng](b2_flip_I06_20261102/KET_QUA_I06_B2_FLIP.md). Output không kèm bằng chứng khóa ngưỡng trước 230 test; lịch sử này được giữ nguyên.

## 02/11/2026 — Đối chiếu donor và chuẩn bị B2-flip phiên mới

Đối chiếu đủ 10.011 prompt bằng đúng bundle đã dùng trên Kaggle và B2 tham chiếu của kho donor thống nhất: Devign đổi **28 validation + 38 test**; REVEAL không đổi. Trong phần I-06 đã chạy, **33 mẫu cần inference lại (28 validation + 5 test)**, giữ được **5.202** record; **33 test đổi prompt còn chưa chạy** dùng input mới cho lượt đầu. CSV ID/hash nằm trong [báo cáo I-06](b2_flip_I06_20261102/KET_QUA_I06_B2_FLIP.md).

Đã sửa hai notebook B2-flip và sinh [bundle mới đủ 10.011 prompt](../04_Arm_B2_Flip/output/bundles_frozen_donor_20261101/grace_b2_flip_frozen_donor_inputs.zip). Runtime mới giữ checkpoint gốc, sửa 28 validation, ghép đủ 2.732 để khóa ngưỡng mới, sửa 5 test rồi tiếp tục 4.776 mẫu thiếu; tổng **4.809 lượt LLM bổ sung**. Ngưỡng/output phiên mới tách riêng; có hàng đợi ưu tiên và resume theo hash. [Hướng dẫn và kiểm thử CPU](B2_FLIP_DONOR_MOI_RESUME.md).

Các mục trên ghi nhận việc đã nhập I-06 và đã chuẩn bị code/input; **chưa có inference GPU phiên donor mới, chưa phát sinh lượt GPU B2-flip phiên donor mới hoặc khóa ngưỡng mới từ score sửa**. Không đổi quy tắc chọn ngưỡng, output/khóa lịch sử, snapshot trong `analysis_lock_20261101` hoặc tag đã niêm phong; không gắn trạng thái đăng ký trước hồi tố. Các mục 01/11 bên dưới giữ lịch sử tại thời điểm ghi nhận.

## 01/11/2026 — Ghi chú nguy cơ chạy lại do thống nhất donor

Theo yêu cầu người dùng, thêm NGUY_CO_CHAY_LAI_DO_DONOR.md, cột nguy cơ cho 15 arm trong MA_TRAN_RUN.md và liên kết/ghi chú ở các file quản lý tiến độ, kiểm toán, ngưỡng. B2/flip/rep là nhóm nguy cơ trực tiếp ở Tầng 1; các arm dùng demo/graph donor ở tầng sau cũng được đánh dấu. Đây là thay đổi tài liệu theo dõi; chưa quyết định hoặc chạy lại inference, chưa đổi prompt/donor, khóa ngưỡng hoặc snapshot/tag đã niêm phong. Hai script sinh báo cáo được bổ sung ghi chú để lần tái sinh tài liệu sau không làm mất cảnh báo này.

## 01/11/2026 — Hoàn thiện vận hành helper và kiểm tra notebook

Sau tag local lúc 17:03:42 Asia/Bangkok, bổ sung watcher local (không đọc test), tài liệu vận hành và kiểm tra source hai notebook Kaggle đã nhúng đúng helper/kiểm tra ngưỡng. Test core tăng từ 4 lên 5, cộng 8 test B0. Không thay grid, objective, tie-break, điều kiện đủ validation, ba khóa ban đầu hoặc model/prompt inventory đã niêm phong. Watcher chỉ thêm khóa cho arm/dataset mới khi đủ kết quả tương ứng; khóa cũ vẫn bất biến.

Không sửa các file snapshot trong analysis_lock_20261101 hoặc viết lại tag. OSF vẫn chưa công bố; không đổi trạng thái thành preregistered. Bản checkpoint Git giữ nguyên source test tại thời điểm niêm phong; test bổ sung hiện ở working tree là kiểm tra vận hành sau đó.

## 01/11/2026 — Nhập hoàn tất inference B2 I-05

Đã nhập và hợp nhất output Kaggle I-05 với I-02/I-04: B2 đạt 10.011/10.011 prediction, 0 invalid, không có conflict; xem [I-05 và merge manifest](RUNS.md) cùng artifact canonical trong `01_Author_Baseline_Unified/output/local_full/inference_qwen_q4_b2_20261101/`. Watcher đã khóa B2/ReVeal tau=0,12 từ đủ validation (MCC=0,082299); ba khóa ban đầu và quy tắc chọn ngưỡng không đổi. Test REVEAL đã được chạy một phần trong I-04 trước thời điểm khóa B2/ReVeal; phần còn lại chạy trong I-05 sau khóa. Vì vậy không gắn nhãn toàn bộ run là tuân thủ thứ tự validation→khóa→test. Đây là cập nhật trạng thái đầu ra và lịch sử tiếp xúc test; không thay đổi protocol/template đã niêm phong, không sửa tag hoặc gói OSF.

## 02/11/2026 — Tiếp tục B2-rand I-09 theo yêu cầu người dùng

Chỉnh notebook sang resume bắt buộc từ I-09 hoặc checkpoint hậu duệ, kiểm hash 12 tập prompt đã audit và prefix record/khóa I-09; giữ nguyên B2 donor đã xong. Chỉ chạy validation còn thiếu, dừng và đóng gói; không fit ngưỡng hoặc chạy test, để người dùng chốt ngưỡng sau. Không thay prompt, model, seed, score, output, khóa hay snapshot lịch sử. Đã thử ZIP/thư mục checkpoint thật và mô phỏng lịch chạy trong thư mục tạm; chưa chạy GPU lượt mới.
