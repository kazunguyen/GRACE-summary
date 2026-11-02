"""Embed the maintained frozen-donor helpers into the two B2-flip notebooks."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def source(cell, text, kind=None):
    cell['source'] = text.splitlines(keepends=True)
    if kind:
        cell['cell_type'] = kind
    if cell['cell_type'] == 'code':
        cell['outputs'] = []
        cell['execution_count'] = None
    cell['metadata'] = {}


def save(path, nb):
    for cell in nb['cells']:
        cell['metadata'] = {}
        if cell['cell_type'] == 'code':
            cell['outputs'] = []
            cell['execution_count'] = None
    nb['metadata'].pop('widgets', None)
    nb['metadata'].pop('papermill', None)
    path.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')


def main():
    p = HERE / 'notebooks/01_prepare_b2_flip_prompts.ipynb'
    nb = json.loads(p.read_text(encoding='utf-8'))
    source(nb['cells'][0], '''# B2-flip — prompt từ kho donor thống nhất

Dùng bộ B2 tham chiếu đã truy hồi/fit whitening trên `research_freeze_20261101`, giữ nguyên target/graph/code demo và đảo nhãn **demo mới**. Không gọi LLM, Joern hoặc encoder CodeT5.

Xuất riêng `output/bundles_frozen_donor_20261101/grace_b2_flip_frozen_donor_inputs.zip`; bundle cũ được giữ để đối chiếu checkpoint I-06.
''')
    source(nb['cells'][1], '''from pathlib import Path
import sys, json, subprocess, importlib
INSTALL_DEPENDENCIES = False
if INSTALL_DEPENDENCIES:
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'transformers==4.57.1', 'sentencepiece'], check=True)
PROJECT_ROOT_OVERRIDE = None
candidates = [Path(PROJECT_ROOT_OVERRIDE)] if PROJECT_ROOT_OVERRIDE else [Path.cwd(), *Path.cwd().parents]
ROOT = next((p.resolve() for p in candidates if (p/'04_Arm_B2_Flip/prepare_frozen_flip.py').is_file()), None)
if ROOT is None:
    raise FileNotFoundError('Mở notebook trong repo hoặc đặt PROJECT_ROOT_OVERRIDE trỏ GRACE-summary')
sys.path.insert(0, str(ROOT/'04_Arm_B2_Flip'))
import prepare_frozen_flip
importlib.reload(prepare_frozen_flip)
REFERENCE_ROOT = prepare_frozen_flip.REFERENCE_ROOT
FROZEN_ROOT = prepare_frozen_flip.FROZEN_ROOT
LEGACY_ROOT = prepare_frozen_flip.LEGACY_ROOT
OUT_ROOT = prepare_frozen_flip.OUT_ROOT
LOCAL_FILES_ONLY = True  # Tokenizer đã cache; đặt False nếu cần tải đúng revision đã pin.
print('B2 của donor mới:', REFERENCE_ROOT)
print('Output mới:', OUT_ROOT)
''')
    source(nb['cells'][2], '''## Kiểm tra phiên donor và bộ B2 mới

Xác minh hash B2 tham chiếu, cache donor và snapshot đã kiểm toán. Bộ tham chiếu đã tái dùng cache Joern/CodeT5 và fit lại whitening trên kho mới. Notebook này chỉ dựng biến thể flip và đếm token bằng đúng tokenizer; không thực hiện lại retrieval.
''')
    source(nb['cells'][3], '''snapshot_sha, proofs = prepare_frozen_flip.inspect_sources(REFERENCE_ROOT, FROZEN_ROOT)
print('Donor snapshot SHA-256:', snapshot_sha)
for dataset, proof in proofs.items():
    print(dataset, 'donor mới:', len(proof['labels']))
''')
    source(nb['cells'][4], '''from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained(prepare_frozen_flip.TOKENIZER,
    revision=prepare_frozen_flip.TOKENIZER_REVISION, local_files_only=LOCAL_FILES_ONLY, trust_remote_code=False)
assert tokenizer.chat_template
reference = next(prepare_frozen_flip.rows(REFERENCE_ROOT/'devign/validation/prompts.jsonl'))
demo_id = reference['demo_ids'][0]
preview = prepare_frozen_flip.swap_demo_label(reference['prompt'], proofs['devign']['labels'][demo_id])
print('Demo mới:', demo_id)
print(preview)
''')
    source(nb['cells'][5], '''importlib.reload(prepare_frozen_flip)
bundles, archive = prepare_frozen_flip.prepare(tokenizer, REFERENCE_ROOT, FROZEN_ROOT, LEGACY_ROOT, OUT_ROOT)
print('Upload archive này lên Kaggle:', archive)
for path in bundles:
    print(path)
print((OUT_ROOT/'prepare_summary.json').read_text(encoding='utf-8'))
''')
    source(nb['cells'][6], '''## Đầu ra

Đủ 10.011 prompt trên bốn split. So với phiên cũ: Devign validation đổi 28, Devign test đổi 38, REVEAL không đổi. Mỗi dòng lưu `previous_prompt_sha256` và `previous_demo_ids` để notebook inference xác minh checkpoint cũ trước khi quyết định giữ/chạy lại; hash lạ phải bị từ chối.

Upload ZIP **frozen_donor** mới, checkpoint `grace_b2_flip_checkpoint.zip` của I-06 và model GGUF vào Input của notebook 02. Notebook 02 mặc định bật resume, chuyển checkpoint sang thư mục phiên mới, ưu tiên 33 mẫu đã chạy nhưng đổi prompt rồi tiếp tục phần thiếu. Giữ nguyên bundle/output lịch sử.
''')
    save(p, nb)
    p = HERE / 'notebooks/02_kaggle_qwen_q4_b2_flip.ipynb'
    nb = json.loads(p.read_text(encoding='utf-8'))
    # Permit rerunning this builder after the helper cell has already been inserted.
    nb['cells'] = [c for c in nb['cells'] if c.get('id') != 'frozen-validation-lock-helper']
    snapshot = hashlib.sha256((ROOT/'01_Author_Baseline_Unified/output/research_freeze_20261101/freeze_manifest.json').read_bytes()).hexdigest()
    source(nb['cells'][0], '''# B2-flip — donor thống nhất, sửa checkpoint rồi chạy tiếp

Gắn **bundle mới** `grace_b2_flip_frozen_donor_inputs.zip`, **checkpoint I-06** `grace_b2_flip_checkpoint.zip` và model Qwen GGUF Q4_K_M. Notebook tự tìm Input, không phụ thuộc username.

Mặc định resume: giữ 5.202 output còn khớp, chạy lại **28 Devign validation + 5 Devign test** đã đổi prompt trước, rồi tiếp tục **4.776 mẫu thiếu** bằng prompt mới. Sau 28 validation, ghép đủ 2.732 để khóa ngưỡng mới trước test. Tổng bổ sung cho checkpoint I-06: **4.809 lượt LLM**. Dừng/tiếp tục nhiều phiên vẫn giữ hàng đợi ưu tiên và không gọi lại mẫu mới đã hoàn thành.

Ngân sách 9 giờ 35 phút, chừa 5 phút đóng gói; một mẫu đang chạy có thể vượt thời điểm dừng. Checkpoint gốc được lưu trong `history/`; kết quả phiên mới nằm ở thư mục riêng. Bundle cũ trong Input được bỏ qua bằng kiểm tra phiên donor.
''')
    source(nb['cells'][3], '''KAGGLE_INPUT_ROOT = Path('/kaggle/input')
BUNDLE_WORK = Path('/kaggle/working/grace_b2_flip_frozen_donor_bundles')
MODEL_FILENAME = 'Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf'
RESUME_FROM_CHECKPOINT = True
CHECKPOINT_INPUT_PATH = None  # Chỉ cần đặt nếu gắn nhiều checkpoint cùng tên.
EXPECTED_DONOR_SHA = ''' + repr(snapshot) + '''
EXPECTED_VARIANT = 'b2_flip_frozen_donor_v1'
if RESUME_FROM_CHECKPOINT:
    if CHECKPOINT_INPUT_PATH is None:
        candidates = sorted(KAGGLE_INPUT_ROOT.rglob('grace_b2_flip_checkpoint.zip'))
        if len(candidates) != 1:
            raise ValueError(f'Gắn đúng một checkpoint B2-flip hoặc đặt CHECKPOINT_INPUT_PATH: {candidates}')
        CHECKPOINT_INPUT_PATH = candidates[0]
    CHECKPOINT_INPUT_PATH = Path(CHECKPOINT_INPUT_PATH)
    if not CHECKPOINT_INPUT_PATH.is_file():
        raise FileNotFoundError(CHECKPOINT_INPUT_PATH)
MAX_RUNTIME_HOURS = 9 + 35/60
CHECKPOINT_RESERVE_SECONDS = 300
GPU_LAYERS = -1
OUT_ROOT = Path('/kaggle/working/grace_b2_flip_frozen_donor_20261101_9h35')
EXPECTED_RUNS = [('devign','validation'), ('reveal','validation'), ('devign','test'), ('reveal','test')]
note(f'Output phiên mới: {OUT_ROOT}; resume={RESUME_FROM_CHECKPOINT}; checkpoint={CHECKPOINT_INPUT_PATH}')
''')
    discovery = ''.join(nb['cells'][4]['source'])
    discovery = discovery.replace("if manifest.get('arm') != 'B2-flip':", "if (manifest.get('arm') != 'B2-flip' or manifest.get('prompt_variant') != EXPECTED_VARIANT):")
    if 'Wrong frozen donor snapshot:' not in discovery:
        discovery = discovery.replace("key = (manifest.get('dataset'), manifest.get('split'))", "if manifest.get('donor_snapshot_sha256') != EXPECTED_DONOR_SHA:\n        raise ValueError(f'Wrong frozen donor snapshot: {origin}')\n    key = (manifest.get('dataset'), manifest.get('split'))")
    discovery = discovery.replace("rglob('grace_b2_flip_inputs.zip')", "rglob('grace_b2_flip*inputs.zip')")
    discovery = discovery.replace('grace_b2_flip_inputs.zip hoặc các bundle B2-flip riêng.', 'grace_b2_flip_frozen_donor_inputs.zip mới từ notebook 01.')
    discovery = discovery.replace('; LIMIT={LIMIT}', '')
    source(nb['cells'][4], discovery)
    source(nb['cells'][10], '%%writefile /kaggle/working/kaggle_flip_frozen_runtime.py\n' + (HERE/'kaggle_flip_frozen_runtime.py').read_text(encoding='utf-8'))
    source(nb['cells'][11], '''# Runtime tự chuyển checkpoint; không extract checkpoint cũ đè lên output mới.
OUT_ROOT.mkdir(parents=True, exist_ok=True)
STATUS_PATH = OUT_ROOT/'checkpoint_status.json'
RUN_DEADLINE_EPOCH = time.time() + MAX_RUNTIME_HOURS*3600
cmd = [sys.executable, '-u', '/kaggle/working/kaggle_flip_frozen_runtime.py',
       '--model', model_path, '--gpu-layers', str(GPU_LAYERS),
       '--deadline-epoch', str(RUN_DEADLINE_EPOCH), '--checkpoint-reserve-seconds', str(CHECKPOINT_RESERVE_SECONDS),
       '--status', str(STATUS_PATH), '--snapshot-sha256', EXPECTED_DONOR_SHA]
if RESUME_FROM_CHECKPOINT:
    cmd += ['--checkpoint', str(CHECKPOINT_INPUT_PATH)]
for dataset, split in EXPECTED_RUNS:
    cmd += ['--run', dataset, split, str(BUNDLE_PATHS[dataset,split]), str(OUT_ROOT/dataset/split)]
try:
    run_logged(cmd, 'inference_batch')
finally:
    # Cả timeout/lỗi backend đều giữ những record đã fsync để có thể tiếp tục.
    if (OUT_ROOT/'migration_ready.json').is_file():
        checkpoint_archive = shutil.make_archive('/kaggle/working/grace_b2_flip_checkpoint', 'zip', root_dir=OUT_ROOT)
        print('Checkpoint phiên donor mới:', checkpoint_archive)
    else:
        print('Chưa chuyển xong checkpoint; sửa lỗi đầu vào rồi dùng lại checkpoint gốc đã gắn.')
    diagnostics_zip()
if STATUS_PATH.exists():
    print(STATUS_PATH.read_text(encoding='utf-8'))
''')
    source(nb['cells'][12], '''status = json.loads((OUT_ROOT/'checkpoint_status.json').read_text(encoding='utf-8'))
print('Trạng thái:', status['state'])
print('Đã có output tương thích:', status['completed_records_total'], '/ 10011')
print('Đã sửa prompt:', status['repair_completed'], '/', status['repair_total'])
print('LLM calls phiên này:', status['inferred_this_session'])
print('Tải grace_b2_flip_checkpoint.zip để tiếp tục phiên sau nếu chưa hoàn tất.')
diagnostics_zip()
''')
    source(nb['cells'][13], '''Ngưỡng nằm trong `OUT_ROOT/thresholds.json` của **phiên donor mới**. Runtime khóa từ validation đầy đủ và kiểm tra trước mỗi test; không sao chép ngưỡng phiên cũ. Model/tokenizer/backend/seed/hash checkpoint sai sẽ dừng. Bản checkpoint I-06 gốc được giữ trong `history/original_checkpoint.zip`, record cũ bị thay trong `history/stale_records.jsonl`.
''')
    helper = {'cell_type': 'code', 'id': 'frozen-validation-lock-helper', 'metadata': {}, 'execution_count': None,
              'outputs': [], 'source': ('%%writefile /kaggle/working/validation_lock.py\n' + (ROOT/'Runs-management/validation_lock.py').read_text(encoding='utf-8')).splitlines(keepends=True)}
    nb['cells'].insert(10, helper)
    save(p, nb)
    print('Updated both B2-flip notebooks; cleared old execution output.')


if __name__ == '__main__':
    main()
