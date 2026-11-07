# I-20 — Chốt B2-rand test seed 42 và 43

Tải bằng `kaggle kernels output quangdung1111/03-kaggle-qwen-q4-b2-rand-three-seed-test-tail-ipy -p <dest>`. Output gốc lưu cục bộ tại `Runs-management/kaggle_outputs_20261107/b2_rand_three_seed_test_tail_latest/`. Worker chạy **20:47:40–22:18:45 GMT+7 ngày 07/11/2026**. Tail xuất đủ 877 record và log xác nhận offload 49/49. SHA-256 checkpoint tail `b94a59afd31162e0e03292b13a4cfceb1b3e8eb36254ca6e3c5960f2fbb2b1ba`.

Ghép 257 record REVEAL của seed 42 vào I-18 và 246 record REVEAL của seed 43 vào I-19. Kiểm CRC checkpoint, byte records tải rời, ID duy nhất, nhãn, prompt SHA, model SHA, runtime, ngưỡng và score hữu hạn. ID mới đúng bằng tập ID còn thiếu. Devign của hai seed giữ đủ 2.732 record từ phiên gốc. Mỗi seed có 2.274 record REVEAL sau ghép. 374 record seed 44 lưu riêng, chờ đối chiếu với phiên chính của seed đó.

| Seed | Dataset | N | τ | MCC | AUROC | AP | F1 | Balanced accuracy |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 42 | Devign | 2.732 | 0,99 | 0,0343 | 0,5318 | 0,4961 | 0,3230 | 0,5144 |
| 42 | REVEAL | 2.274 | 0,89 | 0,0453 | 0,5805 | 0,1227 | 0,1703 | 0,5300 |
| 43 | Devign | 2.732 | 0,99 | 0,0664 | 0,5336 | 0,4980 | 0,3382 | 0,5276 |
| 43 | REVEAL | 2.274 | 0,62 | 0,0596 | 0,5747 | 0,1235 | 0,1910 | 0,5444 |

Tính metric bằng hàm đánh giá của notebook và scikit-learn 1.5.2, với `s >= τ` và τ cố định từ validation. Hai lock ngưỡng có SHA khác nhau nhưng các mục seed 42/43 khớp τ và hash dữ liệu validation nguồn. I-18/I-19 dùng lock runtime `85d87708…` và I-20 dùng `bf1f859d…` có pin SciPy 1.16.3. Các phiên đều ghi SciPy 1.16.3 sau cài đặt. Model hash, tokenizer revision, constructor, backend source và cách tính score đã đối chiếu. Hai kết quả REVEAL vẫn ghép record từ hai phiên có SHA runtime khác nhau.

[Records và metric](../06_Arm_B2_Rand/test_results_20261107/evaluation_summary.json) · [Provenance theo nguồn](../06_Arm_B2_Rand/test_results_20261107/provenance.json)
