"""Audit downloaded I-06 B2-flip: raw confusion counts and donor prompt changes.

No LLM calls, retrieval fitting, threshold selection or modification of input runs.
"""
import csv
import hashlib
import json
import math
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent.parent
ARM = ROOT / '04_Arm_B2_Flip'
DOWNLOAD = ARM / 'output/kaggle_20261102_quangdung1111_run1'
RUN = DOWNLOAD / 'grace_b2_flip_four_split_9h35'
PRIOR = ROOT / 'Runs-management/donor_reconciliation_20261101'
BASE = ROOT / '01_Author_Baseline_Unified'
OLD_B2 = BASE / 'output/local_full/bundles_recovered_joern_final_20261031'
# Keep the imported I-06 audit immutable; fresh verification has a new destination.
OUT = ROOT / 'Runs-management/b2_flip_I06_20261102_CURRENT'
KERNEL = 'quangdung1111/02-kaggle-qwen-q4-b2-flip-ipynb'
MODEL = 'f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335'
HEAD = re.compile(r'\n\nThe following is an example, and it is (Vulnerable|Non-vulnerable)\.\n')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def parse(data):
    return [json.loads(line) for line in data.splitlines() if line.strip()]


def rows(path):
    with path.open('rb', buffering=4 * 1024 * 1024) as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def export(name, rr):
    with (OUT / f'{name}.jsonl').open('w', encoding='utf-8', newline='\n') as f:
        for r in rr:
            f.write(json.dumps(r, ensure_ascii=False, allow_nan=False) + '\n')
    if rr:
        with (OUT / f'{name}.csv').open('w', encoding='utf-8-sig', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(rr[0]))
            w.writeheader()
            for r in rr:
                w.writerow(r)


def flip(prompt, expected_true_label=None):
    matches = list(HEAD.finditer(prompt))
    assert len(matches) == 1, 'Ambiguous demonstration heading'
    match = matches[0]
    assert prompt.endswith('\n\nAnswer (0 or 1):')
    label = int(match.group(1) == 'Vulnerable')
    if expected_true_label is not None:
        assert label == expected_true_label, 'Demo bank label disagrees with B2 text'
    swapped = 'Non-vulnerable' if label else 'Vulnerable'
    return prompt[:match.start(1)] + swapped + prompt[match.end(1):]


