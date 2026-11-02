"""Verify completed reconciliation exports and write a human-readable report."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'donor_reconciliation_20261101'

def read_rows(path):
    with path.open('rb', buffering=4 * 1024 * 1024) as f:
        return [json.loads(line) for line in f if line.strip()]

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def main():
    summary = json.loads((OUT / 'summary.json').read_text(encoding='utf-8'))
    inventory = json.loads((OUT / 'downloaded_output_inventory.json').read_text(encoding='utf-8'))
    root = HERE.parent
    audited_paths = set()
    for source in inventory['sources']:
        path = root / source['path']
        assert digest(path) == source['sha256'], f'Output changed during audit: {path}'
        manifest = json.loads(path.with_name('run_manifest.json').read_text(encoding='utf-8'))
        assert manifest == source['manifest'], f'Run manifest changed during audit: {path}'
        audited_paths.add(path.resolve())
    current_paths = set()
    for folder in root.glob('[0-9][0-9]_*'):
        for path in folder.rglob('records.jsonl'):
            if any(tag in str(path) for tag in ('offline_test', 'pytest', 'threshold_pipeline_tests')):
                continue
            if path.stat().st_size and any(line.strip() for line in path.open('rb')):
                current_paths.add(path.resolve())
    assert audited_paths <= current_paths, 'A historical source output is missing'
    additional_paths = sorted(str(p.relative_to(root)) for p in current_paths - audited_paths)
    # Verify the historical scope; newly imported records are not silently added to this audit.
    decisions = read_rows(OUT / 'downloaded_record_decisions.jsonl')
    comparison = read_rows(OUT / 'demo_comparison.jsonl')
    assert len(decisions) == summary['unique_downloaded_records']
    assert summary['llm_calls'] == 0
    key = lambda r: (r['arm'], r['dataset'], r['split'], r['seed'], r['id'])
    assert len({key(r) for r in decisions}) == len(decisions), 'Multiple inference identities for a target require manual review'
    expected_counts = {'devign': {'validation': 2732, 'test': 2732},
                       'reveal': {'validation': 2273, 'test': 2274}}
    counts = Counter((r['arm'], r['dataset'], r['split']) for r in decisions)
    for (arm, dataset, split), n in counts.items():
        assert n == expected_counts[dataset][split], (arm, dataset, split, n)
    lookup = {(r['dataset'], r['split'], r['id']): r for r in comparison}
    changed = []
    for r in decisions:
        differs = r['old_prompt_sha256'] != r['new_prompt_sha256']
        assert differs == (r['decision'] == 'rerun_changed_prompt')
        if differs:
            c = lookup[r['dataset'], r['split'], r['id']]
            assert c['prompt_changed']
            changed.append(dict(r, old_demo_id=c['old_demo_id'], new_demo_id=c['new_demo_id'],
                                old_demo_removed_from_new_bank=c['old_demo_removed_from_new_bank'],
                                demo_code_changed=c['demo_code_changed'], demo_label_changed=c['demo_label_changed']))
    for (arm, dataset, split), _ in counts.items():
        expected = {r['id']: r for r in changed if (r['arm'], r['dataset'], r['split']) == (arm, dataset, split)}
        path = OUT / 'rerun_inputs' / arm / dataset / split / 'prompts.jsonl'
        if not expected:
            assert not path.exists(), f'Stale rerun input: {path}'
            continue
        rr = read_rows(path)
        assert len(rr) == len(expected)
        assert len({r['id'] for r in rr}) == len(rr)
        for p in rr:
            assert hashlib.sha256(p['prompt'].encode('utf-8')).hexdigest() == p['prompt_sha256']
            assert p['prompt_sha256'] == expected[p['id']]['new_prompt_sha256']
        manifest = json.loads(path.with_name('manifest.json').read_text(encoding='utf-8'))
        assert manifest['prompts_sha256'] == digest(path)
    csv_path = OUT / 'mau_can_inference_lai_CURRENT.csv'
    if changed:
        with csv_path.open('w', encoding='utf-8-sig', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(changed[0]))
            w.writeheader()
            for row in changed:
                w.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v for k, v in row.items()})
    tables = []
    for arm, dataset, split in sorted(counts):
        total = counts[arm, dataset, split]
        n = sum((r['arm'], r['dataset'], r['split']) == (arm, dataset, split) for r in changed)
        tables.append(f'| {arm} | {dataset} | {split} | {total:,} | {n:,} | {total-n:,} |')
    reasons = Counter('demo_cu_bi_loai' if r['old_demo_removed_from_new_bank'] else 'thu_hang_retrieval_thay_doi' for r in changed)
    bank_lines = []
    for dataset, bank in summary['banks'].items():
        reproduced = bank['reproduction'].get('old_demo_reproduced')
        method = f'tái tạo đúng {reproduced:,}/{reproduced:,} demo cũ' if reproduced is not None else 'kho cũ/mới giống hệt về thứ tự, ID, code, nhãn và AST'
        bank_lines.append(f'- **{dataset}:** {bank["old"]["count"]:,} → {bank["new"]["count"]:,} donor; {method}.')
    id_table = ['| Dataset | Split | ID target | Demo cũ | Demo mới | Lý do |',
                '|---|---|---|---|---|---|']
    for r in sorted(changed, key=lambda x: (x['dataset'], x['split'], x['id'])):
        reason = 'Demo cũ bị loại' if r['old_demo_removed_from_new_bank'] else 'Đổi thứ hạng retrieval'
        id_table.append(f'| {r["dataset"]} | {r["split"]} | `{r["id"]}` | `{r["old_demo_id"]}` | `{r["new_demo_id"]}` | {reason} |')
    md = '\n'.join([
        '# Đối chiếu prompt sau thống nhất donor — 01/11/2026', '',
        '**Phạm vi lịch sử 01/11/2026:** snapshot này chỉ đối chiếu các nguồn trong downloaded_output_inventory.json. '
        f'**{len(changed):,} mẫu cần inference mới nếu chuyển B2 sang kho donor đã thống nhất.** '
        f'{len(decisions)-len(changed):,} kết quả còn tương thích về prompt với thay đổi donor này, nếu giữ nguyên model/tokenizer/backend/tham số/chính sách score.', '',
        '| Arm | Dataset | Split | Output đã kiểm tra | Cần inference mới | Giữ kết quả cũ |',
        '|---|---|---|---:|---:|---:|', *tables, '',
        '## Cách kiểm tra', '', *bank_lines, '',
        '1. Đọc từng `records.jsonl`, đối chiếu `prompt_sha256` và nhãn với đúng prompt gốc. '
        'Gộp bản sao bằng arm/dataset/split/seed/ID/hash prompt/hash model; kiểm tra không có score mâu thuẫn.',
        '2. Tái dùng vector CodeT5 và AST/CPG đã cache; với kho thay đổi, fit lại whitening 256 chiều trên toàn bộ kho mới. '
        'Giữ thuật toán B2: top-50 ngữ nghĩa → top-5 → rerank 0,7 Jaccard code + 0,3 AST. '
        'Tái tạo kho cũ trước để kiểm tra attribution; mọi demo được nhận diện là đổi đều được kiểm tra lại bằng hàm retrieval scalar gốc.',
        '3. Giữ nguyên phần code target, graph 40/80 và câu dẫn; chỉ thay payload demo/nhãn, cắt demo bằng đúng tokenizer Qwen và ngân sách 1.500 token. '
        'So SHA-256 của toàn bộ prompt cuối cùng. Đổi ID donor nhưng prompt cuối giống hệt không tạo thêm lượt inference.', '',
        f'Trong các prompt cần chạy lại: **{reasons["demo_cu_bi_loai"]:,}** dùng demo cũ không còn trong kho mới; '
        f'**{reasons["thu_hang_retrieval_thay_doi"]:,}** đổi lựa chọn retrieval dù demo cũ vẫn còn. '
        'Vì vậy không thể dùng riêng kiểm toán donor bị loại để quyết định danh sách chạy lại.', '',
        '## Danh sách và đầu vào', '',
        '- [Danh sách chính xác các mẫu cần inference lại (CSV)](mau_can_inference_lai_CURRENT.csv): ID target, demo cũ/mới, hash prompt trước/sau và đường dẫn output gốc.',
        '- [Toàn bộ quyết định giữ/chạy lại (CSV)](downloaded_record_decisions.csv).',
        '- [So sánh demo của toàn bộ B2 (CSV)](demo_comparison.csv).',
        '- `rerun_inputs/B2/<dataset>/<split>/prompts.jsonl`: chỉ các prompt đổi, kèm manifest; **đầu vào để kiểm tra, chưa phải bundle Kaggle hoàn chỉnh**.',
        '- `new_reference/B2/<dataset>/<split>/prompts.jsonl`: bộ prompt tham chiếu mới đầy đủ, xuất riêng, chưa thay bộ prompt đang dùng.',
        '- [Tóm tắt máy đọc được](summary.json) và [nguồn output đã đối chiếu](downloaded_output_inventory.json).', '',
        '## Cách dùng kết quả', '',
        'Danh sách này áp dụng khi chuyển sang kho `research_freeze_20261101`; kết quả cũ vẫn mô tả đúng các prompt cũ. '
        'Không cần chạy lại B0 chỉ vì đổi donor. Chưa tìm thấy output inference thật đã tải về của B1, B2-flip, B2-rep hoặc B2-rand trong lần kiểm tra này; '
        'các arm đó không được tính thành lượt chạy lại trong snapshot này. B1 I-07 và B2-flip I-06 đã được xác minh sau đó; xem [hiện trạng](../HIEN_TRANG.md).', '',
        'Nếu validation B2 thay đổi, ghép score mới của các mẫu đổi với score cũ còn tương thích để có **toàn bộ validation phiên mới**, rồi tính/khóa ngưỡng cho phiên đó. '
        'Không chọn ngưỡng chỉ trên phần chạy lại, không dùng test để chọn ngưỡng và không ghi đè ngưỡng lịch sử. '
        'Các score test giữ được có thể chấm lại offline bằng ngưỡng phiên mới.', '',
        'Lần đối chiếu này không gọi LLM, không sửa prompt/output đang dùng, không đổi `thresholds.json` và không sửa snapshot/tag đã niêm phong.', '',
        '## Kiểm tra đầu ra', '',
        'Đã kiểm tra đủ mẫu từng split, không trùng ID quyết định, mọi hash prompt mới khớp nội dung, '
        'và tập `rerun_inputs` trùng chính xác tập quyết định cần inference mới. Hash đầu vào/nguồn retrieval nằm trong các JSON provenance đi kèm.', '',
        '## ID của các mẫu cần inference mới', '', *id_table, '',
    ])
    (OUT / 'KET_QUA_DOI_CHIEU_CURRENT.md').write_text(md, encoding='utf-8')
    verification = {'checked_records': len(decisions), 'rerun_prompts': len(changed),
                    'rerun_inputs_verified': True, 'source_outputs_unchanged': True,
                    'no_new_downloaded_record_files': not additional_paths, 'additional_record_files_outside_historical_scope': additional_paths, 'scripts_sha256': {
                        name: digest(HERE / name) for name in ('reconcile_donor_prompts.py', 'summarize_donor_reconciliation.py')},
                    'exports_sha256': {name: digest(OUT / name) for name in
                        ('summary.json', 'demo_comparison.jsonl', 'downloaded_record_decisions.jsonl',
                         'mau_can_inference_lai_CURRENT.csv', 'KET_QUA_DOI_CHIEU_CURRENT.md')}}
    (OUT / 'verification_CURRENT.json').write_text(json.dumps(verification, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'checked': len(decisions), 'rerun': len(changed), 'reasons': dict(reasons), 'table': tables}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
