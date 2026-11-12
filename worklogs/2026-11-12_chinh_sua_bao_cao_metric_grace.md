# Chỉnh sửa báo cáo metric GRACE ngày 12/11/2026

Bản chỉnh sửa được tạo từ [báo cáo ngày 07/11, cập nhật ngày 11/11](2026-11-07_bao_cao_metric_cac_arm_hoan_tat.md). Kết quả nằm trong [báo cáo ngày 12/11](2026-11-12_bao_cao_metric_cac_arm_hoan_tat.md). Phạm vi chỉnh sửa là B3/H2.3, RQ4 và B1-H2/RQ3/H3.1 theo bản đối chiếu ngày 12/11.

## Thay đổi

- **B3/H2.3.** Đổi kết luận thành “chưa có kết luận xác nhận”. Chuyển các hàng metric, CI ghép cặp và McNemar/Holm của B3 sang phần thăm dò ở mục 4.5. Giữ các giá trị p đã hiệu chỉnh từ họ 22 phép so của PA1 cho từng bộ ngưỡng.
- **RQ4.** Thay chênh lệch tỷ lệ dự đoán 1 tại ngưỡng riêng (−22,29/+29,73 điểm phần trăm) bằng chênh lệch tại ngưỡng chung 0,5 (−1,10/+17,02 điểm phần trăm, Devign/ReVeal). Mục 4.2 giữ số đếm B2/B3 tương ứng là 1.778/1.748 trên 2.732 mẫu Devign và 1.046/1.433 trên 2.274 mẫu ReVeal. Các cặp khác còn cần bảng tỷ lệ tại ngưỡng chung.
- **B1-H2/RQ3/H3.1.** Dùng B1−B0 và B1−B1-shuf để trả lời RQ3 trong phần chính. Chuyển số gộp toàn test của B1-H2 sang mục 4.5 và ghi rõ phân tầng có và thiếu evidence còn chờ.

## Phạm vi kiểm tra

Các chỉnh sửa dùng số đã có trong báo cáo và các bảng PA1. Bản gốc được lưu nguyên văn. Việc kiểm tra đối chiếu các hàng được chuyển với bản gốc và kiểm tra kết luận H2.3 cùng chênh lệch RQ4 trong bản mới.

## Đính chính về B1-full

