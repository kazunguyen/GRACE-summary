# Tiến độ và điều kiện chạy tiếp theo Phương án 2

Đối chiếu local **02/11/2026**. [HIEN_TRANG.md](HIEN_TRANG.md) là bảng sinh từ record; [RUNS.md](RUNS.md) là sổ từng lượt chạy. Có code/notebook không đồng nghĩa đã inference hoặc đã nghiệm thu nghiên cứu.

## 1. Tiến độ các bước

| Bước | Đã có | Còn thiếu / điều kiện chạy tiếp |
|---|---|---|
| 0 — Offline lịch sử | B0_offline ở workspace nguồn đã tái tạo 36 run, P_pre/P_post, repair–harm/oracle/routing; nằm ngoài repo bàn giao này | Có thể tích hợp sớm group-aware OOF/routing CI; expert DeepSeek nhị phân lịch sử không thay thế expert Qwen mới |
| 1 — Backend | Qwen3-Coder-30B-A3B Q4_K_M, model/tokenizer pin, llama-cpp-python0.3.16, có inference thật | B0 có helper khóa; notebook B1/B2 hiện chưa có make_lock/require_test_lock. Watcher chưa xác minh đang chạy |
| 2 — Freeze/raw/CPG/embedding | Freeze donor, cache CodeT5, CPG Joern cuối; B2 tham chiếu mới, bundle flip mới và B2 rerun-66 | Áp dụng donor mới vào inference B2/flip; rep bám đúng phiên B2 cuối. Không encode/parse/retrieve lại chỉ để resume |
| 3 — Prompt/audit | Hậu kiểm 100.110 dòng/40 tập của 6 arm; dry-run mới đủ validation 10 arm/28 tập, 70.070 dòng; 28/28 đạt sau đối chiếu nguồn | B1-H2 và bốn arm B3 blocked vì thiếu đầu vào; chưa đủ 15 arm. Đã có 60 mẫu/hai phiếu trống, chưa có hai người chấm |
| 4 — Đăng ký trước | Analysis lock local có thời điểm sau khi inference bắt đầu, hash/tag lịch sử | Chưa OSF; không gọi preregistration hồi tố. Amendment dùng thời điểm thật, giữ lịch sử tiếp xúc test |
| 5 — Ma trận | B0=10.011; B2=10.011; B1=5.434; flip=5.235; rep/rand chưa có output | B1 còn 4.577; B2 donor mới thêm 66; flip thêm 4.809. Đồng bộ gate/validation/ngưỡng đúng phiên trước test mới; rep gọi model mới |
| 6 — Anchor và giá trị bổ sung | Có supervised_anchor.py/complementarity.py trong kit | Chưa có anchor_scores/summary SUP-LR/MLP/METRIC ba seed cho chiến dịch này; cần adapter cache, expert Qwen ghép ID và cùng folds |
| 7 — Bảng/thống kê | Có stats.py/evaluate_final.py và contrast/biên delta | Sinh metric/CI từ ma trận và anchors mới; bootstrap5.000, báo lần suy biến, Holm, tách nguồn bất định |
| 8 — Review/label audit | Có lịch sử review và make_case_packets.py | Chưa đủ 100 target/dataset, hai người chấm độc lập, phân xử,60 ca SUP-LR/B2 và audit50FN+50FP/dataset |
| 9 — Tái lập | Có code/hash/nhật ký/snapshot | Gói artifact cuối, kiểm máy sạch, README chạy lại và công bố/DOI |

## 2. Các giới hạn cần giữ khi bàn giao

- Khóa local B0/Devign, B0/REVEAL, B2/Devign tạo ~09:57 UTC ngày 01/11, sau khi test tương ứng đã xong. B2/REVEAL có phần test trước khóa ~10:42 UTC. B1/flip đã chạy429/230 test nhưng chưa có bằng chứng khóa trước các mẫu đó. Không backdate hay gọi run cũ xác nhận hồi tố.
- B0 có 1.132 raw response không phải0/1 dù score valid đủ; B1 có3 raw invalid ở REVEAL validation. Báo valid score/raw riêng, không ép invalid thành nhãn0.
- B2-rep mới có notebook prompt, chưa có runner inference riêng/output. Prompt giống B2 phải gọi backend mới; resume checkpoint không phải repeat độc lập.
- B2-rand mới có notebook/bundle. Notebook chạy B2 rerun-66 trước rồi tự chuyển sang rand; folder 07 là bổ sung B2, không phải arm thứ16.

## 3. Điều kiện tích hợp và audit

Kiểm toán gốc 01/11: [JSON điều kiện](KIEM_TOAN_DIEU_KIEN_TANG_1.json), [JSON tích hợp](KIEM_TRA_TICH_HOP_TUNG_ARM.json). Đây là snapshot, không phải tiến độ hôm nay; script audit còn giữ xuất *_CURRENT riêng.

