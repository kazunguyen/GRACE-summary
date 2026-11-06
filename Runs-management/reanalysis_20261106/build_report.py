import json,hashlib
from pathlib import Path
out=Path('Runs-management/reanalysis_20261106'); d=json.loads((out/'results.json').read_text(encoding='utf-8'))
lines=['# Tính lại kết quả GRACE từ records ngày 06/11/2026','',
'Phân tích hậu nghiệm theo yêu cầu người dùng. B0/B1/B2/B2-flip đã đủ validation và test trên Devign và ReVeal. Dùng 40.044 records; không chọn ngưỡng từ test và không dùng các giá trị của file ngưỡng preregistration để fit.',
'', 'B0/B1/B2 chọn ngưỡng riêng từ toàn bộ validation bằng grace_diag.stats.pick_threshold, lưới 0,01–0,99 bước 0,01, MCC không xác định bị bỏ qua, hòa thì gần 0,5. B2-flip kế thừa ngưỡng vừa tính lại của B2. Chỉ lọc score valid; raw greedy không phải 0/1 được đếm riêng và không loại score hữu hạn.',
'', 'Đã kiểm tra đủ ID duy nhất, nhãn khớp manifest, score hữu hạn và s khớp sigmoid(logprob_1-logprob_0) với sai số <1e-10 cho từng record. AP dùng sklearn.average_precision_score để xử lý đồng hạng score.',
'', '## Ngưỡng validation','', '| Dataset | Arm | n validation | tau | MCC validation tại tau | Chính sách |','|---|---|---:|---:|---:|---|']
for key,r in d['thresholds'].items():
 ds,a=key.split('|');lines.append(f"| {ds} | {a} | {r['n_validation']} | {r['tau']:.2f} | {r['validation_mcc']:.6f} | {r['policy']} |")