**Bỏ đề xuất chạy lại validation chỉ vì lý do renderer.** Audit dựng prompt ghi nhận cách dựng graph dùng cho test đã sửa tái tạo đúng phần graph của **5.005/5.005 prompt validation**, kể cả khung graph rỗng. Theo đối chiếu bổ sung, khối mã nguồn của **5.005/5.005 prompt validation** khớp theo từng ID với B2-rep validation, phù hợp với cách bản test đã sửa lấy khối mã chuẩn từ B2. [Audit B1-full](../Runs-management/locked_continuations_20261108/b1_full_corrected_v4/audit.json) · [Mã dựng prompt](../scripts/build_budget_fixed_b1_full_20261108.py#L87)

Mức thay đổi **4.753/5.006 prompt** là chênh lệch giữa **test cũ và test đã sửa**. Kết quả hiện tại lấy từ lượt chạy đủ **5.006/5.006 mẫu** trên bộ test đã sửa và dùng ngưỡng validation đã khóa. Khi mô tả kết quả, ghi rõ lần sửa áp dụng cho bộ prompt test cũ và lượt test hiện tại dùng bộ đã sửa. [Nhật ký sửa test](2026-11-08_locked_kaggle_continuations.md#L19) · [Nghiệm thu lượt chạy](../Runs-management/run_handoff_20261108/B1_FULL_RUNTIME_ACCEPTANCE.md)

## Đính chính về H1.1, B2-rep, B1-H2 và Step 6

- **H1.1.** Bảng chính đã kết luận đúng theo bộ ngưỡng đăng ký: H1.1 được hỗ trợ một phần. Trên Devign, cận trên CI của ΔMCC(B2−B0) là **0,0681**, vượt biên **0,03**. Kết quả đạt cả biên MCC và AUROC trên cả hai dataset ở §4.4 chỉ áp dụng cho bộ ngưỡng hiệu chỉnh hồi cứu. [Báo cáo ngày 12/11](2026-11-12_bao_cao_metric_cac_arm_hoan_tat.md#3-đối-chiếu-giả-thuyết-đăng-ký-trước-tại-mục-43)
- **B2-rep.** Đối chiếu theo ID cho thấy **5.006/5.006** records có score trùng B2, timestamp khác, `elapsed_s > 0` và `tag=repeat`. Đây là bằng chứng cho một lượt lặp riêng. Hai đầu ra còn thiếu là kết quả kiểm chứng chuẩn từ `compare_records` và hồ sơ provenance runtime đầy đủ. [Records B2-rep](../Runs-management/run_handoff_20261108/completed_results/B2-rep/seed_42)
- **B1-H2 trên ReVeal.** Ngưỡng **0,67** đến từ validation Colab ở lượt I-13. Ngưỡng **0,21** đến từ khóa validation Kaggle và là giá trị dùng trong báo cáo. Phần thăm dò vẫn cần phân tầng theo mẫu có và thiếu evidence. [Sổ chạy I-13](../Runs-management/RUNS.md#L148) · [Khóa validation Kaggle](../Runs-management/b1h2_kaggle_validation_threshold_lock_20261106.json#L422)
- **Step 6.** Các score đã lưu cho SUP-LR và SUP-METRIC giống nhau theo từng ID qua cả ba seed 42, 43, 44, trên validation và test của cả hai dataset. SUP-MLP có biến thiên giữa các seed. Cụm “đủ ba seed” mô tả số seed đã ghi nhận. Với SUP-LR và SUP-METRIC, các score này không cho thấy biến thiên giữa seed. [Scores Devign](../STEP6_supervised_anchors/runs/anchor/locked_step6_20261108/devign/anchor_scores.csv) · [Scores ReVeal](../STEP6_supervised_anchors/runs/anchor/locked_step6_20261108/reveal/anchor_scores.csv)

## Đính chính về khóa SciPy của B2-rand ReVeal

**Hai khóa runtime khác hash vì bản mới bổ sung pin `scipy==1.16.3` và cập nhật metadata của khóa.** Log cài đặt và `pip freeze` của các lượt test seed 42/43 dùng khóa cũ đều xác nhận SciPy đã là **1.16.3**, đúng phiên bản được pin cho lượt chạy phần còn thiếu. Vì vậy, việc thêm pin chỉ cố định phiên bản SciPy đã dùng. Hai phần records không có chênh lệch phiên bản SciPy và không cần chạy lại vì lý do này. [Log seed 42](../Runs-management/kaggle_outputs_20261107/b2_rand_seed42_test_latest/grace_diagnostics/install_dependencies.log) · [Log seed 43](../Runs-management/kaggle_outputs_20261107/b2_rand_seed43_test_latest/grace_diagnostics/install_dependencies.log) · [Khóa mới](../Runs-management/kaggle_outputs_20261107/b2_rand_three_seed_test_tail_latest/inference_runtime_lock.json)

Việc bổ sung pin SciPy không ảnh hưởng đến kết quả qua thay đổi phiên bản. Phân tích độ nhạy với seed 44 cũng cho cùng kết luận về biên lợi ích AUROC trên ReVeal.

## Cập nhật báo cáo về B2-rand ReVeal

- **Mục 1.6.** Ghi rõ hai khóa runtime của seed 42/43, việc khóa mới bổ sung pin SciPy 1.16.3 và các lượt dùng khóa cũ đã chạy đúng phiên bản này. Việc thêm pin giữ nguyên phiên bản SciPy đã dùng. Kết luận AUROC được đối chiếu bằng phân tích độ nhạy ở mục 4.1.
- **Mục 4.1.** Giữ phép so chính với seed 42. Bổ sung phân tích độ nhạy với seed 44 trên đủ 2.274 mẫu ReVeal, cùng một khóa runtime. ΔAUROC(B2−B2-rand) = **−0,0087**, CI 95% **[−0,0304; +0,0142]**. CI được tính riêng bằng 5.000 lượt bootstrap ghép cặp theo 646 cụm file. Cận trên dưới **+0,02**, nên cách đọc theo biên lợi ích AUROC giữ nguyên. [Báo cáo cập nhật](2026-11-12_bao_cao_metric_cac_arm_hoan_tat.md) · [Kết quả seed 44](../06_Arm_B2_Rand/test_results_20261107/seed_44/reveal/test/evaluation.json)

## Đính chính phần Hiếu đã làm (3:30PM 12/11/2026)

Đối chiếu commit `65fa20e` trên `docs/offline-checks-20261112`. Báo cáo ngày 12/11 đã bổ sung `compare_records` cho B2-rep/B2-flip, phân tầng B1-H2, `ppr@0.5`, CI ΔAUPRC, phép so B2−B2-nolabel và bảng đối soát số cũ. Bản đối soát giải thích MCC B2 đổi do ngưỡng, AUROC B2 Devign đổi sau donor rerun và 1.132 phản hồi thô sai định dạng của B0 là tổng bốn split. [Worklog của Hiếu](https://github.com/kazunguyen/GRACE-summary/blob/65fa20efe71e04f45396879eaeb256a5f29d8bac/worklogs/2026-11-12_xu_ly_offline_theo_danh_gia_tien_do.md) · [Báo cáo cập nhật](2026-11-12_bao_cao_metric_cac_arm_hoan_tat.md)

- **B1-full.** Đính chính đề xuất chạy lại validation vì renderer trong worklog của Hiếu và mục D3. Con số **4.753/5.006** là số prompt khác giữa hai bản test. Audit tái tạo đúng phần graph của **5.005/5.005** prompt validation. Lượt test đã sửa đủ **5.006 mẫu** và dùng ngưỡng đã khóa. Bỏ đề xuất chạy lại vì lý do này.
- **B2-rand ReVeal.** Khóa mới bổ sung pin SciPy **1.16.3**, đúng phiên bản các lượt dùng khóa cũ đã chạy. Không cần chạy lại vì SciPy. Phân tích độ nhạy seed 44 vẫn cho cùng kết luận theo biên AUROC +0,02. Phương án chạy lại một nhóm ID trong worklog của Hiếu dành cho phép đối chiếu trực tiếp score trên cùng ID và cùng prompt qua hai runtime.
- **B1-H2 ReVeal.** Đính chính cách gọi 0,67 là “ghi chép lệch”. **0,67** là ngưỡng validation Colab I-13. **0,21** là ngưỡng khóa validation Kaggle dùng trong báo cáo. Đã có kết quả phân tầng test theo evidence ở mức thăm dò.
- **Kiểm tra lại và phần còn mở.** 37 test đều pass. Chạy lại script inventory trên worktree mới dừng ở bước B0 vì thiếu records validation. Đếm trực tiếp từ thư mục chính cho bốn split B0 được 284 + 302 + 261 + 285 = 1.132. Ba script của kit v1.2 đã có. Chuỗi đầy đủ `import_records → thresholds --compare → evaluate_final` và file ngưỡng hiệu chỉnh có hash vẫn còn mở.
