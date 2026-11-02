---
id: "prompt-inputs-git-delivery-20261102"
title: "Kiểm tra và bàn giao input dựng prompt qua Git"
author: "Codex (trợ lý AI)"
author_type: "AI assistant"
recorded_at: "2026-11-02T18:41:35.417+07:00"
timezone: "Asia/Bangkok"
status: "completed"
data_commit: "bef5d2ea983c095b2b4e5388ef1ef931da678646"
remote_branch: "origin/baseline-unified"
---

## Yêu cầu

Kiểm contract, raw donor đã chốt, CPG Joern và cache CodeT5 cho Devign/REVEAL validation/test; bổ sung commit/push và README. File trên 100 MiB được skip, giữ local và báo rõ. Mỗi công việc có worklog riêng.

## Đã làm và thay đổi

- Đối chiếu code/notebook để lấy đúng snapshot CPG, sáu embedding cache (có hai train donor), raw/freeze, compact donor bank mới và B2 reference đủ bốn tập.
- Kiểm kích thước từng file trước stage/commit. Danh mục có 78 file đủ điều kiện: hai contract đã có, bổ sung 76 file data/metadata; tổng khoảng 726,35 MiB.
- Thêm .gitattributes để giữ nguyên byte/hash raw/cache trên Windows/Linux. Ghi 16 đường dẫn quá lớn cụ thể vào .gitignore, không xóa file local.
- Cập nhật README, [báo cáo input](../Runs-management/PROMPT_INPUTS_GIT_20261102.md), [inventory size/SHA256](../Runs-management/prompt_input_inventory_20261102.json) và [verifier dùng thư viện Python chuẩn](../Runs-management/verify_prompt_inputs_git.py).

## Kiểm tra

- Sáu cache khớp model CodeT5 pinned, N×768 float32, số dòng hoàn tất, ID/hash code raw frozen và checksum provenance retrieval.
- Raw/manifest frozen, compact donor mới, prompt B2 cũ/mới khớp các checksum có sẵn.
- Kiểm whitespace với cr-at-eol cho snapshot CRLF nguyên bản: pass. Giữ nguyên CRLF để không đổi hash snapshot.
- Sau commit và push, verifier xác nhận 78/78 input khớp byte/SHA256 và blob ở origin/baseline-unified. Kiểm trực tiếp git ls-remote xác nhận commit bef5d2ea983c095b2b4e5388ef1ef931da678646; 16 đường dẫn lớn không có trong tree remote.
- [Kết quả kiểm remote](../Runs-management/prompt_inputs_git_verification_20261102.json). GitHub cảnh báo khuyến nghị 50 MiB với hai vector train và Devign compact bank, nhưng push thành công vì từng file dưới giới hạn 100 MiB.

## File skip và giới hạn bàn giao

16 file lớn gồm sáu CPG train/validation/test, hai donors frozen kèm graph, bốn specs và bốn donor copies của B2 cũ. Kích thước và đường dẫn từng file ở báo cáo input. Bốn ZIP B2 cũ dưới ngưỡng đã có sẵn chứa specs tương ứng, có thể giải nén/kiểm hash; chúng không chứa full graph donor và không phải bundle donor mới.

Clone/pull đủ raw và CodeT5/ref đã nêu, nhưng vẫn thiếu CPG/donor graph nguyên bản để tái dựng mọi bước. Bàn giao các file skip riêng đúng phiên/hash. Không parse Joern, encode CodeT5, inference LLM, tính tau hoặc sửa snapshot trong việc này.
