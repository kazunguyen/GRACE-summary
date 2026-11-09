"""Synthetic probes for branches not reached by the empty-pool release.

No real human reviews or source claims. All files are written under probe_sandbox;
production releases are read-only. Uses the actual reviewed functions/render block.
"""
import ast
from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import re
import runpy
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SANDBOX = OUT / "probe_sandbox"
SANDBOX.mkdir(exist_ok=False)
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "01_Author_Baseline_Unified/diagnostic_kit/src")]
import b3_step6_packet_tool as tool
from grace_diag.amended_b3 import VerifiedPairSelector, payload_hash, validate_pair
from grace_diag.probes import QUESTION, split_blocks
from grace_diag.token_budget import TokenCounter

fixture = runpy.run_path(str(ROOT / "tests/test_amended_b3.py"))["fixture_pair"]
pair, bank = fixture("case_probe")
candidate = {k: deepcopy(v) for k, v in pair.items() if k != "reviews"}
validate_pair(candidate, bank, "devign", require_reviews=False)


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def jsonl(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), encoding="utf-8")


v_id, p_id = candidate["vulnerable_id"], candidate["patched_id"]
cm = {"case_id": "case_probe", "project": "SYNTHETIC_PROJECT", "function_hint": "copy_item",
      "vulnerable_donor": {"id": v_id, "commit_id": candidate["source"]["parent_commit"]},
      "patched_candidate_donor": {"id": p_id, "commit_id": candidate["source"]["fix_commit"]},
      "source_investigation": {"is_direct_parent_edge": True,
          "vulnerable_parent_shas": [], "patched_parent_shas": [candidate["source"]["parent_commit"]],
          "vulnerable_changed_files": ["fixture.c"], "patched_changed_files": ["fixture.c"],
          "shared_files": ["fixture.c"], "vulnerable_commit_msg": "SYNTHETIC TEST ONLY",
          "patched_commit_msg": "SYNTHETIC TEST ONLY"}}
packet_release = SANDBOX / "packet_generation"
dump(packet_release / "source_archive/devign/case_probe/case_manifest.json", cm)
packets = tool.generate_review_packets(packet_release)
packet = packets[0]
triage_rows = tool.run_automated_technical_triage(packet_release)
triage = {r["case_id"]: r for r in triage_rows}


def review(name, bound_hash, decision="approve"):
    return {"case_id": "case_probe", "reviewer": name,
            "reviewed_at": "2026-11-08T06:00:00+00:00", "payload_sha256": bound_hash,
            "same_function_verified": True, "security_fix_verified": True,
            "source_revisions_verified": True, "explanation_supported": True,
            "decision": decision, "comments": "SYNTHETIC SOFTWARE PROBE, NOT HUMAN REVIEW"}


known = {packet["case_id"]: packet}
packet_reviews = [review("SYNTHETIC-REVIEWER-1", packet["payload_sha256"]),
                  review("SYNTHETIC-REVIEWER-2", packet["payload_sha256"])]
forms = [tool.validate_review_form(r, known, triage) for r in packet_reviews]
stdout = io.StringIO()
with redirect_stdout(stdout):
    admitted = tool.determine_eligible_pairs(packet_reviews, known, triage, [candidate], {"devign": bank})
result = {"fixture_scope": "SYNTHETIC_SOFTWARE_ONLY_NO_REAL_PAIRS_OR_HUMAN_REVIEWS",
    "generated_packet_to_candidate_binding": {
        "candidate_valid_without_reviews": True, "triage_status": triage["case_probe"]["status"],
        "generated_packet_hash": packet["payload_sha256"], "full_pair_payload_hash": payload_hash(candidate),
        "both_forms_pass_ingestion": all(ok for ok, _ in forms),
        "admitted_pairs": len(admitted["devign"]), "validator_message": stdout.getvalue().strip()}}

# Separate the binding bug from the review-consensus bug using a control packet
# bound to the full pair, as the submitted unit test does.
correct_hash = payload_hash(candidate)
control_known = {"case_probe": {"case_id": "case_probe", "payload_sha256": correct_hash}}
conflicting = [review("SYNTHETIC-REVIEWER-1", correct_hash),
               review("SYNTHETIC-REVIEWER-2", correct_hash),
               review("SYNTHETIC-REVIEWER-3", correct_hash, "reject")]
assert all(tool.validate_review_form(r, control_known, triage)[0] for r in conflicting)
with redirect_stdout(io.StringIO()):
    admitted_conflict = tool.determine_eligible_pairs(conflicting, control_known, triage, [candidate], {"devign": bank})
result["unresolved_review_disagreement"] = {"approve_reviews": 2, "reject_reviews": 1,
    "admitted_pairs_despite_reject": len(admitted_conflict["devign"])}
placeholder = review("SYNTHETIC-REVIEWER-1", correct_hash)
placeholder["reviewed_at"] = "YYYY-MM-DDTHH:MM:SSZ"
result["placeholder_timestamp_accepted"] = tool.validate_review_form(placeholder, control_known, triage)[0]

