---
id: "step3-20261102-05"
title: "Chạy và kiểm dry-run toàn validation cho mười arm"
author: "Codex (trợ lý AI)"
author_type: "AI assistant"
requested_by: "Người dùng trong chat"
recorded_at: "2026-11-02T18:13:39+07:00"
timezone: "Asia/Bangkok"
work_date: "2026-11-02"
record_type: "retrospective_worklog"
status: "completed"
overall_step3_status: "incomplete"
evidence_verified_at: "2026-11-02T17:52:40.257851+07:00"
---

# Chạy và kiểm dry-run toàn validation cho mười arm

Ghi lại công việc đã thực hiện trước đó. recorded_at là thời điểm lập worklog; evidence_verified_at (nếu có) là mốc kiểm chứng của artifact, không phải thời gian bắt đầu/kết thúc chạy.

## Việc đã làm

- Chạy đủ 2.732 Devign và 2.273 REVEAL validation cho B0, B1, B1-full, B1-shuf, B2, B2-rand, B2-nolabel, B2-labelonly, B2-flip, B2-rep.
- B1-shuf/B2-rand dùng seed 42/43/44; các arm còn lại dùng seed 42: tổng 70.070 dòng prompt/28 tập.
- Theo lựa chọn người dùng, giữ 3 target Devign và 27 REVEAL thiếu graph ở cả ba seed B1-shuf với graph trống/cờ missing.
- Kiểm độc lập ID validation, hash prompt, budget thành phần/context, donor frozen và dung sai kích thước graph.

## Thay đổi đã thực hiện

Xuất prompt, manifest, audit từng dòng, p50/p95 token, tỷ lệ cắt/demo rỗng/graph thiếu, danh sách cờ và checksum tại [dry_run_validation_20261102](../Runs-management/dry_run_validation_20261102/README.md). Ghi lượt P-10 vào RUNS.md.

## Kết quả và bằng chứng

- 0 lỗi dựng. Bộ dò ban đầu: 27 pass, một needs_review; sau [đối chiếu nguồn](2026-11-02_step3_06_doi_chieu_canh_bao_nhan.md), 28/28 tập đạt, không còn cờ nhãn chưa giải quyết trong phạm vi kiểm tra.
- Giữ 176 dòng cờ demo và 390 dòng thiếu graph; danh sách hợp nhất có 562 dòng do bốn dòng có cả hai loại cờ. Demo rỗng cao nhất 24/2.732 = 0,878%, dưới 1%.
- [Báo cáo](../Runs-management/dry_run_validation_20261102/KET_QUA.md), [verification](../Runs-management/dry_run_validation_20261102/verification.json), [final status](../Runs-management/dry_run_validation_20261102/final_status.json), [cờ từng mẫu](../Runs-management/dry_run_validation_20261102/review_flags.csv).

## Phần còn thiếu

B1-H2 và B3/B3-nodiff/B3-swap/B3-flip blocked vì thiếu evidence/cặp demo/Key difference; chưa đủ 15 arm. Không gọi LLM, tạo score hay fit tau. Hash threshold và snapshot niêm phong giữ nguyên.
