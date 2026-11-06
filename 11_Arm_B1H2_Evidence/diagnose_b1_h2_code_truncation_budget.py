"""Quantify whether source-complete B1-H2 target code fits the registered total context."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARM = ROOT / "11_Arm_B1H2_Evidence"
RUNS = ROOT / "Runs-management"
TOKENIZER = ARM / "tokenizer_cache_v6/models--Qwen--Qwen3-Coder-30B-A3B-Instruct/snapshots/b2cff646eb4bb1d68355c01b18ae02e7cf42d120"
V6 = ARM / "validation_h2_cluster_v6_joern_error_20261105"
SOURCE = ROOT / "01_Author_Baseline_Unified/output/local_full/bundles_recovered_joern_final_20261031"
OUT = ARM / "audit/b1_h2_code_truncation_budget_20261105.json"


def rows(path: Path):
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def main() -> None:
    sys.path.insert(0, str(ROOT / "01_Author_Baseline_Unified/diagnostic_kit/src"))
    from grace_diag.probes import split_blocks
    from transformers import PreTrainedTokenizerFast

    tok = PreTrainedTokenizerFast.from_pretrained(TOKENIZER, local_files_only=True)
    reports = {}
    all_items = []
    for dataset in ("devign", "reveal"):
        prompt_path = V6 / dataset / "validation/B1-H2/42/prompts.jsonl"
        source_path = SOURCE / dataset / "validation/specs.jsonl"
        prompts = {row["id"]: row for row in rows(prompt_path)}
        sources = {row["id"]: row for row in rows(source_path)}
        audit_path = prompt_path.parent / "audit_rows.csv"
        with audit_path.open(encoding="utf-8-sig", newline="") as stream:
            truncated_ids = [row["id"] for row in csv.DictReader(stream) if row["code_truncated"].lower() == "true"]
        items = []
        for uid in truncated_ids:
            row, source = prompts[uid], sources[uid]
            prompt = row["prompt"]
            blocks = split_blocks(prompt)
            complete_code = source["query_code"].strip()
            code_tokens = len(tok.encode(complete_code, add_special_tokens=False))
            expanded = "\n\n".join((
                blocks["role"], complete_code, blocks["question"],
                *([blocks["graph"]] if blocks["graph"] else []),
                *([blocks["demo"]] if blocks["demo"] else []), blocks["answer"],
            ))
            chat = tok.apply_chat_template([{"role": "user", "content": expanded}], tokenize=True, add_generation_prompt=True)
            full_total = len(chat["input_ids"])
            item = {
                "id": uid,
                "current_code_tokens": int(row["evidence"]["tokens"]["code"]),
                "source_complete_code_tokens": code_tokens,
                "current_total_tokens": int(row["evidence"]["tokens"]["total"]),
                "source_complete_chat_tokens": full_total,
                "full_target_fits_3000_code_cap": code_tokens <= 3000,
                "full_target_fits_8192_context_plus_reserve": full_total + 64 <= 8192,
            }
            items.append(item)
            all_items.append(item)
        reports[dataset] = {
            "truncated_rows": len(items),
            "full_code_token_min": min((x["source_complete_code_tokens"] for x in items), default=None),
            "full_code_token_median": sorted(x["source_complete_code_tokens"] for x in items)[len(items)//2] if items else None,
            "full_code_token_max": max((x["source_complete_code_tokens"] for x in items), default=None),
            "full_code_fits_registered_total_context": sum(x["full_target_fits_8192_context_plus_reserve"] for x in items),
            "examples": items,
        }
    out = {
        "schema": "b1_h2_code_truncation_budget_diagnostic_v1",
        "tokenizer_revision": "b2cff646eb4bb1d68355c01b18ae02e7cf42d120",
        "scope": "Validation B1-H2 rows flagged code_truncated; replaces capped target snippet with full frozen source query_code, holding graph/question/template constant. No prompts changed and no inference performed.",
        "registered_budget": {"target_code": 3000, "graph": 1500, "total": 8192, "reserve": 64},
        "all_datasets": {
            "truncated_rows": len(all_items),
            "full_code_fits_3000": sum(x["full_target_fits_3000_code_cap"] for x in all_items),
            "full_code_fits_total_context": sum(x["full_target_fits_8192_context_plus_reserve"] for x in all_items),
        },
        "datasets": reports,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(OUT), **out["all_datasets"], "datasets": {k: {key: v for key, v in val.items() if key != "examples"} for k, val in reports.items()}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
