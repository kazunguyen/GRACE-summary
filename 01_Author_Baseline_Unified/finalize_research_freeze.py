"""Verify completed freeze, attach graph provenance and write progress report."""
import json
from pathlib import Path
from freeze_research_data import ROOT,OUT,filehash,rows,digest,tokens

manifest=OUT/'freeze_manifest.json'
summary=json.loads(manifest.read_text(encoding='utf-8'))
summary['graph_sources']={}
for d in ('devign','reveal'):
    expected={r['id']:r for r in rows(OUT/d/'train_manifest.jsonl') if r['keep_in_bank']}
    seen=set(); norm=set()
    for r in rows(OUT/d/'donors.jsonl'):
        uid=r['function_uid']; assert uid in expected and uid not in seen; seen.add(uid)
        assert r['target']==expected[uid]['label']
        assert digest(r['func'].encode())==expected[uid]['code_sha256']
        nh=expected[uid]['norm_sha256']; assert nh not in norm; norm.add(nh)
    assert seen==set(expected)
    for s in ('train','validation','test'):
        p=ROOT/f'output/local_full/cpg_recovered_joern_final_20261031/{d}/cpg/{s}.jsonl'
        summary['graph_sources'][f'{d}/{s}']={'path':str(p.relative_to(ROOT)),'sha256':filehash(p)}
    print(d,'verified',len(seen),flush=True)
summary['verification']='Donor IDs equal keep_in_bank set; unique IDs and normalized groups; labels and raw code SHA256 match manifests; graph source SHA256 recorded.'
manifest.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
mh=filehash(manifest)
protocol=ROOT/'diagnostic_kit/configs/protocol.yaml'
text=protocol.read_text(encoding='utf-8').replace('manifest_sha256: "fill: từ build_manifests.py"',f'manifest_sha256: "{mh}"\n  frozen_snapshot: output/research_freeze_20261101/freeze_manifest.json')
with protocol.open('w',encoding='utf-8',newline='\n') as f: f.write(text)
table=[]
for d,st in summary['datasets'].items():
    rem=st['bank_removals']; table.append(f"| {d} | {st['per_split']['train']['n']:,} | {st['donor_count']:,} | {rem.get('overlap_eval_exact',0)} | {rem.get('label_conflict',0)} | {rem.get('duplicate_train',0)} | {st['per_split']['validation']['near_flags']} / {st['per_split']['test']['near_flags']} |")
