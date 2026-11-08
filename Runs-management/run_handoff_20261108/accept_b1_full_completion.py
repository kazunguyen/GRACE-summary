"""Read-only B1-full acceptance; retain exact source bytes in the Git handoff."""
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import sys
from datetime import datetime, timezone
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
STAGE = ROOT / 'Runs-management/locked_continuations_20261108/b1_full'
REMOTE = STAGE / 'remote_output'
RUN = REMOTE / 'b1_full_locked_20261108'
DEST = OUT / 'completed_results/b1_full_test_completed_20261108'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def digest(b): return hashlib.sha256(b).hexdigest()
delivery = read(STAGE/'delivery.json')
identity = read(RUN/'run_identity.json')
contract_path = RUN/'inference_runtime_lock.json'
c = read(contract_path)
current = read(ROOT/'configs/inference_runtime_lock.json')
provenances = list(RUN.glob('locked_*/runtime_provenance.json'))
assert len(provenances) == 1
provpath = provenances[0]; prov = read(provpath)
checks = {}
def check(name, value): checks[name] = bool(value)
contract_sha = sha(contract_path)
check('launch_contract_byte_hash',contract_sha==identity['runtime_contract_sha256']==prov['runtime_contract_sha256']== '85d8770839f80260cdc7c27b27b6cce6bf8815675c8593db68fb102589c5cbd6')
body={k:v for k,v in c.items() if k!='integrity'}
check('launch_contract_canonical_seal',digest(json.dumps(body,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())==c['integrity']['sha256']==prov['runtime_contract_integrity'])
check('packages_all_launch_pins',all(prov['packages'].get(k)==v for k,v in c['packages'].items()))
freeze=dict(line.split('==',1) for line in prov['pip_freeze'].splitlines() if '==' in line)
observed_scipy=freeze.get('scipy')
check('constructor',prov['constructor']==identity['constructor']==c['constructor'])
check('model_identity',prov['model_sha256']==identity['model_sha256']==delivery.get('model_sha256',c['model']['sha256'])==c['model']['sha256'])
check('input_worker_helper_identity',prov['input_manifest_sha256']==delivery['input_manifest_sha256']==identity['input_manifest_sha256'] and prov['runner_sha256']==delivery['worker_sha256']==sha(REMOTE/'kaggle_inference.py') and prov['runtime_helper_sha256']==sha(REMOTE/'grace_runtime_contract.py'))
check('backend_source_archive',sha(REMOTE/c['backend_source']['sdist_filename'])==prov['backend_sdist_sha256']==c['backend_source']['sdist_sha256'])
buildlog=provpath.parent/'backend_build.log';offlog=provpath.parent/'model_load_offload.log'
check('native_and_build_log_hashes',sha(buildlog)==prov['backend_build_log_sha256'] and sha(offlog)==prov['offload_log_sha256'])
native=offlog.read_text(encoding='utf-8');build=buildlog.read_text(encoding='utf-8')
check('two_t4_native_devices',set(re.findall(r'using device CUDA(\d+) \(Tesla T4\)',native))=={'0','1'})
check('full_gpu_offload',bool(re.search(r'offloaded 49/49 layers to GPU',native)))
check('context_batch_ubatch',all(re.search(r'\b'+key+r'\s*=\s*'+str(c['constructor'][key])+r'\b',native) for key in ('n_ctx','n_batch','n_ubatch')))
check('both_gpu_model_buffers',all(re.search(r'CUDA'+str(i)+r' model buffer size',native) for i in (0,1)))
check('cuda_build_success', 'Successfully built llama_cpp_python' in build and 'compute_75' in build and 'libggml-cuda.so' in build)
check('build_environment',all(prov['build_environment'].get(k)==c['build'][k] for k in ('CMAKE_BUILD_PARALLEL_LEVEL','FORCE_CMAKE')) and all(s in prov['build_environment']['CMAKE_ARGS'] for s in ('GGML_CUDA=on','CMAKE_CUDA_ARCHITECTURES=75','CMAKE_LIBRARY_PATH=/usr/local/nvidia/lib64')))
check('provenance_platform_and_threads',prov['python'].startswith('3.13.') and 'Linux' in prov['platform'] and prov['n_threads']==max(prov['cpu_count']//2,1) and prov['n_threads_batch']==prov['cpu_count'])
check('complete_build_provenance',all(prov.get(k) for k in ('nvcc','compiler','cxx_compiler','cmake','pip_freeze','compiled_backend_sha256','gpu_before_load','gpu_after_load','libc')) and all(re.fullmatch('[0-9a-f]{64}',v) for v in prov['compiled_backend_sha256'].values()))
# Notebook JSON permits cell source as a string or a list of string fragments.
# Compare the exact resulting cell text; do not strip whitespace/newlines.
check('reviewed_notebook_source',sha(STAGE/'kernel/notebook.ipynb')==delivery['notebook_sha256'] and [''.join(x.get('source','')) for x in read(STAGE/'kernel/notebook.ipynb')['cells']]==[''.join(x.get('source','')) for x in read(STAGE/'remote_notebook.json')['cells']] and read(STAGE/'remote_source_verification.json')['all_cell_sources_match'])

groups=[]
from sklearn.metrics import roc_auc_score,matthews_corrcoef,balanced_accuracy_score,f1_score
with ZipFile(STAGE/'dataset/grace_locked_b1_full_20261108.zip') as z:
    check('input_bundle_sha',sha(STAGE/'dataset/grace_locked_b1_full_20261108.zip')==delivery['bundle_sha256'])
    raw=z.read('input_manifest.json');m=json.loads(raw)
    check('input_manifest_sha',digest(raw)==delivery['input_manifest_sha256'])
    check('fresh_only',m['legacy_count']==identity['legacy_count']==0 and z.read('legacy_records.jsonl')==b'')
    for lock in m['threshold_locks']:
        payload=z.read(lock['member']);check('threshold_lock_bytes_'+lock['member'],digest(payload)==lock['sha256'])
        obj=json.loads(payload);unsigned={k:v for k,v in obj.items() if k!='locked_sha256'}
        check('threshold_lock_seal_'+lock['member'],obj['locked_sha256'] in (digest(json.dumps(unsigned,sort_keys=True,ensure_ascii=False,indent=2).encode()),digest(json.dumps(unsigned,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode())))
    lock=json.loads(z.read(m['threshold_locks'][0]['member']))
    for g in m['groups']:
        ds=g['dataset'];payload=z.read(g['member']);prompts=[json.loads(x) for x in payload.splitlines() if x.strip()];expected={x['id']:x for x in prompts}
        records=[json.loads(x) for x in (RUN/'B1-full/seed_42'/ds/'test/records.jsonl').read_bytes().splitlines() if x.strip()]
        check(ds+'_input_hash',digest(payload)==g['sha256'])
        check(ds+'_census',len(records)==len({x['id'] for x in records})==g['count'] and {x['id'] for x in records}==set(expected))
        freeze_dir=ROOT/'01_Author_Baseline_Unified/output/research_freeze_20261101'
        freeze_manifest=read(freeze_dir/'freeze_manifest.json')
        rawfile=freeze_dir/ds/'test_raw.jsonl'
        check(ds+'_official_raw_hash',sha(freeze_dir/'freeze_manifest.json')=='e1d3c6b17c3a0b5c1e05203794d48a33825e0ea00a55deaaef565af25efe0448' and sha(rawfile)==freeze_manifest['datasets'][ds]['files_sha256']['test_raw.jsonl'])
        official={r['id']:r for r in (json.loads(x) for x in rawfile.read_bytes().splitlines() if x.strip())}
        check(ds+'_official_ids_labels',set(official)==set(expected) and all(r['label']==official[r['id']]['target'] for r in records))
        ok=True;errors=[]
        for row in records:
            exp=expected[row['id']]
            val=all(row[k]==exp[k] for k in ('id','dataset','split','label','prompt_sha256','demo_ids','tokens','graph_missing'))
            val &= digest(exp['prompt'].encode())==row['prompt_sha256'] and row['arm']=='B1-full' and row['seed']==42
            val &= row['record_origin']=='fresh_locked' and row['runtime_provenance']==provpath.relative_to(RUN).as_posix() and row['runtime_provenance_sha256']==sha(provpath)
            val &= row['model_sha256']==prov['model_sha256'] and row['runtime_contract_sha256']==contract_sha and row['inference_seed']==c['constructor']['seed'] and row['tokenizer_revision']==c['tokenizer']['revision']
            val &= row['token_ids']=={'0':15,'1':16} and row['valid'] is True and all(math.isfinite(row[k]) for k in ('logprob_0','logprob_1','s'))
            lp0,lp1=row['logprob_0'],row['logprob_1'];mx=max(lp0,lp1);score=math.exp(lp1-mx)/(math.exp(lp0-mx)+math.exp(lp1-mx))
            val &= abs(score-row['s'])<1e-12 and abs(math.exp(lp0)-row['p0'])<1e-12 and abs(math.exp(lp1)-row['p1'])<1e-12
            val &= row['tau']==g['tau'] and row['pred_tau']==int(row['s']>=g['tau']) and row['pred_argmax']==int(row['s']>=.5)
            val &= row['tokens']['approx'] is False and row['tokens']['total']+64<=8192 and row['tokens']['code']<=3000 and row['tokens']['graph']<=1500
            if not val:errors.append(row['id']);ok=False
        check(ds+'_all_record_identity_score_budget_checks',ok)
        check(ds+'_validation_threshold_inherited',any(e['arm']=='B1-full' and e['dataset']==ds and e['tau_star']==g['tau'] for e in lock['entries'].values()))
        y=[r['label'] for r in records];scores=[r['s'] for r in records];pred=[r['pred_tau'] for r in records]
        groups.append(dict(dataset=ds,count=len(records),unique_ids=len({r['id'] for r in records}),errors=errors,tau=g['tau'],raw_response_invalid=sum(not r['response_valid'] for r in records),metrics=dict(auroc=roc_auc_score(y,scores),mcc=matthews_corrcoef(y,pred),ba=balanced_accuracy_score(y,pred),f1=f1_score(y,pred))))
    for name in ('input_manifest.json','threshold_lock.json','renderer_audit.json'):(DEST/name).write_bytes(z.read(name))
checkpoint=REMOTE/'b1_full_locked_20261108_checkpoint.zip'
with ZipFile(checkpoint) as z:
    check('checkpoint_crc',z.testzip() is None)
    check('checkpoint_records_exact',all(z.read('B1-full/seed_42/'+ds+'/test/records.jsonl')==(RUN/'B1-full/seed_42'/ds/'test/records.jsonl').read_bytes() for ds in ('devign','reveal')))
for p in (buildlog,):shutil.copyfile(p,DEST/p.relative_to(RUN))
evidence=OUT/'b1_full_runtime_acceptance_evidence';evidence.mkdir(exist_ok=True)
for p in (STAGE/'delivery.json',STAGE/'launch.json',STAGE/'remote_source_verification.json',REMOTE/'kaggle_inference.py',REMOTE/'grace_runtime_contract.py'):
    shutil.copyfile(p,evidence/p.name)
result=dict(checked_at_utc=datetime.now(timezone.utc).isoformat(),checks=checks,all_checks_pass=all(checks.values()),runtime_acceptance='PASS_LAUNCH_CONTRACT' if all(checks.values()) else 'FAIL',runtime_contract_sha256=contract_sha,later_current_contract_sha256=sha(ROOT/'configs/inference_runtime_lock.json'),scipy_observed_in_pip_freeze=observed_scipy,scipy_current_pin=current['packages'].get('scipy'),later_contract_retroactive_certification=False,groups=groups,checkpoint=dict(bytes=checkpoint.stat().st_size,sha256=sha(checkpoint)),limitations=['Model file and loaded compiled libraries were hashed by the verified runner on Kaggle; audit verifies recorded provenance and source/build logs, not a local rehash of the large model or remote loaded memory.','Acceptance applies to the six-package contract pinned at launch, not a claim that the later SciPy-added contract was loaded.','No model rerun, threshold optimization or changes to frozen files.'])
(OUT/'b1_full_runtime_acceptance.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
sys.exit(0 if result['all_checks_pass'] else 1)
