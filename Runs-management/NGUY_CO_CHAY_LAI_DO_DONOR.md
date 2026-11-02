# Theo dõi nguy cơ chạy lại khi thống nhất donor

**Hiện trạng sau đối chiếu 02/11/2026:** xem [HIEN_TRANG.md](HIEN_TRANG.md) và [current_status.json](current_status.json). Hai file này bổ sung các snapshot kiểm toán/ngưỡng ngày 01/11; không tạo khóa mới. B2 hiện chưa tích hợp helper vào notebook; watcher chưa được xác minh đang chạy. B2-rand đã có 12 bundle và notebook chạy kèm B2 rerun-66, chưa có output inference.

Ghi nhận ngày 01/11/2026, bổ sung B2-flip ngày 02/11/2026 theo yêu cầu người dùng. **Khi chuyển sang kho donor thống nhất: cần inference mới 66 mẫu B2 Devign đã chạy (28 validation, 38 test) và 33 mẫu B2-flip Devign đã chạy (28 validation, 5 test). Thêm 33 B2-flip test đổi prompt còn chưa chạy, dùng prompt mới cho lượt đầu. Chưa tự inference lại hoặc thay prompt/donor của chiến dịch hiện tại.**

## Bổ sung B2-flip I-06 — 02/11/2026

**Đã triển khai luồng chuyển phiên:** [hai notebook B2-flip](../04_Arm_B2_Flip/README.md) hiện dùng B2 tham chiếu donor mới và resume có chọn lọc; [bundle mới đầy đủ](../04_Arm_B2_Flip/output/bundles_frozen_donor_20261101/grace_b2_flip_frozen_donor_inputs.zip) đã được sinh. Giữ 5.202 kết quả còn khớp, ưu tiên sửa 33 mẫu, rồi chạy 4.776 mẫu thiếu. Ngưỡng/output mới tách riêng; chưa thực hiện inference GPU. [Chi tiết](B2_FLIP_DONOR_MOI_RESUME.md).

Đã tải output `quangdung1111/02-kaggle-qwen-q4-b2-flip-ipynb` vào `04_Arm_B2_Flip/output/kaggle_20261102_quangdung1111_run1/`. Có **5.235/10.011** mẫu đã chạy: Devign validation 2.732, REVEAL validation 2.273, Devign test 230, REVEAL test 0. Dừng do giới hạn thời gian; còn **4.776** mẫu chưa chạy, không tính chúng vào invalid. Raw CM: **TP=913, TN=1.887, FP=1.819, FN=616, invalid response=0, invalid score=0**.

Đã đối chiếu chính bundle prompt tải từ Kaggle với từng record và toàn bộ 10.011 prompt ghép cặp B2. Khi dùng B2 tham chiếu của kho donor mới, B2-flip đổi **66** prompt Devign, trong đó:

| Split | Đã chạy: cần inference lại | Đã chạy: giữ output | Chưa chạy: dùng prompt mới | Tổng prompt đổi |
|---|---:|---:|---:|---:|
| Devign validation | **28** | 2.704 | 0 | 28 |
| Devign test | **5** | 225 | **33** | 38 |
| REVEAL validation | 0 | 2.273 | 0 | 0 |
| REVEAL test | 0 | 0 | 0 | 0 |
| Tổng | **33** | **5.202** | **33** | **66** |

Danh sách [33 mẫu đã chạy cần inference lại](b2_flip_I06_20261102/mau_da_chay_can_inference_lai.csv), [33 mẫu đổi nhưng chưa chạy](b2_flip_I06_20261102/mau_chua_chay_can_doi_prompt.csv), [báo cáo và bằng chứng I-06](b2_flip_I06_20261102/KET_QUA_I06_B2_FLIP.md). Không gọi 33 mẫu chưa chạy là rerun. Khi chuyển phiên, dùng score B2-flip mới cho 28 validation đổi và 2.704 score B2-flip validation còn khớp để khóa ngưỡng mới; không dùng score của B2 thay cho B2-flip.

## Kết quả đối chiếu B0/B2 — 01/11/2026

Đã kiểm tra **20.022 prediction riêng biệt**, gồm B0 và B2, mỗi arm đủ 10.011 mẫu trên bốn dataset/split; các bản sao checkpoint được gộp và kiểm tra không mâu thuẫn. Hash của từng prompt trong output khớp prompt gốc. Đã tái tạo đúng **5.464/5.464 demo B2 Devign cũ** trước khi fit lại whitening bằng kho mới và so prompt mới.

| Arm | Dataset | Validation cần inference mới | Test cần inference mới |
|---|---|---:|---:|
| B0 | Devign | 0 | 0 |
| B0 | REVEAL | 0 | 0 |
| B2 | Devign | **28** | **38** |
| B2 | REVEAL | 0 | 0 |