report='''# Tiến độ các bước theo Phương án 2

Cập nhật 01/11/2026. Nguồn: [đề cương Phương án 2](../../REPORT_TO_TEACHER/20261029/PhuongAn2_De_cuong_nghien_cuu_GRACE_hop_nhat.pdf), Mục 7 (Bước 0–9). Đánh giá dựa trên artifact trong GRACE-summary; không suy ra hoàn thành chỉ vì đã có script. Smoke test GPU không thuộc phạm vi lần cập nhật này. Phần 1/3/4 trong yêu cầu người dùng là các hạng mục kỹ thuật, không đồng nhất với số Bước trong PDF.

| Bước PDF | Tiến độ | Đã có | Phần còn lại / điều kiện nghiệm thu |
|---|---|---|---|
| B0 — Phân tích offline từ dự đoán cũ | Không đánh giá theo yêu cầu | Kho bằng chứng lịch sử được giữ nguyên. | Không làm hoặc xác nhận B0 trong đợt này. |
| B1 — LLM tự host có logprob | Đã chốt framework; chưa nghiệm thu runtime toàn ma trận | Qwen Q4_K_M, llama-cpp-python 0.3.16, model hash, tokenizer revision, hàm raw logits chung và config native; lượt B2 Kaggle đã có kết quả thật. | Notebook/runtime cho từng arm làm sau; smoke test không được tính thiếu trong đánh giá đợt này. |
| B2 — Đóng băng dữ liệu, retrieval, specs | Hoàn tất snapshot dữ liệu/donor; specs toàn ma trận chưa hoàn tất | Raw/manifest/hash ba split, exact dedup, near flags Jaccard chính xác, donor duy nhất đã kiểm tra, hash nguồn CPG sáu split. Chọn full official validation. | Dựng demo B2 từ donor mới; cặp B3, Key difference, H2 evidence và specs mỗi arm thuộc việc tạo prompt tiếp theo. Không dùng bundle cũ như đã tự động đạt snapshot mới. |
| B3 — Renderer, probe, kiểm tra prompt | Hoàn tất sửa framework graph/score; chưa nghiệm thu prompt | Prefix và B1-full trần 40/80; H2 yêu cầu metadata graph nguồn; B2-rep gọi mới; score gốc thống nhất. | Folder/notebook từng arm, kiểm chứng H2 source, dry-run/audit toàn validation và người đọc prompt sẽ làm theo yêu cầu sau. |
| B4 — Đăng ký trước | Chưa hoàn tất | Protocol đã cập nhật model/hash/tokenizer, dữ liệu, graph và scoring. | Chờ prompt/audit để viết preregistration, điền ngày, commit/tag và OSF; không tự gắn trạng thái đã đăng ký. |
| B5 — Chạy ma trận | Chưa hoàn tất | Ma trận 15 arm / 19 arm–seed. Lượt B2 cũ: Devign validation 2.732/2.732; REVEAL validation 1.664/2.273; test chưa chạy theo checkpoint đã nhập. | Dựng prompt theo snapshot mới, validation và ngưỡng từng arm trước test; chưa tái sử dụng số cũ làm xác nhận nếu chưa đối chiếu identity/donor. |
| B6 — Mốc giám sát, P_pre/P_post, routing | Có mã khung; chưa có nghiệm thu lượt mới | supervised_anchor.py, complementarity.py trong kit. | Fit/evaluate ba seed trên snapshot khóa, xuất đặc trưng chung, đối chứng và routing từ expert mới. |
| B7 — Thống kê, bảng và hình | Có mã khung; chưa hoàn tất đầu ra | stats.py, evaluate_final.py và cấu hình contrast/biên delta. | Sinh bảng/hình từ ma trận và anchor mới; kiểm tra ghép ID/CI/hiệu chỉnh đa kiểm định. |
| B8 — Chấm mù, gói ca và kiểm toán nhãn | Chưa xác nhận hoàn thành cho nghiên cứu mới | Có lịch sử chấm mù và make_case_packets.py. | Gói ca, hai người chấm, kappa, kiểm toán nhãn theo giao thức cuối. |
| B9 — Gói tái lập | Hoàn thành một phần | Snapshot hash, script tái tạo/kiểm tra, tài liệu framework, kit và sổ run. | Đóng gói notebook/đầu ra cuối, README và kiểm tra tái lập trên máy sạch. |

## Snapshot dữ liệu đã kiểm tra

Các số loại là số dòng train, gán lý do theo thứ tự overlap eval → nhóm nhãn mâu thuẫn → bản sao cùng nhãn. Cờ gần trùng eval đối chiếu train gốc, bao gồm exact; chỉ gắn cờ, không loại khỏi eval.

| Dataset | Train gốc | Donor giữ | Loại trùng eval | Loại nhãn mâu thuẫn | Loại bản sao cùng nhãn | Eval gần trùng validation / test |
|---|---:|---:|---:|---:|---:|---:|
'''+ '\n'.join(table)+f'''

Manifest tổng: [freeze_manifest.json](../01_Author_Baseline_Unified/output/research_freeze_20261101/freeze_manifest.json). SHA-256: `{mh}`. Thống kê và hash từng file nằm trong manifest; donor IDs khớp chính xác tập keep_in_bank, không lặp ID/nhóm chuẩn hóa; nhãn/hash mã khớp manifest. Nguồn graph được khóa bằng hash tham chiếu, không tạo lại CPG.

Quy tắc và cách dùng: [QUY_UOC_FRAMEWORK_20261101.md](QUY_UOC_FRAMEWORK_20261101.md). Các notebook arm tiếp theo phải dùng snapshot mới và hàm scoring chung. Mô hình/API top-k lịch sử không tự động được coi tương thích.

## Kiểm tra mã

- `python -m pytest diagnostic_kit/tests test_logprobs.py -q`: 39 passed.
- Bộ bổ sung kiểm tra literal, logits ngoài top-5, underflow, graph cap và H2 guard: 4 passed.
- Lượt kiểm tra rộng ban đầu có ba lỗi import `fcntl` ở các script Joern/embedding chạy Linux khi gọi bằng Python Windows; không sửa các script đó trong đợt này. Một assertion B1-full cũ đã được cập nhật vì cùng trần 40/80 có thể tạo graph giống B1 khi không cần cắt. Bộ kit sau sửa đã xanh.
- Chưa chạy GPU/backend smoke test, không tạo prompt/notebook từng arm và không thực hiện đăng ký trước trong đợt này.
'''
(ROOT.parent/'Runs-management/TIEN_DO_PHUONG_AN_2.md').write_text(report,encoding='utf-8')
print('DONE manifest SHA256',mh,flush=True)