for part in ['full','no_exact_or_near_train']:
 lines+=['',f'## Test {part}','', '| Dataset | Arm | n | tau | AUROC | AP | MCC | BA | Precision | Recall | F1 | Tỷ lệ đoán 1 | TP | FP | TN | FN | Raw invalid |','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
 for r in d['metrics']:
  if r['partition']!=part or r['mode']=='fixed_0.5':continue
  cols=['dataset','arm','n','tau','auroc','auprc_AP','mcc','balanced_accuracy','precision','recall','f1','positive_rate','TP','FP','TN','FN','raw_invalid']
  lines.append('| '+' | '.join('NA' if r.get(k) is None else (f'{r[k]:.4f}' if isinstance(r[k],float) else str(r[k])) for k in cols)+' |')
lines+=['','Tập sensitivity bỏ các mẫu exact_train hoặc near_train theo manifest đóng băng; còn 2.472 Devign và 1.978 ReVeal. Giữ cùng ngưỡng full validation, không fit lại trên test đã lọc. CSV metrics.csv có thêm toàn bộ kết quả tại ngưỡng cố định 0,5. MCC của predictor hằng là không xác định, không ép bằng 0.',
'', '## Chênh lệch ghép cặp trên full test','',
'5.000 lượt paired cluster bootstrap, seed 20261117. Devign: 2.068 commit_id. ReVeal: 646 source_id/file-hash; nối qua raw test ID và kiểm Counter(group,label) khớp canonical_reveal_test.csv lịch sử. Ngưỡng validation giữ cố định trong bootstrap, nên CI chưa bao gồm bất định do chọn ngưỡng. CI 95% dưới đây chưa hiệu chỉnh đa so sánh; không gọi là kết luận xác nhận Holm của toàn bộ họ giả thuyết preregistered.',
'', '| Dataset | So sánh (sau trừ trước) | Metric | Delta | CI95 thấp | CI95 cao | Biên delta | Nhận định theo CI đơn lẻ |','|---|---|---|---:|---:|---:|---:|---|']
for r in d['contrasts']:
 lines.append(f"| {r['dataset']} | {r['b']} - {r['a']} | {r['metric']} | {r['delta']:.4f} | {r['ci95_lo']:.4f} | {r['ci95_hi']:.4f} | {r['margin']:.2f} | {r['verdict']} |")
lines+=['','## Trả lời sáu RQ trong đề cương','',
'RQ1 — Tái lập: B2 không vượt B0 trên point estimate ở cả MCC và AUROC trên cả hai dataset. Cận trên CI đơn lẻ của delta MCC đều <0,03 và delta AUROC đều <0,02, phù hợp H1.1 trong đề cương ở mức phân tích hậu nghiệm này. B2 MCC test 0,0597/0,0645 đều <0,15; F1 Devign 0,5485 thấp hơn ALL-1 0,6295, phù hợp tiêu chí H1.2. Trên ReVeal B2 F1 0,2005 cao hơn ALL-1 0,1837 nhưng vẫn chỉ AUROC 0,5662; không thể dùng F1 riêng để gọi là mạnh. Chỉ một backbone Qwen Q4 được tính lại, không phải tái tính ba backbone hay xác nhận trực tiếp hiệu năng GPT-4 bài gốc.',
'',
'RQ2 — Cơ chế demonstration: thêm demo truy hồi vào B1 không tăng AUROC (delta -0,0030/-0,0179). B2-flip đổi 554/2732 (20,28%) nhãn Devign và 243/2274 (10,69%) nhãn ReVeal tại ngưỡng kế thừa; tại argmax 0,5 là 18,12%/13,90%. Đây là tỷ lệ bất đồng thô, chưa phải net sensitivity do B2-rep chưa có. ReVeal full test đảo nhãn làm giảm AUROC 0,0401 với CI cluster [-0,0648;-0,0155]; Devign CI chứa 0. Tuy nhiên trên tập bỏ trùng/gần trùng, delta AUROC flip-base đảo chiều: Devign +0,0110, ReVeal +0,0134. Do đó không kết luận ảnh hưởng nhãn là bền vững trên mọi partition hoặc chứng minh sao chép nhãn; cần rep, rand, nolabel, labelonly và CI theo partition.',
'',
'RQ3 — Graph: B1-B0 delta AUROC -0,0070 Devign và +0,0101 ReVeal. Devign cận trên CI <0,02; ReVeal cận trên 0,0287 nên vẫn chưa đủ chứng cứ loại lợi ích >=0,02. MCC B1 thấp hơn B0 ở cả hai dataset tại ngưỡng validation. Chưa có shuf/full/H2 nên chưa thể kết luận LLM không đọc graph (toàn bộ H3.1).',
'',
'RQ4 — Khả năng phân biệt hay điểm hoạt động: trong các arm đã chạy, không thấy tăng phân biệt từ B0->B1->B2 nhất quán; ở Devign B1->B2 recall tăng 25,58%->63,35%, tỷ lệ đoán 1 tăng 22,04%->60,18%, nhưng AUROC giảm 0,5335->0,5305 và MCC giảm 0,0788->0,0597. ReVeal B1->B2 recall tăng 30,43%->65,65%, tỷ lệ đoán 1 tăng 23,79%->56,11% nhưng AUROC giảm 0,5841->0,5662. Tăng recall/F1 không tự chứng minh tăng khả năng phân biệt. Chưa có B3 nên H2.3 về cặp tương phản chưa đánh giá. H4.1 AUROC <=0,62 đúng về point estimate cho bốn arm hiện có; chưa khái quát toàn bộ 15 arm.',
'',
'RQ5 — Mốc có giám sát và giá trị bổ sung: bốn arm LLM không đủ trả lời. Chưa tính lại SUP-LR/MLP/METRIC, P-PRE/P-POST hoặc routing của chiến dịch này; không trộn metric lịch sử vào phép so mới. H5.1/H5.2/H5.3 còn thiếu dữ liệu.',
'',
'RQ6 — Truy hồi và lỗi: records điểm số không cung cấp đánh giá liên quan cơ chế hoặc xác minh nhãn thật. Cần nối hai người chấm, audit nhãn và packet sửa/hỏng; chưa kết luận H6.1 từ phân tích này.',
'', '## Tái lập và giới hạn','',
'Chạy từ thư mục repo: `python Runs-management/reanalysis_20261106/recompute.py`. results.json lưu ngưỡng, metric, CI, độ nhạy và đường dẫn/SHA-256 đầu vào. metrics.csv gồm full/clean, ngưỡng validation/0,5, confusion matrix và invalid raw. contrasts.csv và sensitivity.csv lưu số liệu chi tiết.',
'',
'Các file preregistration/config khóa được giữ nguyên. Đây là phiên phân tích mới sau khi đã xem test, không được mô tả là ngưỡng đã khóa trước inference. Việc cập nhật CHANGES_AFTER_PREREG.md/worklog vẫn pending theo yêu cầu trước; báo cáo này không thay thế amendment đó.'
]
proposal=Path('docs/OSF_response/De_cuong_nghien_cuu_GRACE_hop_nhat.docx')
lines+=['',f'SHA-256 đề cương: `{hashlib.sha256(proposal.read_bytes()).hexdigest()}`.']
(out/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(out/'REPORT.md')
