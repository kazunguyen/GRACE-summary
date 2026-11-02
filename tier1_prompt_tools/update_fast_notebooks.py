"""Patch performance-related cell source only; preserve user outputs and metadata."""
import ast
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FOLDERS=('03_Arm_B1_Graph_Only','04_Arm_B2_Flip','05_Arm_B2_Rep')
OLD_IMPORT='from prepare_cached import prepare,cache_paths,render_paired,convert_graph,rows'
NEW_IMPORT='''import importlib, prepare_cached
importlib.reload(prepare_cached)  # Nạp bản tối ưu mới kể cả khi kernel đã import module trước đó.
from prepare_cached import prepare,cache_paths,render_paired,convert_graph,rows'''
OLD_PREVIEW="preview,evidence=render_paired(ARM,spec,reference['prompt'],counter)"
NEW_PREVIEW="preview,evidence=render_paired(ARM,spec,reference['prompt'],counter,reference=reference)"
OLD_PREPARE='bundles,archive=prepare(ARM,REFERENCE_ROOT,OUT_ROOT,RUNS,tokenizer,'
NEW_PREPARE='''# Nạp lại helper trước khi chạy cell này để tránh dùng bản chậm đã nằm trong kernel.
import importlib, prepare_cached
importlib.reload(prepare_cached)
prepare=prepare_cached.prepare
bundles,archive=prepare(ARM,REFERENCE_ROOT,OUT_ROOT,RUNS,tokenizer,'''

for folder in FOLDERS:
    for path in (ROOT/folder/'notebooks').glob('*.ipynb'):
        n=json.loads(path.read_text(encoding='utf-8'));changed=False
        for c in n['cells']:
            if c['cell_type']!='code':continue
            src=''.join(c['source'])
            updated=src
            if 'importlib.reload(prepare_cached)' not in updated:
                updated=updated.replace(OLD_IMPORT,NEW_IMPORT)
                updated=updated.replace(OLD_PREPARE,NEW_PREPARE)
            updated=updated.replace(OLD_PREVIEW,NEW_PREVIEW)
            ast.parse(updated)
            if updated!=src:
                c['source']=updated.splitlines(keepends=True);changed=True
        if changed:
            path.write_text(json.dumps(n,ensure_ascii=False,indent=1),encoding='utf-8',newline='\n')
        print(path.name,'patched' if changed else 'already current')