def metrics(rr):
    cm = Counter(TP=0, TN=0, FP=0, FN=0)
    invalid_response = invalid_score = disagreements = 0
    for r in rr:
        raw = str(r.get('raw', '')).strip()
        response_ok = bool(r.get('response_valid')) and raw in ('0', '1')
        score = r.get('s')
        score_ok = bool(r.get('valid')) and isinstance(score, (int, float)) and math.isfinite(score) and 0 <= score <= 1
        invalid_response += not response_ok
        invalid_score += not score_ok
        if response_ok:
            pred = int(raw)
            cm['TP' if r['label'] == 1 and pred == 1 else 'TN' if r['label'] == 0 and pred == 0 else 'FP' if pred == 1 else 'FN'] += 1
            if score_ok:
                disagreements += pred != int(score >= .5)
    assert sum(cm.values()) + invalid_response == len(rr)
    return dict(count=len(rr), **cm, invalid_response=invalid_response, invalid_score=invalid_score,
                raw_vs_score_05_disagreements=disagreements)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    status = read(RUN / 'checkpoint_status.json')
    archive = DOWNLOAD / 'grace_b2_flip_checkpoint.zip'
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        checked_checkpoint = 0
        for name in z.namelist():
            if name.endswith('/'):
                continue
            assert z.read(name) == (RUN / name).read_bytes(), f'Checkpoint and separate output disagree: {name}'
            checked_checkpoint += 1
    provenance = {}
    for dataset in ('devign', 'reveal'):
        proof = read(PRIOR / f'{dataset}_retrieval_provenance.json')
        bank = PRIOR / f'cache/{dataset}_new_bank.jsonl'
        assert file_sha(bank) == proof['new']['cache_sha256']
        provenance[dataset] = {'proof': proof, 'labels': {r['id']: r['target'] for r in rows(bank)}}
    b2_changes = {(r['dataset'], r['split'], r['id']): r for r in rows(PRIOR / 'demo_comparison.jsonl')}
    downloaded = []
    comparison = []
    split_results = []
    changed_review = []
    bundle_proofs = []
    runtime_identities = []
    for dataset, split in [('devign', 'validation'), ('reveal', 'validation'), ('devign', 'test'), ('reveal', 'test')]:
        bundle = DOWNLOAD / f'grace_b2_flip_bundles/{dataset}_{split}_b2_flip.zip'
        with zipfile.ZipFile(bundle) as z:
            assert z.testzip() is None
            bm = json.loads(z.read('bundle_manifest.json'))
            data = z.read('prompts.jsonl')
            assert sha(data) == bm['prompts_sha256']
            original = parse(data)
        old_by_id = {r['id']: r for r in original}
        assert len(old_by_id) == len(original) == bm['count']
        local = ARM / f'output/bundles/{dataset}/{split}/prompts.jsonl'
        bundle_proofs.append({'dataset': dataset, 'split': split, 'bundle_sha256': file_sha(bundle),
                              'prompts_sha256': bm['prompts_sha256'], 'count': len(original),
                              'local_current_prompt_file_matches': local.exists() and file_sha(local) == bm['prompts_sha256']})
        record_path = RUN / dataset / split / 'records.jsonl'
        rr = list(rows(record_path)) if record_path.exists() else []
        seen = {r['id']: r for r in rr}
        assert len(rr) == len(seen)
        assert len(rr) == status['runs'][f'{dataset}/{split}'].get('completed', 0)
        if rr:
            runtime = read(record_path.with_name('run_manifest.json'))
            assert runtime['bundle_sha256'] == file_sha(bundle)
            assert runtime['prompt_set_sha256'] == bm['prompts_sha256']
            assert runtime['model_sha256'] == MODEL
            runtime_identities.append({k: runtime[k] for k in ('model_sha256', 'tokenizer', 'tokenizer_revision',
                'quantization', 'llama_cpp_python', 'scoring', 'gpu_layers', 'context_tokens')})
        for r in rr:
            old = old_by_id[r['id']]
            assert (r['arm'], r['dataset'], r['split'], r['label'], r['prompt_sha256'], r['demo_ids']) == (
                'B2-flip', dataset, split, old['label'], old['prompt_sha256'], old['demo_ids'])
            assert r['model_sha256'] == MODEL and r['seed'] == 42
        original_b2_dir = OLD_B2 / dataset / split
        b2m = read(original_b2_dir / 'bundle_manifest.json')
        assert file_sha(original_b2_dir / 'prompts.jsonl') == b2m['prompts_sha256']
        assert bm['reference_b2_sha256']['prompts'] == b2m['prompts_sha256']
        old_b2 = {r['id']: r for r in rows(original_b2_dir / 'prompts.jsonl')}
        new_path = PRIOR / f'new_reference/B2/{dataset}/{split}/prompts.jsonl'
        nm = read(new_path.with_name('manifest.json'))
        assert file_sha(new_path) == nm['prompts_sha256']
        new_b2 = {r['id']: r for r in rows(new_path)}
        assert set(old_b2) == set(new_b2) == set(old_by_id)
        for old in original:
            uid = old['id']
            b2 = old_b2[uid]
            assert old['prompt_sha256'] == sha(old['prompt'].encode('utf-8'))
            assert flip(b2['prompt']) == old['prompt'], 'Original flip is not exactly the original B2 with demo label inverted'
            assert b2['demo_ids'] == old['demo_ids']
            fresh = new_b2[uid]
            true_label = provenance[dataset]['labels'][fresh['demo_ids'][0]]
            new_prompt = flip(fresh['prompt'], true_label)
            new_sha = sha(new_prompt.encode('utf-8'))
            changed = new_sha != old['prompt_sha256']
            has_output = uid in seen
            decision = ('rerun_changed_prompt' if changed else 'keep_identical_prompt') if has_output else (
                'pending_changed_prompt_use_new' if changed else 'pending_identical_prompt')
            prior_change = b2_changes[dataset, split, uid]
            item = {'arm': 'B2-flip', 'dataset': dataset, 'split': split, 'id': uid, 'seed': 42,
                    'has_downloaded_output': has_output, 'decision': decision, 'prompt_changed': changed,
                    'old_demo_id': old['demo_ids'][0], 'new_demo_id': fresh['demo_ids'][0],
                    'old_demo_removed_from_new_bank': prior_change['old_demo_removed_from_new_bank'],
                    'old_prompt_sha256': old['prompt_sha256'], 'new_prompt_sha256': new_sha,
                    'source_records': record_path.relative_to(ROOT).as_posix() if has_output else ''}
            comparison.append(item)
            if has_output:
                downloaded.append(item)
            if changed:
                changed_review.append(dict(item, target_label=old['label'], new_prompt_text=new_prompt,
                    token_metadata_status='review text/hash only; recompute exact flip token metadata before packaging inference inputs'))
        stat = metrics(rr)
        eval_path = record_path.with_name('evaluation.json')
        if eval_path.exists():
            e = read(eval_path)
            assert e['n_total'] == stat['count']
            assert e['confusion_matrix'] == [[stat['TN'], stat['FP']], [stat['FN'], stat['TP']]]
            assert e['n_score_valid'] == len(rr) - stat['invalid_score']
        affected = [r for r in comparison if (r['dataset'], r['split']) == (dataset, split)]
        stat.update(dataset=dataset, split=split, expected=len(original), remaining=len(original)-len(rr),
                    rerun_completed=sum(r['decision'] == 'rerun_changed_prompt' for r in affected),
                    pending_changed=sum(r['decision'] == 'pending_changed_prompt_use_new' for r in affected),
                    keep_completed=sum(r['decision'] == 'keep_identical_prompt' for r in affected),
                    all_changed=sum(r['prompt_changed'] for r in affected))
        split_results.append(stat)
    assert all(r == runtime_identities[0] for r in runtime_identities)
    assert len(downloaded) == status['completed_records_total'] == 5235
    all_records = [r for p in RUN.rglob('records.jsonl') for r in rows(p)]
    totals = metrics(all_records)
    rerun = [r for r in downloaded if r['decision'] == 'rerun_changed_prompt']
    pending = [r for r in comparison if r['decision'] == 'pending_changed_prompt_use_new']
    totals.update(expected=len(comparison), remaining=len(comparison)-len(downloaded), rerun_completed=len(rerun),
                  pending_changed=len(pending), keep_completed=len(downloaded)-len(rerun),
                  all_changed=len(rerun)+len(pending), completion_percent=100*len(downloaded)/len(comparison),
                  inference_calls_to_complete_unified=len(comparison)-len(downloaded)+len(rerun))
    assert totals['all_changed'] == 66
    export('all_prompt_comparison', comparison)
    export('downloaded_record_decisions', downloaded)
    export('mau_da_chay_can_inference_lai', rerun)
    export('mau_chua_chay_can_doi_prompt', pending)
    with (OUT / 'changed_prompt_text_review.jsonl').open('w', encoding='utf-8', newline='\n') as f:
        for r in changed_review:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    inventory = {'kernel': KERNEL, 'download_command': f'kaggle kernels output {KERNEL} -p {DOWNLOAD}',
                 'downloaded_at_audit_utc': datetime.now(timezone.utc).isoformat(), 'cli_version': '2.2.5',
                 'files': [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': file_sha(p)}
                           for p in sorted(DOWNLOAD.rglob('*')) if p.is_file()]}
    write(OUT / 'download_inventory.json', inventory)
    started = datetime.fromisoformat(status['started_at'])
    ended = datetime.fromisoformat(status['timed_out_at'])
    local_tz = timezone(timedelta(hours=7))
    result = {'run_id': 'I-06', 'arm': 'B2-flip', 'kernel': KERNEL,
              'created_utc': datetime.now(timezone.utc).isoformat(),
              'started_at_utc': started.isoformat(), 'stopped_at_utc': ended.isoformat(),
              'started_at_bangkok': started.astimezone(local_tz).isoformat(),
              'stopped_at_bangkok': ended.astimezone(local_tz).isoformat(),
              'elapsed_seconds': (ended-started).total_seconds(), 'status': status,
              'metrics_definition': 'raw greedy 0/1 response; TP=label1/raw1; TN=label0/raw0; FP=label0/raw1; FN=label1/raw0; not validation-tuned thresholds',
              'totals': totals, 'by_split': split_results, 'inference_identity': runtime_identities[0],
              'bundle_proofs': bundle_proofs, 'checkpoint_files_crosschecked': checked_checkpoint,
              'checkpoint_zip_sha256': file_sha(archive),
              'threshold_evidence_in_download': [p.relative_to(DOWNLOAD).as_posix() for p in DOWNLOAD.rglob('*threshold*.json')],
              'script_sha256': file_sha(Path(__file__)), 'llm_calls_during_audit': 0,
              'original_prompts_outputs_thresholds_modified': False}
    write(OUT / 'summary.json', result)
    lines = ['# I-06 — B2-flip Kaggle, checkpoint nhập ngày 02/11/2026', '',
        f'Nguồn: `{KERNEL}`. Output gốc lưu tại `04_Arm_B2_Flip/output/kaggle_20261102_quangdung1111_run1/`.', '',
        f'Chạy từ **{started.astimezone(local_tz):%d/%m/%Y %H:%M:%S}** đến **{ended.astimezone(local_tz):%d/%m/%Y %H:%M:%S} Asia/Bangkok**, '
        f'{(ended-started).total_seconds()/3600:.4f} giờ theo timestamp trong checkpoint. Trạng thái `timed_out`, dừng sau Devign test. '
        'Đã tải checkpoint và log; kiểm tra CRC, hash và đối chiếu nội dung ZIP checkpoint với các file output tải riêng.', '',
        f'**Hoàn thành {totals["count"]:,}/{totals["expected"]:,} ({totals["completion_percent"]:.2f}%), còn {totals["remaining"]:,} mẫu chưa chạy.**', '',
        '## Kết quả trên các mẫu đã inference', '',
        'TP/TN/FP/FN dưới đây tính từ `raw` token 0/1 của mô hình, cùng cách `evaluation.json` gốc. '
        'Đây là thống kê hiện trạng, không phải kết quả tại ngưỡng tối ưu validation. '
        '`invalid response` là raw không hợp lệ; `invalid score` là thiếu/không hữu hạn/sai miền score hoặc `valid=false`. '
        'Mẫu chưa chạy không được tính vào invalid.', '',
        '| Dataset | Split | Đã chạy / dự kiến | TP | TN | FP | FN | Invalid response | Invalid score |',
        '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in split_results:
        lines.append(f'| {r["dataset"]} | {r["split"]} | {r["count"]:,}/{r["expected"]:,} | {r["TP"]} | {r["TN"]} | {r["FP"]} | {r["FN"]} | {r["invalid_response"]} | {r["invalid_score"]} |')
    lines += [f'| **Tổng** | | **{totals["count"]:,}/{totals["expected"]:,}** | **{totals["TP"]}** | **{totals["TN"]}** | **{totals["FP"]}** | **{totals["FN"]}** | **{totals["invalid_response"]}** | **{totals["invalid_score"]}** |', '',
        '## Ảnh hưởng khi chuyển sang kho donor thống nhất', '',
        f'**{len(rerun)} mẫu đã có output phải inference lại** vì hash prompt cuối thay đổi. '
        f'**{len(pending)} mẫu đổi prompt còn chưa chạy** chỉ cần dùng prompt mới khi chạy lần đầu. '
        f'Giữ được {totals["keep_completed"]:,} output đã tải khi giữ inference identity. '
        'Tổng số target đổi prompt của toàn bộ B2-flip là 66, tất cả ở Devign.', '',
        f'Để hoàn tất toàn bộ B2-flip theo donor mới cần thêm **{totals["inference_calls_to_complete_unified"]:,} lượt LLM**: '
        f'{totals["remaining"]:,} mẫu chưa chạy + {len(rerun)} mẫu phải chạy lại. '
        f'{len(pending)} mẫu đổi prompt chưa chạy nằm trong phần {totals["remaining"]:,} này.', '',
        '| Dataset | Split | Đã chạy: cần inference lại | Đã chạy: giữ kết quả | Chưa chạy: cần dùng prompt mới | Tổng prompt thay đổi |',
        '|---|---|---:|---:|---:|---:|']
    for r in split_results:
        lines.append(f'| {r["dataset"]} | {r["split"]} | {r["rerun_completed"]} | {r["keep_completed"]} | {r["pending_changed"]} | {r["all_changed"]} |')
    lines += ['',
        'Năm Devign test đã chạy cần inference lại: ' + ', '.join(f'`{r["id"]}`' for r in rerun if r['split'] == 'test') + '.', '',
        '- [Các mẫu đã chạy cần inference lại (CSV)](mau_da_chay_can_inference_lai.csv).',
        '- [Các mẫu chưa chạy cần đổi prompt (CSV)](mau_chua_chay_can_doi_prompt.csv).',
        '- [Quyết định cho toàn bộ output tải về (CSV)](downloaded_record_decisions.csv).',
        '- [Đối chiếu toàn bộ 10.011 prompt (CSV)](all_prompt_comparison.csv).',
        '- `changed_prompt_text_review.jsonl`: nội dung prompt mới của 66 target đổi, để đọc/so hash; chưa phải bundle inference, cần metadata token đúng trước khi đóng gói.', '',
        '## Cách đối chiếu', '',
        '1. Dùng đúng bốn ZIP prompt nằm trong output Kaggle làm nguồn prompt gốc; kiểm tra manifest, hash archive và từng record ID/label/hash prompt/demo/model/seed.',
        '2. Kiểm tra toàn bộ 10.011 prompt B2-flip cũ bằng cách đảo đúng câu nhãn demo của B2 cũ; phải giống từng ký tự với bundle Kaggle.',
        '3. Tái dùng bộ B2 tham chiếu donor thống nhất đã được kiểm toán trước đó. Kiểm tra hash bộ tham chiếu và cache bank; '
        'đảo nhãn thật của demo mới để dựng B2-flip mới, giữ nguyên code target, graph, câu dẫn và code demo từ B2 phiên mới.',
        '4. So hash toàn bộ prompt cuối, rồi giao danh sách thay đổi với ID thực có output. Không suy ra số rerun chỉ từ donor bị loại hoặc chỉ từ số 66 của B2.', '',
        '## Thứ tự validation/test và giữ lịch sử', '',
        'Hai validation đã đủ, nhưng output tải về không kèm `thresholds.json`/`threshold_lock.json`; '
        'vì vậy checkpoint này không cung cấp bằng chứng đã khóa ngưỡng trước 230 mẫu Devign test. Giữ nguyên thông tin thứ tự khi báo cáo. '
        'CM ở trên dùng raw; không lấy nhãn/score test để chọn ngưỡng trong kiểm toán này.', '',
        'Khi chuyển donor, validation Devign B2-flip đổi 28 prompt: inference lại 28, ghép với 2.704 score validation còn khớp, '
        'rồi tính/khóa ngưỡng riêng cho phiên mới trên đủ 2.732 validation trước test mới. Không ghi đè ngưỡng/kết quả lịch sử.', '',
        'Muốn tiếp tục đúng phiên donor cũ: dùng `grace_b2_flip_checkpoint.zip` đã tải để resume phần còn thiếu. '
        'Muốn chuyển donor mới: tạo phiên input/output riêng, chỉ tái dùng các record còn khớp prompt và runtime; '
        'checkpoint cũ chứa hash cũ của các target đổi nên không được coi chúng là đã hoàn thành prompt mới.', '',
        'Kiểm toán chỉ chạy CPU, không gọi LLM, không ghi đè prompt/output cũ hoặc các khóa ngưỡng. '
        '[Tóm tắt máy đọc được](summary.json), [danh sách/hash file tải về](download_inventory.json).', '']
    (OUT / 'KET_QUA_I06_B2_FLIP.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'totals': totals, 'by_split': split_results,
                      'started_at_bangkok': result['started_at_bangkok'], 'stopped_at_bangkok': result['stopped_at_bangkok']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
