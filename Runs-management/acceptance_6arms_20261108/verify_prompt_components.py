"""Measure B1-full components using the repository's own block boundaries."""
from collections import Counter
import json
from pathlib import Path
import sys
from zipfile import ZipFile

from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "01_Author_Baseline_Unified/diagnostic_kit/src"))
from grace_diag.probes import split_blocks


def main():
    tokenizer = AutoTokenizer.from_pretrained(str(ROOT / "11_Arm_B1H2_Evidence/tokenizer_cache_v6/models--Qwen--Qwen3-Coder-30B-A3B-Instruct/snapshots/b2cff646eb4bb1d68355c01b18ae02e7cf42d120"), local_files_only=True)
    origin = ROOT / "Runs-management/kernel_outputs_harvest/huuhieu3333_grace-b1-full-test"
    report = []
    for path in sorted((origin / "b1_full_test_bundles").glob("*.zip")):
        with ZipFile(path) as z:
            prompts = [json.loads(line) for line in z.read("prompts.jsonl").splitlines() if line.strip()]
            manifest = json.loads(z.read("bundle_manifest.json"))
        ds = manifest["dataset"]
        completed = {r["id"] for r in (json.loads(l) for l in (origin / f"b1_full_test/seed_42/{ds}/test/records.jsonl").read_bytes().splitlines() if l.strip())}
        results = []
        for start in range(0, len(prompts), 32):
            batch = prompts[start:start + 32]
            blocks = [split_blocks(r["prompt"]) for r in batch]
            code_enc = tokenizer.backend_tokenizer.encode_batch([b["code"] for b in blocks], add_special_tokens=False)
            graph_enc = tokenizer.backend_tokenizer.encode_batch([b["graph"] for b in blocks], add_special_tokens=False)
            for row, code, graph in zip(batch, code_enc, graph_enc):
                if len(code.ids) > 3000 or len(graph.ids) > 1500:
                    results.append({"id": row["id"], "code_tokens": len(code.ids), "graph_tokens": len(graph.ids),
                                    "code_over": len(code.ids) > 3000, "graph_over": len(graph.ids) > 1500,
                                    "already_inferred": row["id"] in completed})
        summary = {"dataset": ds, "n": len(prompts), "code_over_3000": sum(r["code_over"] for r in results),
                   "graph_over_1500": sum(r["graph_over"] for r in results), "either_over": len(results),
                   "already_inferred_either_over": sum(r["already_inferred"] for r in results), "violations": results}
        report.append(summary)
        print({k: v for k, v in summary.items() if k != "violations"}, flush=True)
    (Path(__file__).parent / "b1_full_component_audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