Trong 66 prompt thay đổi, **21** dùng demo cũ không còn trong kho mới; **45** đổi demo do thứ hạng retrieval thay đổi dù demo cũ còn trong kho. Kho REVEAL cũ/mới giống hệt về thứ tự ID, code, nhãn và AST. Tổng cộng **19.956** prediction còn tương thích với thay đổi donor này khi giữ nguyên inference identity.

Danh sách ID, demo và hash trước/sau: [CSV 66 mẫu](donor_reconciliation_20261101/mau_can_inference_lai.csv); [báo cáo đầy đủ](donor_reconciliation_20261101/KET_QUA_DOI_CHIEU.md). Prompt mới được xuất riêng trong `donor_reconciliation_20261101/rerun_inputs/`; không ghi đè bundle đang dùng. Các arm khác chưa có output inference thật đã tải về tại thời điểm kiểm tra, nên chưa có kết quả cũ để tính là cần chạy lại.

Validation Devign thay đổi: sau khi có score mới cho 28 mẫu, phải ghép với 2.704 score validation còn giữ được để tính/khóa ngưỡng cho **phiên B2 Devign mới**. Không chọn ngưỡng trên riêng 28 mẫu và không ghi đè ngưỡng lịch sử.

**Đóng gói ngày 02/11/2026:** đã tạo [07_Arm_B2_Donor_Rerun_66](../07_Arm_B2_Donor_Rerun_66/README.md), có ZIP upload Kaggle chứa đúng 66 prompt, manifest/hash, audit và 2.704 score validation tái sử dụng để notebook riêng có thể ghép đủ validation trước test. Đây là chuẩn bị đầu vào, chưa inference lại. ZIP: `07_Arm_B2_Donor_Rerun_66/output/grace_b2_devign_donor_rerun_66_20261102.zip`.

## Trạng thái cần phân biệt

- Bộ B2 tham chiếu hiện tại vẫn dùng cache đã sinh trước đó; các arm ghép cặp bám đúng B2 này. Không ghi đè các kết quả đã chạy.
- Kho donor mới nằm trong `01_Author_Baseline_Unified/output/research_freeze_20261101/`. Protocol template đang trỏ kho này, nhưng sự tồn tại của kho mới không tự thay demo trong prompt B2 cũ.
- Devign: kho B2 cũ 21.750 donor, kho mới 21.691 donor. Kiểm toán đã ghi nhận **5 prompt validation và 16 prompt test** của B2 dùng demo không thuộc kho mới; đây là số prompt, không phải số donor duy nhất hoặc số lượt chắc chắn phải chạy lại.
- **Không giới hạn phạm vi ảnh hưởng vào 21 prompt đó:** đổi kho có thể đổi phép fit whitening/thứ tự retrieval và lựa chọn demo của những target khác. Phải đối chiếu toàn bộ prompt sau khi tạo bộ tham chiếu mới.

## Tầng 1: arm nào có nguy cơ?

| Arm / folder | Phụ thuộc donor? | Ghi chú quản lý chạy lại |
|---|---|---|
| B0 / 02_Arm_B0_Source_Only | Không | Không cần inference lại chỉ vì đổi donor nếu code target, scaffold, tokenizer/model và các tham số thực thi giữ nguyên. |
| B1 / 03_Arm_B1_Graph_Only | Không trực tiếp | Không cần inference lại chỉ vì đổi donor nếu code/CPG target và prompt giữ nguyên. Demo B2 tham chiếu được dùng để đối chiếu cache không phải demo xuất hiện trong prompt B1. |
| **B2 / 01_Author_Baseline_Unified** | **Có: demo truy hồi và kho fit retrieval** | **Đã so toàn bộ: 66 prompt Devign đổi (28 validation, 38 test); 0 prompt REVEAL đổi.** Chỉ 66 prompt cần inference mới khi chuyển kho; giữ inference identity. Kết quả lịch sử vẫn có giá trị cho đúng prompt/kho đã dùng. |
| **B2-flip / 04_Arm_B2_Flip** | **Có: dùng demo của B2, đảo nhãn** | **Đã so I-06: 33 mẫu đã chạy cần inference lại (28 validation + 5 test Devign); 33 Devign test đổi prompt còn chưa chạy.** Tổng 66 prompt thay đổi; REVEAL 0. Phải bám B2 mới và đảo nhãn demo mới, không dùng prompt B2 thuần để chạy flip. |
| **B2-rep / 05_Arm_B2_Rep** | **Có: phải lặp đúng prompt B2** | **Kế thừa nguy cơ từ B2.** Nếu B2 mới đổi prompt, rep phải dùng prompt B2 mới. Rep luôn là một lần gọi LLM độc lập; không chép response B2 sang rep. Kết quả rep cũ chỉ có thể giữ nếu prompt/identity phù hợp và đó thực sự là lượt gọi độc lập. |

