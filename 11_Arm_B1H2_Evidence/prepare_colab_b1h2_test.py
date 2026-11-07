import sys, json, zipfile, hashlib, os
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('HF_HUB_CACHE', str(ROOT/'output/hf_tokenizer_cache'))
sys.path.insert(0, str(ROOT / 'Runs-management'))
from dry_run_full_validation import ExactCounter, render_project

OUT = ROOT / '11_Arm_B1H2_Evidence/colab_l4_b1h2_test_20261106'
OUT.mkdir(exist_ok=True)
SOURCE = ROOT.parent / 'grace_15arms_prompts_and_clean_specs (1).zip'
source_hash=hashlib.sha256()
with SOURCE.open('rb') as stream:
    for chunk in iter(lambda:stream.read(4*1024*1024),b''):source_hash.update(chunk)
if source_hash.hexdigest()!='9db0d3eebb66a2f83c1f9803ceb0192954a3dfe2c3de9515188a996ede84ed7b':
    raise ValueError('Original source archive checksum changed')
counter = ExactCounter()
prompts = []
sources = {}
with zipfile.ZipFile(SOURCE) as z:
    for ds in ('devign', 'reveal'):
        # Establish that the original renderer still reproduces the supplied validation packet.
        val = f'prompts/dry_run_validation_20261102/{ds}/validation/B1-H2/42/prompts.jsonl'
        expected = {r['id']: r for r in map(json.loads, z.read(val).splitlines())}
        checked = 0
        with z.open(f'specs/{ds}_validation_15arms.jsonl') as f:
            for line in f:
                spec = json.loads(line)
                clean = {k:v for k,v in spec.items() if k not in ('label','target','target_label','ground_truth')}
                rendered = render_project(clean, 'B1-H2', 42, counter, None)
                if rendered.prompt != expected[spec['id']]['prompt']:
                    raise ValueError('Original renderer differs from validation packet: '+spec['id'])
                checked += 1
                if checked == 5: break
        member = f'specs/{ds}_test_15arms.jsonl'
        h = hashlib.sha256()
        count = 0
        with z.open(member) as f:
            for line in f:
                h.update(line)
                spec = json.loads(line)
                clean = {k:v for k,v in spec.items() if k not in ('label','target','target_label','ground_truth')}
                rendered = render_project(clean, 'B1-H2', 42, counter, None)
                prompts.append(dict(id=spec['id'],dataset=ds,split='test',arm='B1-H2',seed=42,
                                    prompt_variant='project_frozen_donor_dryrun_v1',prompt=rendered.prompt,
                                    prompt_sha256=hashlib.sha256(rendered.prompt.encode()).hexdigest(),evidence=rendered.evidence))
                count += 1
        if count != (2732 if ds == 'devign' else 2274): raise ValueError((ds,count))
        sources[ds] = dict(member=member,sha256=h.hexdigest(),count=count,validation_renderer_matches=checked)
        print(ds,count,flush=True)
if len({r['id'] for r in prompts}) != 5006: raise ValueError('Test ID coverage error')
payload = ''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in prompts).encode()
lock = json.loads((ROOT/'configs/thresholds.json').read_text(encoding='utf-8'))
manifest = dict(schema='b1h2_original_test_v1',created_utc=datetime.now(timezone.utc).isoformat(),
                count=len(prompts),dataset_counts={'devign':2732,'reveal':2274},sources=sources,
                prompts_sha256=hashlib.sha256(payload).hexdigest(),source_archive_sha256='9db0d3eebb66a2f83c1f9803ceb0192954a3dfe2c3de9515188a996ede84ed7b',
                thresholds={ds:lock['thresholds'][f'{ds}|B1-H2|42'] for ds in ('devign','reveal')},
                threshold_lock_sha256=lock['locked_sha256'],platform_deviation='Colab L4; preregistered Kaggle 2xT4; offload must be verified before test inference')
bundle=OUT/'b1h2_original_test_bundle.zip'
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('prompts.jsonl',payload)
    z.writestr('bundle_manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2))
    z.write(ROOT/'configs/thresholds.json','thresholds.json')
(OUT/'bundle_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('BUNDLE',bundle,'SHA256',hashlib.sha256(bundle.read_bytes()).hexdigest(),flush=True)