# Exercise the actual Step 8 render-and-audit block without running its full
# release builder or changing a production pool. No assertions are replaced.
tree = ast.parse((ROOT / "scripts/b3_step8_validation_census_builder.py").read_text(encoding="utf-8"))
render_try = next(n for n in ast.walk(tree) if isinstance(n, ast.Try)
    and any(isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute)
            and x.func.attr == "render_family" for x in ast.walk(n)))
tokenizer = ROOT / "11_Arm_B1H2_Evidence/tokenizer_cache_v6/models--Qwen--Qwen3-Coder-30B-A3B-Instruct/snapshots/b2cff646eb4bb1d68355c01b18ae02e7cf42d120"
counter = TokenCounter(str(tokenizer))
target = {"id": "SYNTHETIC-TARGET", "query_code": "int target_fn(void) { return 0; }", "nodes": [], "edges": []}
ns = {"selector": VerifiedPairSelector([pair], bank, "devign"), "counter": counter,
      "clean_target": target, "record": {}, "re": re}
exec(compile(ast.Module(body=[render_try], type_ignores=[]), "actual_step8_render_block", "exec"), ns)
record = ns["record"]
blocks = split_blocks(record["prompt"])
result["actual_step8_render_audit_block"] = {
    "code_block_is_expected_target": blocks["code"] == target["query_code"],
    "official_question_is_in_prompt": QUESTION in record["prompt"],
    "literal_Question_colon_is_in_prompt": "Question:" in record["prompt"],
    "record_status": record["status"], "prompt_evaluation_status": record["prompt_evaluation_status"],
    "figure6_order_compliant": record["figure6_order_compliant"],
    "target_label_in_prompt": record["target_label_in_prompt"]}

# File-preservation probe on a synthetic mini-bank and synthetic existing pool.
# Temporarily relocate only the module's ROOT used for its disk reads.
storage_release = SANDBOX / "storage_release"
fake_root = SANDBOX / "synthetic_repository"
for ds in ("devign", "reveal"):
    records = list(bank.values()) if ds == "devign" else []
    freeze = fake_root / "01_Author_Baseline_Unified/output/research_freeze_20261101" / ds
    jsonl(freeze / "train_raw.jsonl", records)
    jsonl(freeze / "train_manifest.jsonl", [{"id": r["id"], "keep_in_bank": True} for r in records])
pool_path = storage_release / "pools/eligible_pairs.devign.jsonl"
jsonl(pool_path, [pair])
dump(storage_release / "reviews/submitted/malformed.json", {})
before_bytes = pool_path.read_bytes()
old_root = tool.ROOT
tool.ROOT = fake_root
try:
    with redirect_stdout(io.StringIO()):
        tool.ingest_human_reviews_and_seal_pools(storage_release)
finally:
    tool.ROOT = old_root
result["existing_pool_with_invalid_submitted_form"] = {"before_bytes": len(before_bytes),
    "after_bytes": pool_path.stat().st_size, "existing_pool_preserved": pool_path.read_bytes() == before_bytes}

# Check whether the submitted remediation audit's own overall Boolean gates
# the preservation/input checks that it computes.
audit_tree = ast.parse((ROOT / "Runs-management/b3_verified_patch_v1/remediation_audit_20261108/audit_remediated_release.py").read_text(encoding="utf-8"))
verdict_assignment = next(n for n in ast.walk(audit_tree) if isinstance(n, ast.Assign)
    and any(isinstance(t, ast.Name) and t.id == "all_remediations_passed" for t in n.targets))
mock_result = {"finding_f01_remediation": {"status": "PASS_CLEAN_SEPARATION"},
    "finding_f02_remediation": {"status": "PASS_BOUNDED_AND_COMPLETE_PROVENANCE"},
    "finding_f03_remediation": {"status": "PASS_TRUTHFUL_CENSUS_EVALUATION"},
    "finding_f04_remediation": {"status": "PASS_REAL_SOURCE_ONLY"},
    "finding_f05_remediation": {"status": "PASS_FACTUAL_UNRESOLVED_PROVENANCE"},
    "finding_f06_and_f07_remediation": {"status": "PASS_GATES_AND_GOVERNANCE_HONEST"},
    "prior_v1_release_preservation": {"intact": False},
    "freeze_and_inputs": {"module_hashes_pass": False, "scripts_hashes_pass": False}}
scope = {"all_seals_pass": True, "result": mock_result}
exec(compile(ast.Module(body=[verdict_assignment], type_ignores=[]), "actual_remediation_overall_gate", "exec"), scope)
result["remediation_overall_gate_probe"] = {"mock_preservation_and_source_hashes_pass": False,
    "all_remediations_passed_result": scope["all_remediations_passed"]}

(OUT / "positive_path_probes.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
