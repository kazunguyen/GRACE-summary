"""Update future Kaggle notebook/runtime sources; preserve saved outputs/metadata."""
import ast,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
core=(HERE/'validation_lock.py').read_text(encoding='utf-8')
IMPORT='''
# Shared validation-only analysis; helper is embedded by the Kaggle notebook.
import sys
if str(Path(__file__).resolve().parent.parent / 'Runs-management') not in sys.path:
    sys.path.insert(0,str(Path(__file__).resolve().parent.parent / 'Runs-management'))
from validation_lock import make_lock,persist_lock,require_test_lock,evaluate_at_locked_threshold,read_jsonl,file_sha256
'''
def instrument(source,arm):
    if 'require_test_lock(' in source:return source
    source=source.replace('import numpy as np\n','import numpy as np\n'+IMPORT,1)
    source=source.replace('checkpoint_reserve_seconds, status_path):','checkpoint_reserve_seconds, status_path, thresholds_path=None):',1)
    source=source.replace('    started = time.time()','    thresholds_path = Path(thresholds_path) if thresholds_path else Path(status_path).parent / "thresholds.json"\n    started = time.time()',1)
    if arm=='B2':source=source.replace('n_gpu_layers=gpu_layers, logits_all=True, verbose=True)','n_gpu_layers=gpu_layers, logits_all=True, seed=42, verbose=True)')
    marker="        identity_file = out / 'run_manifest.json'"
    gate=f'''        locked_threshold = None
        if split == 'test':
            val_hash = None
            for vd,vs,vb,vo in runs:
                if vd == dataset and vs == 'validation':
                    val_hash = load_bundle(vb)[0]['prompts_sha256']
                    break
            locked_threshold = require_test_lock(thresholds_path,'{arm}',dataset,identity,val_hash)
            print(f'Test threshold locked: {{dataset}} tau={{locked_threshold["tau"]}}',flush=True)
'''
    assert marker in source;source=source.replace(marker,gate+marker,1)
    marker='        metrics = evaluate_output(output)'
    auto=f'''        if split == 'validation' and limit is None:
            locked_threshold = persist_lock(thresholds_path,make_lock(rows,list(done.values()),'{arm}',dataset,identity,
                manifest['prompts_sha256'],[{{'path':str(output),'records_sha256':file_sha256(output)}}]))
            write_json_atomic(out/'threshold_lock.json',locked_threshold)
            print(f'Validation threshold auto-locked: {{dataset}} tau={{locked_threshold["tau"]}}',flush=True)
'''
    assert marker in source;source=source.replace(marker,auto+marker,1)
    marker="        (out / 'evaluation.json').write_text"
    extra="        if locked_threshold is not None:\n            metrics['score_threshold_validation_locked'] = evaluate_at_locked_threshold(list(done.values()),locked_threshold)\n"
    source=source.replace(marker,extra+marker,1)
    source=source.replace("    ap.add_argument('--model', required=True)","    ap.add_argument('--thresholds', help='Defaults to thresholds.json beside checkpoint_status.json')\n    ap.add_argument('--model', required=True)",1)
    source=source.replace('args.deadline_epoch, args.checkpoint_reserve_seconds, args.status)','args.deadline_epoch, args.checkpoint_reserve_seconds, args.status, args.thresholds)')
    source=source.replace('args.deadline_epoch,\n              args.checkpoint_reserve_seconds, args.status)','args.deadline_epoch,\n              args.checkpoint_reserve_seconds, args.status, args.thresholds)')
    ast.parse(source);return source

for arm,nbpath,module_path in [
 ('B0',ROOT/'02_Arm_B0_Source_Only/notebooks/02_kaggle_qwen_q4_b0.ipynb',ROOT/'02_Arm_B0_Source_Only/kaggle_b0_runtime.py'),
 ('B2',ROOT/'01_Author_Baseline_Unified/notebooks/02_kaggle_qwen_q4_b2.ipynb',ROOT/'01_Author_Baseline_Unified/kaggle_b2_threshold_runtime.py')]:
    n=json.loads(nbpath.read_text(encoding='utf-8'))
    index=next(i for i,c in enumerate(n['cells']) if ''.join(c.get('source',[])).startswith('%%writefile') and 'kaggle_' in ''.join(c['source']).split('\n')[0])
    writer=n['cells'][index];header,old=''.join(writer['source']).split('\n',1)
    source=instrument(old,arm)
    writer['source']=(header+'\n'+source).splitlines(keepends=True)
    module_path.write_text(source,encoding='utf-8',newline='\n')
    helper={'cell_type':'code','execution_count':None,'id':'validation-threshold-helper','metadata':{},'outputs':[],
            'source':('%%writefile /kaggle/working/validation_lock.py\n'+core).splitlines(keepends=True)}
    old_helper=next((i for i,c in enumerate(n['cells']) if c.get('id')=='validation-threshold-helper'),None)
    if old_helper is None:n['cells'].insert(index,helper)
    else:n['cells'][old_helper]=helper
    note='''## Tự khóa ngưỡng validation trước test
Khi đủ validation của arm/dataset, runtime tự chọn tau theo MCC (lưới 0,01–0,99), lưu thresholds.json vào thư mục checkpoint. Test chỉ được xử lý khi có ngưỡng cùng model/tokenizer/backend. Chia phiên/resume vẫn dùng checkpoint cũ; nếu đã inference test ở phiên cũ thì ngưỡng chốt sau đó không biến run cũ thành đăng ký trước. Cập nhật notebook không thay mã đang chạy trên Kaggle.
'''
    if not any(c.get('id')=='validation-threshold-note' for c in n['cells']):
        n['cells'].insert(1,{'cell_type':'markdown','id':'validation-threshold-note','metadata':{},'source':note.splitlines(keepends=True)})
    nbpath.write_text(json.dumps(n,ensure_ascii=False,indent=1),encoding='utf-8',newline='\n')
    print('Updated future runtime:',arm)
