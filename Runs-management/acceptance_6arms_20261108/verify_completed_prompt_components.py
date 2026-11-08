"""Check graph/demo budgets and shared code/graph of the three complete arms."""
import hashlib
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
    harvest = ROOT / "Runs-management/kernel_outputs_harvest"
    report = []
    for ds in ["devign", "reveal"]:
        groups = {}
        for arm, slug, folder in [
            ("B2-rep", "huuhieu3333_grace-b2-rep-test", "b2_rep_test_bundles"),
            ("B2-nolabel", "tomandjerry223_grace-b2-nolabel-test", "b2_nolabel_test_bundles"),
            ("B2-labelonly", "tomandjerry223_grace-b2-labelonly-test", "b2_labelonly_test_bundles"),
        ]:
            path = harvest / slug / folder / f"42_{ds}_test.zip"
            with ZipFile(path) as z:
                groups[arm] = {r["id"]: split_blocks(r["prompt"]) for r in (json.loads(l) for l in z.read("prompts.jsonl").splitlines() if l.strip())}
        base = groups["B2-rep"]
        assert all(set(g) == set(base) for g in groups.values())
        differences = []
        for uid, b in base.items():
            for arm in ["B2-nolabel", "B2-labelonly"]:
                other = groups[arm][uid]
                if b["code"] != other["code"] or b["graph"] != other["graph"]:
                    differences.append({"id": uid, "arm": arm})
            a = b["demo"].partition("\n")[2].strip("\n")
            b_demo = groups["B2-nolabel"][uid]["demo"].partition("\n")[2].strip("\n")
            if a != b_demo:
                differences.append({"id": uid, "arm": "B2-nolabel", "issue": "demo_code_changed"})
        ids = list(base)
        violations = []
        for start in range(0, len(ids), 32):
            batch = ids[start:start + 32]
            graphs = tokenizer.backend_tokenizer.encode_batch([base[i]["graph"] for i in batch], add_special_tokens=False)
            demos = tokenizer.backend_tokenizer.encode_batch([base[i]["demo"].partition("\n")[2].strip("\n") for i in batch], add_special_tokens=False)
            for uid, graph, demo in zip(batch, graphs, demos):
                if len(graph.ids) > 1500 or len(demo.ids) > 1500:
                    violations.append({"id": uid, "graph_tokens": len(graph.ids), "demo_code_tokens": len(demo.ids)})
        item = {"dataset": ds, "n_per_arm": len(base), "shared_code_graph_and_nolabel_demo_differences": differences,
                "graph_or_demo_over_1500": violations}
        report.append(item)
        print(ds, "shared component differences", len(differences), "budget violations", len(violations), flush=True)
    (Path(__file__).parent / "completed_component_audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
