# Nghiệm thu prompt B3 v4 — 08/11/2026

**Kết luận: prompt Devign đạt kiểm tra kỹ thuật toàn census 2.732/2.732. REVEAL chưa có prompt vì pool vẫn rỗng. Chưa gọi release hai dataset là hoàn tất hoặc sẵn sàng inference GPU.**

## Bằng chứng đã kiểm

- Dựng lại toàn bộ **2.732 prompt B3 Devign** bằng selector và renderer chuẩn từ frozen specs/clean bank; từng prompt khớp nguyên văn bản đã nộp.
- ID set khớp frozen validation/raw/specs; code hash sau strip khớp. Canonical prompt hash, selection/pair hash, pool hash và census hashes khớp.
- Ba seal inputs/pool/prompt hợp lệ; module/script/authority hashes khớp bytes hiện tại. Artifact nguồn không thay trong lúc audit.
- Tokenizer chính xác tại revision đã khóa. Prompt lớn nhất **4.983 token chat**, cộng reserve64 là **5.047 < 8.192**. Kiểm 100% code ≤3.000, graph ≤1.500, mỗi demo ≤1.500; demo và Key difference được giữ đầy đủ; các prompt khớp output renderer Figure6 chuẩn.
- Tất cả prompt Devign ở trạng thái `RENDERED_AUDITED`; không có render/audit failures. Target API chỉ lấy ID/code/nodes/edges, không truyền label hoặc demo hint của target cho selector.
- **2.273 REVEAL** đủ census ID nhưng đều `PAUSED`, prompt/hash/flags null đúng thực tế; không tính các dòng này là prompt đã dựng.

Audit này không gọi LLM, không chạy builders vào release hiện có, không tune threshold và không chạy lại bộ tests không liên quan. Full-census rendering/tokenization là kiểm trực tiếp trên deliverable được yêu cầu, không phải số lượng unit test thay cho audit.

## Review cuối đã được đối chiếu

Trong lượt này chủ dự án xác nhận **hai phiếu độc lập đã ký và niêm phong trên payload cuối**:

`0ced77fefccbcef797c3c01abfa0d139d5611e2d562e8f5ec01089ff05168ee1`

Đã đối chiếu form `Hieu` lúc `2026-11-08T10:05:00Z`, `Dung` lúc `2026-11-08T10:06:00Z`: cùng canonical payload hash, decision approve, bốn xác nhận true. Validator và consensus hiện hành đều chấp nhận; pool payload cũng khớp hash. Nguồn xác nhận review thật là lời xác nhận tường minh của chủ dự án trong hội thoại, không phải suy từ sự hiện diện JSON hay xác minh chữ ký số độc lập.

Điều này cập nhật tình trạng review còn chờ trong audit trước theo đúng trình tự thời gian. Không thay review gốc hoặc ký thay người duyệt.

## Việc còn lại trước đóng gói delivery B3

1. **Thống nhất version metadata:** inputs ghi `v4_verified_patch_admitted`, pool và prompt manifests còn ghi `v3_remediated`/parent v2. Các seal vẫn đúng nhưng tên phiên bản không nhất quán. Sửa ở release kế tiếp, ghi đúng parent/version và seal lại manifests liên quan. Không cần thay prompt bytes đã kiểm chỉ để sửa metadata; cần tính lại hashes/bindings bị ảnh hưởng.
2. **Chốt phạm vi:** Devign đạt kỹ thuật, REVEAL blocked; nếu triển khai Devign trước, phải có quyết định scope riêng và manifest tương ứng. Không tự thay số đầy đủ hai dataset từ5.005 xuống2.732 rồi gọi full study complete.
3. **Nghiệm thu notebook/runtime riêng:** chưa có bằng chứng trong kiểm tra này về delivery source readback, môi trường GPU thực hoặc scoring/resume của B3 mới. Chỉ sau các cổng đó mới inference validation mới; không nhập score/tau lịch sử.

Pool Devign hiện có đúng **một pair**, nên cả2.732 target chọn cùng case08. Điều này không làm prompt sai, nhưng cần công bố phạm vi khoa học: đây chưa là bằng chứng selector thích ứng theo từng target hay retrieval hiệu quả trên pool đa dạng. Không đổi pool dựa trên test metric.

## Trạng thái chuyển bước

| Công việc | Trạng thái |
|---|---|
| Xác nhận hai review trên payload cuối | Đã đối chiếu theo xác nhận chủ dự án + form validator |
| Prompt Devign toàn census | PASS |
| Prompt REVEAL | BLOCKED_EMPTY_POOL |
| Full prompt release hai dataset | Chưa đạt |
| Sửa metadata và chuẩn bị delivery theo scope được duyệt | Có thể làm tiếp |
| Launch B3 GPU | Chưa được nghiệm thu bởi báo cáo này; không thực hiện trong lượt này |

Bằng chứng: [audit toàn prompt](audit.json), [xác nhận review và kết quả validator](review_confirmation.json), [inventory nguồn](source_inventory.json), [mã kiểm lại](audit_prompts.py).
