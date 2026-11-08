import os
import sys
import shutil
import time
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "08_Arm_B1_Shuf"))
import prepare_shuf

out_dir = ROOT / "08_Arm_B1_Shuf/output/test_shuf_prompts"
if out_dir.exists():
    print(f"Cleaning existing incomplete test prompts in {out_dir}...")
    shutil.rmtree(out_dir)

out_dir.mkdir(parents=True, exist_ok=True)

from transformers import AutoTokenizer
print("Loading AutoTokenizer for prompt generation...")
tokenizer = AutoTokenizer.from_pretrained(
    "Qwen/Qwen3-Coder-30B-A3B-Instruct",
    revision=prepare_shuf.REVISION,
    trust_remote_code=False,
    local_files_only=False
)

print("\nStarting prepare_shuf for test census (Devign + ReVeal across 3 seeds: 42, 43, 44)...")
t0 = time.time()
archive_path = prepare_shuf.prepare(
    b1_root=ROOT / "03_Arm_B1_Graph_Only/output/bundles",
    b2_root=ROOT / "01_Author_Baseline_Unified/output/local_full/bundles_recovered_joern_final_20261031",
    frozen_root=ROOT / "01_Author_Baseline_Unified/output/research_freeze_20261101",
    out_root=out_dir,
    tokenizer=tokenizer,
    runs=[("devign", "test"), ("reveal", "test")]
)

print(f"\nSUCCESS: Generated all B1-shuf test prompts in {time.time() - t0:.1f}s!")
print(f"Archive created at: {archive_path}")

# Verify generated prompt files
for seed in [42, 43, 44]:
    for ds in ["devign", "reveal"]:
        p_path = out_dir / f"seed_{seed}" / ds / "test" / "prompts.jsonl"
        lines = len(p_path.read_text(encoding="utf-8").splitlines())
        print(f"  -> seed_{seed} {ds} test: {lines} prompts")
