import hashlib,json,sys
from pathlib import Path
import yaml
root=Path(__file__).parent
protocol_path=root/'diagnostic_kit/configs/protocol.yaml'
with protocol_path.open(encoding='utf-8') as f: protocol_text=f.read()
with protocol_path.open('w',encoding='utf-8',newline='\n') as f: f.write(protocol_text)
sys.path.insert(0,str(root/'diagnostic_kit/src'))
from grace_diag.llm_backend import load_backend_config
p=yaml.safe_load((root/'diagnostic_kit/configs/protocol.yaml').read_text(encoding='utf-8'))
f=root/p['dedup']['frozen_snapshot']
assert hashlib.sha256(f.read_bytes()).hexdigest()==p['dedup']['manifest_sha256']
cfg=load_backend_config(root/'diagnostic_kit/configs/backend_native.yaml')
assert cfg.scoring_policy==p['scoring']['policy']
assert cfg.model_sha256==p['backend']['model_sha256']
assert cfg.tokenizer_revision==p['backend']['tokenizer_revision']
assert p['graph_prefix']=={'nodes':40,'edges':80}
assert (root.parent/'Runs-management/TIEN_DO_PHUONG_AN_2.md').exists()
print('Final config, frozen manifest hash, scoring/model/tokenizer identities and progress report: OK')