## Các arm Tầng 2/3 cần ghi nhớ trước khi chạy

| Nhóm arm | Nguy cơ khi kho donor đổi |
|---|---|
| B2-rand | Có: tập donor/lựa chọn ngẫu nhiên có thể đổi; giữ seed không bảo đảm cùng demo. |
| B2-nolabel, B2-labelonly | Có: phụ thuộc demo B2. Nếu prompt cuối cùng không đổi thì không tự phát sinh yêu cầu inference lại; đặc biệt labelonly có thể vẫn cho cùng câu gợi ý nhãn. |
| B1-shuf | Có: graph lấy từ donor có thể đổi dù code target giữ nguyên. |
| B3, B3-nodiff, B3-swap, B3-flip | Có: cặp demo và/hoặc mô tả khác biệt có thể đổi. Các biến thể phải dùng cùng cặp B3 của cùng phiên tham chiếu. |
| B1-full, B1-H2 | Không trực tiếp nếu chỉ dùng code/CPG/evidence của chính target và cách đóng gói giữ nguyên. Thay đổi nguồn graph/evidence là lý do khác, phải kiểm riêng. |

Các arm chưa inference không có run cũ để “chạy lại”; ghi chú này yêu cầu chốt donor/phiên tham chiếu trước khi sinh/chạy bộ prompt xác nhận. Các mốc SUP huấn luyện theo dữ liệu/đặc trưng riêng cần xem lại identity train nếu dữ liệu huấn luyện thay đổi, nhưng không phải lượt inference LLM của các arm trên.

## Quy tắc quyết định, tránh chạy lại không cần thiết

1. Giữ nguyên artifact hiện tại cùng manifest/hash; tạo phiên prompt tham chiếu mới riêng nếu quyết định áp dụng kho mới. Không sửa ngầm demo bên trong bộ đang dùng.
2. Tái sử dụng cache Joern/CodeT5 còn khớp ID/hash code; không mặc định parse/encode lại. Khi kho fit retrieval thay đổi phải tái tạo retrieval tương ứng, không tái sử dụng whitening cũ mà gọi là đã fit trên kho mới.
3. So **prompt_sha256 và inference identity** trên toàn bộ từng arm/dataset/split. Identity gồm model/checkpoint, tokenizer, backend/tham số và chính sách lấy score. Demo ID thay đổi nhưng prompt thực gửi không đổi thì phải đánh giá theo prompt/identity thực tế, đồng thời giữ provenance đúng.
4. Prompt và identity giữ nguyên: có thể tái sử dụng kết quả phù hợp, với ngoại lệ yêu cầu gọi độc lập của B2-rep. Prompt hoặc identity đổi: ghi danh sách target bị ảnh hưởng, đánh giá số lượt cần inference mới; chưa mặc định toàn arm phải chạy lại.
5. Nếu validation của một arm đổi, tính/khóa ngưỡng cho **phiên mới** từ validation mới. Không ghi đè ngưỡng cũ hoặc chọn bằng test. Score test còn tương thích có thể được chấm lại offline theo ngưỡng mới, không tự cần thêm GPU chỉ vì ngưỡng đổi.
6. Mọi quyết định chạy lại phải ghi rõ phiên donor, phiên B2/B3 tham chiếu, hash trước/sau, số target ảnh hưởng và cách xử lý cache. Giữ kết quả lịch sử/thăm dò tách khỏi phiên xác nhận mới.

**Trạng thái hiện tại: ĐÃ SO B0/B2 VÀ B2-FLIP I-06; 66 B2 + 33 B2-FLIP ĐÃ CHẠY CẦN INFERENCE MỚI NẾU CHUYỂN DONOR.** Thêm 33 B2-flip test đổi prompt còn chưa chạy. Chưa tự gọi lại LLM, chưa thay prompt/output/khóa ngưỡng đang dùng; không tự mở rộng danh sách sang B2-rep hoặc arm chưa có output.

Liên kết quản lý: [ma trận arm](MA_TRAN_RUN.md), [sổ run thực tế](RUNS.md), [tiến độ đề cương](TIEN_DO_PHUONG_AN_2.md). Các bản snapshot/commit/tag trong analysis_lock_20261101 được giữ nguyên; ghi chú này bổ sung theo dõi rủi ro, không sửa lịch sử giao thức đã niêm phong.
