"""Run actual Step 8 with authentic empty pools in a new sandbox, no inputs manifest."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
import b3_step8_validation_census_builder as step8
release=OUT/'probe_sandbox/entrypoint_missing_inputs'
shutil.copytree(ROOT/'Runs-management/b3_verified_patch_v1/release_20261108_v2/pools',release/'pools')
log=io.StringIO()
with contextlib.redirect_stdout(log):
    step8.run_step8(release)
manifest=json.loads((release/'validation/validation_prompt_manifest.json').read_text(encoding='utf-8'))
result={'inputs_manifest_exists':(release/'inputs_manifest.json').exists(),
        'entrypoint_completed_without_inputs_manifest':True,
        'prompt_content_status':manifest['prompt_content_status'],
        'gpu_inference_status':manifest['gpu_inference_status']}
(OUT/'entrypoint_probe.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
(OUT/'entrypoint_probe.log').write_text(log.getvalue(),encoding='utf-8')
print(json.dumps(result,indent=2))
