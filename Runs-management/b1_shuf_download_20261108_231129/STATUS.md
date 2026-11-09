# B1-shuf — kết quả tải về và kiểm checkpoint

Kernel: `huuhieu3333/grace-b1-shuf-resume-20261108`, version2 đã phát hành trong hồ sơ launch. API lúc23:11 ngày08/11/2026 báo COMPLETE, không có failure message. Worker là `timed_out`, cập nhật cuối20:44:41 GMT+7, theo deadline của phiên90 phút; COMPLETE của Kaggle không có nghĩa đã hoàn thành toàn census.

**Đã tải toàn bộ output/checkpoint/log về thư mục này.** Lần tải đầu vướng encoding khi CLI ghi log; tải lại bằng UTF-8 đã hoàn tất, giữ nguyên các output bytes.

| Seed | Devign Test | REVEAL Test | Tổng |
|---|---:|---:|---:|
| 42 | 2.732/2.732 | 2.274/2.274 | 5.006/5.006 |
| 43 | 1.410/2.732 | 0/2.274 | 1.410/5.006 |
| 44 | 0/2.732 | 0/2.274 | 0/5.006 |
| **Tổng** | **4.142/8.196** | **2.274/6.822** | **6.416/15.018 (42,72%)** |

Phiên vừa rồi thêm **665 records**, đều là seed43 Devign, từ745 lên1.410. Còn8.602 records: seed43 Devign1.322, seed43 REVEAL2.274, seed44 Devign2.732 và REVEAL2.274.

## Kiểm toàn vẹn

- ZIP CRC đạt; mọi member checkpoint trùng output đã tải. Worker đúng SHA đã khóa, input manifest/prompt/threshold locks đúng; run identity giữ nguyên qua resume.
- Kiểm toàn bộ6.416 records: ID không trùng/ngoài census, đúng label/prompt/model/runtime identity; score finite trong[0,1] và tính lại từ logprobs khớp.
- Toàn bộ5.751 record cũ giữ nguyên bytes/prefix, không bị ghi đè khi resume.0 legacy imports trong run này.
- Cả2 runtime sessions có provenance/build/native log hashes khớp, package và constructor đúng launch contract, đủ2 T4/49 layers/context/batch. Có2 raw response không binary nhưng numeric score hợp lệ, đã giữ lại.
- Verdict **PASS_LAUNCH_CONTRACT** cho contract6 package `85d8770839f80260cdc7c27b27b6cce6bf8815675c8593db68fb102589c5cbd6`. Không gán lại chứng nhận contract7 package mới dùng cho B3.

Checkpoint mới: `b1_shuf_locked_20261108_checkpoint.zip`.

SHA-256: `f69ddb1bf1f06a96ad04391d032d6f3be95b7fab35bd926ef851cb2028715b19`.

Checkpoint này **đủ toàn vẹn để chuẩn bị resume**, bỏ qua đúng6.416 records đã có. Chưa khởi chạy tiếp trong lượt kiểm tra này. Log có các warning cài dependency nhưng build và inference sau đó đã thành công; trạng thái dừng hiện tại là deadline, không phải assertion/model failure.

[Audit JSON](checkpoint_audit.json), [script kiểm lại](audit_checkpoint.py), [download receipt](download_receipt.json).
