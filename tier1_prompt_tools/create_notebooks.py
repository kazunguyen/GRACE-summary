"""Rebuild only the three unexecuted tier-1 preparation notebooks."""
import json
import textwrap
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ARMS={'B1':'03_Arm_B1_Graph_Only','B2-flip':'04_Arm_B2_Flip','B2-rep':'05_Arm_B2_Rep'}
def cell(kind,text):
    out={'cell_type':kind,'metadata':{},'source':textwrap.dedent(text).strip()+'\n'}
    if kind=='code':out.update(execution_count=None,outputs=[])
    return out
for arm,name in ARMS.items():
    folder=ROOT/name; notebooks=folder/'notebooks'; notebooks.mkdir(parents=True,exist_ok=True)
    desc={'B1':'Có graph 40/80; không mã/nhãn demo; giữ câu dẫn demo trống như B0.',
          'B2-flip':'Giữ code target, graph và mã demo B2; chỉ đảo nhãn demo.',
          'B2-rep':'Giữ prompt B2 giống từng ký tự, gồm nhãn demo. Khi inference phải gọi model mới, không dùng response cache B2.'}[arm]
    cells=[cell('markdown',f'''# Sinh prompt {arm} từ cache B2

{desc}

Notebook chỉ đọc cache và sinh prompt, không gọi LLM, không chạy Joern/CodeT5 và không viết notebook inference.
Mặc định đủ Devign/REVEAL validation/test, theo đúng tập ID và demo B2 đã có. Không âm thầm chọn lại demo bằng kho donor mới: các cặp flip/rep cần cùng tham chiếu B2.
'''),cell('code',f'''
from pathlib import Path
import sys,subprocess,json
INSTALL_DEPENDENCIES=False
if INSTALL_DEPENDENCIES:
    subprocess.run([sys.executable,'-m','pip','install','numpy','transformers==4.57.1','sentencepiece'],check=True)
PROJECT_ROOT_OVERRIDE=None  # Folder GRACE-summary nếu kernel mở ngoài repo.
candidates=[Path(PROJECT_ROOT_OVERRIDE)] if PROJECT_ROOT_OVERRIDE else [Path.cwd(),*Path.cwd().parents]
ROOT=next((p.resolve() for p in candidates if (p/'tier1_prompt_tools/prepare_cached.py').is_file()),None)
if ROOT is None: raise FileNotFoundError('Mở notebook trong repo hoặc đặt PROJECT_ROOT_OVERRIDE')
ARM='{arm}'
ARM_ROOT=ROOT/'{name}'
BASELINE=ROOT/'01_Author_Baseline_Unified'
REFERENCE_ROOT=BASELINE/'output/local_full/bundles_recovered_joern_final_20261031'
FROZEN_ROOT=BASELINE/'output/research_freeze_20261101'
OUT_ROOT=ARM_ROOT/'output/bundles'
RUNS=[('devign','validation'),('reveal','validation'),('devign','test'),('reveal','test')]
sys.path.insert(0,str(ROOT/'tier1_prompt_tools'))
import importlib, prepare_cached
importlib.reload(prepare_cached)
from prepare_cached import prepare,cache_paths,render_paired,convert_graph,rows
print('Arm:',ARM)
print('B2 reference:',REFERENCE_ROOT)
print('Output:',OUT_ROOT)
'''),cell('markdown','''## Kiểm tra cache đã có

Specs B2 đã chứa CPG Joern và demo chọn bằng CodeT5. Tái sử dụng trực tiếp chúng là tầng cache cao nhất; không cần load encoder, chạy retrieval hay copy các file vectors.npy sang folder arm. Manifest/hash B2 và prompt từng mẫu sẽ được kiểm tra. Nếu B2 thay đổi, phải chọn thư mục tham chiếu đúng, không trộn hai phiên bản.
'''),cell('code','''
for dataset,split in RUNS:
    files,manifest=cache_paths(dataset,split,REFERENCE_ROOT)
    print(dataset,split,'B2 rows:',manifest['count'],'tokenizer:',manifest['tokenizer_revision'])
for dataset in sorted({d for d,s in RUNS}):
    for split in ('train','validation','test'):
        cache=BASELINE/'output/local_full'/dataset/'embedding_cache'/split
        m=json.loads((cache/'manifest.json').read_text(encoding='utf-8'))
        assert m['model']=='Salesforce/codet5-base@02cd2d31bb7c6d0e4d91156167b2de044989c733'
        assert m['completed']==len(m['rows']) and (cache/'vectors.npy').is_file(),'CodeT5 cache incomplete'
        print('CodeT5 cache reused via B2 demo selection:',dataset,split,m['completed'])
'''),cell('code','''
from transformers import AutoTokenizer
first_files,first_manifest=cache_paths(*RUNS[0],REFERENCE_ROOT)
tokenizer=AutoTokenizer.from_pretrained(first_manifest['tokenizer'],revision=first_manifest['tokenizer_revision'],trust_remote_code=False)
assert tokenizer.chat_template
from grace_diag.token_budget import TokenCounter
counter=TokenCounter(None); counter.tok=tokenizer; counter.approx=False
spec=next(rows(first_files['specs']))
reference=next(r for r in rows(first_files['prompts']) if str(r['id'])==str(spec['id']))
preview,evidence=render_paired(ARM,spec,reference['prompt'],counter,reference=reference)
print(preview)
print(json.dumps(evidence,ensure_ascii=False,indent=2))
if ARM=='B2-rep': assert preview==reference['prompt']
'''),cell('code','''
import importlib, prepare_cached
importlib.reload(prepare_cached)
prepare=prepare_cached.prepare
bundles,archive=prepare(ARM,REFERENCE_ROOT,OUT_ROOT,RUNS,tokenizer,
                      frozen_root=FROZEN_ROOT if FROZEN_ROOT.is_dir() else None)
print('Archive:',archive)
for path in bundles: print(path)
'''),cell('markdown','''## Đầu ra và đối chiếu

Mỗi split có prompts.jsonl, pairing_audit.jsonl, prompt_preview.txt, bundle_manifest.json và ZIP. Manifest ghi hash B2 gốc, số prompt giống B2, số graph thiếu và số demo B2 không thuộc kho donor mới. Đây là dữ liệu **ghép cặp với B2 đã có**, không tự chứng nhận tuân thủ snapshot donor mới. Nếu cần B2 xác nhận trên kho mới, phải tạo B2 mới rồi dùng cùng cache đó cho cả flip/rep.

B2-rep bắt buộc giống prompt B2 100%; các response/score B2 không được tái sử dụng khi chạy inference sau này. Với B1 không có demo trong prompt; nhãn thật của demo tham chiếu chỉ nằm ở pairing_audit, không đi vào renderer/prompt. Notebook sẽ dừng nếu hash nguồn, ID, nhãn target hoặc renderer B2 không khớp.
''')]
    for i,c in enumerate(cells):c['id']=f'{arm.lower()}-{i:02}'
    nb={'cells':cells,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.11'}},'nbformat':4,'nbformat_minor':5}
    (notebooks/f'01_prepare_{arm.lower().replace("-","_")}_prompts.ipynb').write_text(json.dumps(nb,ensure_ascii=False,indent=1),encoding='utf-8',newline='\n')
    (folder/'.gitignore').write_text('output/\n__pycache__/\n.pytest_cache/\n',encoding='utf-8')
    (folder/'README.md').write_text(f'''# {arm} — notebook sinh prompt

{desc}

Mở [notebook](notebooks/01_prepare_{arm.lower().replace('-','_')}_prompts.ipynb) và chạy các cell theo thứ tự. Kernel local/WSL, không cần GPU. Bật INSTALL_DEPENDENCIES nếu cần. Default đọc specs/prompt đã hoàn tất từ B2 tại `01_Author_Baseline_Unified/output/local_full/bundles_recovered_joern_final_20261031` và xuất cả bốn dataset/split vào `output/bundles/` của folder này.

Graph Joern và lựa chọn demo CodeT5 được dùng trực tiếp từ specs B2, không parse/encode/retrieve lại. Code dùng chung ở [tier1_prompt_tools](../tier1_prompt_tools/README.md). Notebook kiểm hash nguồn, dựng lại B2 để đối chiếu prompt, rồi mới tạo arm. Không sửa cache B2, không sao chép response B2 và chưa có notebook inference cho arm này.

Đầu ra ghép cặp với B2 gốc. Các demo không thuộc kho donor mới được thống kê trong manifest/audit; không âm thầm thay demo vì như vậy sẽ phá phép so flip/rep. Muốn chạy nghiên cứu trên kho donor mới, cần bộ B2 tham chiếu mới dùng chung cho các arm.
''',encoding='utf-8')
    print(notebooks)