Đã có adapter evidence và audit tự động cho các artifact hiện hữu; dry-run [toàn validation 10 arm](dry_run_validation_20261102/KET_QUA.md) đã qua [kiểm bàn giao](dry_run_validation_20261102/verification.json). B1-H2/B3/B3-nodiff/B3-swap/B3-flip blocked vì thiếu evidence/cặp demo/Key difference; chưa nghiệm thu 15 arm hoặc bằng người. [Kết luận cuối](dry_run_validation_20261102/final_status.json) giữ một cảnh báo nhầm ở bộ dò gốc và bằng chứng giải quyết bằng nguồn frozen riêng. Demo rỗng ≤1% đạt ở mọi tập; 176 cờ demo và 390 cờ thiếu graph vẫn giữ. Hai người cần đọc 30 prompt/dataset và lập biên bản thật. Có module trong kit không chứng minh notebook đã gọi module đó; các hạn chế runtime B2 còn nguyên. Anchor là đối chứng dùng chung, không train lại riêng cho từng arm LLM.

B0/B1 giữ scaffold trống, graph 40/80, native logits và Kaggle là các quyết định contract đã thống nhất, khác một số ví dụ PDF. Ghi đúng variant; không đổi âm thầm rồi gộp kết quả hai phiên.

## 4. Chuyển donor

| Arm | Kết quả tái dùng theo thay đổi donor | GPU tiếp theo |
|---|---|---|
| B0 | Toàn bộ | Không rerun chỉ vì đổi donor |
| B1 | Toàn bộ5.434 record | 4.577 mẫu thiếu; đồng bộ gate và khóa validation trước test mới |
| B2 | REVEAL giữ; Devign giữ prompt không đổi | 28 validation+38 test=66; ghép đủ2.732 validation trước khóa phiên mới |
| B2-flip | 5.202/5.235 record I-06 | Sửa 28 validation+5 test, rồi4.776 mẫu thiếu=4.809 lượt;33 test đổi prompt chưa chạy nằm trong4.776 |
| B2-rep | Chưa có output | Chốt B2 phiên cuối, sinh prompt giống từng ký tự, gọi model độc lập |

Chi tiết/CSV: [donor](NGUY_CO_CHAY_LAI_DO_DONOR.md), [resume flip](B2_FLIP_DONOR_MOI_RESUME.md), [đối chiếu B2](donor_reconciliation_20261101/KET_QUA_DOI_CHIEU.md). Không xóa input donor còn phụ thuộc.

Freeze Devign 21.691 donor, REVEAL 17.636; SHA manifest e1d3c6b17c3a0b5c1e05203794d48a33825e0ea00a55deaaef565af25efe0448. Chuẩn hóa token C/C++ giữ literal; exact dedup loại train trùng eval/nhãn mâu thuẫn; near Jaccard3-gram>=0,9 chỉ gắn cờ. CPG cuối còn 240/50.052 mẫu thiếu AST; eval Devign val/test3/2, REVEAL27/23. Xem [quy ước](QUY_UOC_FRAMEWORK_20261101.md).

## 5. Đến đâu mới thêm cải tiến?

**Làm ngay:** sửa lỗi contract/runtime/gate, donor migration, audit/provenance. Có thể tích hợp sớm group-aware OOF, routing paired CI và evaluator offline của Hiếu nếu không đổi prompt/model/score hoặc dữ liệu inference; lưu cấu hình/folds/seed và đánh dấu phiên phân tích mới.

**Mốc chốt Tầng 1 trước cải tiến phương pháp:** B0/B1/B2/flip/rep đủ hai dataset và hai split cùng phiên contract; repeat gọi độc lập; ngưỡng validation đúng phiên có bằng chứng; audit dữ liệu/prompt được nghiệm thu; đã có bảng metric/CI/net sensitivity làm mốc. Những run lịch sử test trước khóa phải được khai báo và chốt cách diễn giải với thầy, không tự coi xác nhận hồi tố. Thiếu một điều kiện thì mốc chưa đóng.

Đổi retrieval/demo/graph/model/quantization/tokenizer/prompt: tạo branch/variant, input/output/ngưỡng riêng, ghi amendment vào [CHANGES_AFTER_ANALYSIS_LOCK.md](CHANGES_AFTER_ANALYSIS_LOCK.md) và so ghép cặp với baseline đã khóa. Arm ablation có sẵn trong [ma trận](MA_TRAN_RUN.md) không phải cải tiến mới; ưu tiên Tầng 1 trước Tầng 2/3, có thể phân công song song nếu từng arm đủ gate và ghi đúng phiên.

## 6. Hồ sơ đã gộp

Đợt02/11 đã sửa mô tả B2 có helper/watcher đang chạy về đúng bằng chứng; giữ lỗi test tích hợp B2. Các báo cáo kiểm toán Markdown và biên bản đối chiếu được gộp ở đây; hai JSON gốc giữ nguyên. Phương pháp ngưỡng được gộp vào [hướng dẫn khóa](TU_DONG_KHOA_NGUONG.md). Script tạo/niêm phong snapshot một lần và generator Markdown trùng đã bỏ; lịch sử còn trong Git. Helper khóa/refresh, test còn liên quan và script audit/tái tạo donor được giữ.

Các số test xanh trong báo cáo cũ chỉ chứng minh lần kiểm đó. test_validation_lock.py còn một lỗi vì notebook B2 thiếu helper; không xóa test để báo xanh, không suy ra CPU test đã nghiệm thu GPU.

Sau đợt dọn đã chạy lại test trạng thái/ngưỡng và frozen resume: **14 passed, 1 failed**. Lỗi duy nhất là test notebook B2 thiếu helper nêu trên; sáu kiểm thử flip vẫn pass. Hash ngưỡng/snapshot gốc giữ nguyên; không có inference GPU hay khóa mới.
