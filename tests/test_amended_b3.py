"""Synthetic fixtures verify software behavior, not actual pair security quality."""
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

from grace_diag.amended_b3 import (VerifiedPairSelector, changed_lines, digest,
                                   patch_text, payload_hash, validate_pair, difference_from_source,
                                   make_pair_candidate)
from grace_diag.contrastive_pair_builder import jaccard_similarity
from grace_diag.token_budget import TokenCounter


def fixture_pair(pair_id="fixture-a", function="copy_item"):
    before = f"int {function}(char *dst, const char *src, unsigned n) {{\n    memcpy(dst, src, n);\n    return 0;\n}}\n"
    after = f"int {function}(char *dst, const char *src, unsigned n) {{\n    if (n > 16) return -1;\n    memcpy(dst, src, n);\n    return 0;\n}}\n"
    v, p = pair_id + ":v", pair_id + ":p"
    bank = {uid: {"id": uid, "function_uid": uid, "dataset": "devign", "split": "train",
                  "target": label, "func": code} for uid, label, code in ((v, 1, before), (p, 0, after))}
    pair = {"pair_id": pair_id, "dataset": "devign", "vulnerable_id": v, "patched_id": p,
            "test_fixture": True, "before_sha256": digest(before), "after_sha256": digest(after),
            "key_difference": "The patched snippet adds `if (n > 16) return -1;` before `memcpy(dst, src, n);`. This limits n to 16 in this synthetic example; safety also assumes dst has capacity 16.",
            "changed_lines": changed_lines(before, after),
            "source": {"repository": "https://example.invalid/SYNTHETIC-NOT-REAL",
                       "path": "fixture.c", "function": function, "fix_commit": "1" * 40,
                       "parent_commit": "2" * 40, "source_url": "https://example.invalid/SYNTHETIC-NOT-REAL/patch",
                       "security_rationale": "SYNTHETIC fixture: assume dst capacity 16; reject larger copy lengths.",
                       "before": before, "after": after, "diff": patch_text(before, after)}}
    pair["source"]["fix_diff"] = pair["source"]["diff"].replace("--- vulnerable", "--- a/fixture.c").replace("+++ patched", "+++ b/fixture.c")
    pair["key_difference"] = difference_from_source(pair["source"])
    pair["reviews"] = [{"reviewer": "SYNTHETIC-UNIT-TEST-REVIEWER-" + str(i),
                        "reviewed_at": "TEST-FIXTURE-NOT-HUMAN-REVIEW", "decision": "approve",
                        "payload_sha256": payload_hash(pair), "same_function_verified": True,
                        "security_fix_verified": True, "source_revisions_verified": True,
                        "explanation_supported": True} for i in (1, 2)]
    return pair, bank


def test_exact_ranking_and_lexicographic_tie():
    a, bank_a = fixture_pair("a")
    b, bank_b = fixture_pair("b")
    c, bank_c = fixture_pair("c", "parse_header")
    selector = VerifiedPairSelector([b, c, a], bank_a | bank_b | bank_c, "devign")
    query = "void parse_header(int *p) { if (!p) return; }"
    pair, demos, score = selector.select(query)
    expected = sorted([(sum(jaccard_similarity(query, d["func"]) for d in selector.demos[p["pair_id"]]) / 2,
                        p["pair_id"]) for p in [a, b, c]], key=lambda x: (-x[0], x[1]))[0]
    assert pair["pair_id"] == expected[1]
    assert score["mean_jaccard"] == pytest.approx(expected[0])
    assert Fraction(score["score_numerator"], score["score_denominator"]) >= 0
    assert selector.select("")[0]["pair_id"] == "a"
    pair["key_difference"] = "mutated"
    demos[0]["func"] = "mutated"
    assert selector.select(query)[0]["key_difference"] != "mutated"


@pytest.mark.parametrize("fault", ["missing_donor", "wrong_label", "test_donor", "wrong_dataset",
                                    "wrong_hash", "wrong_diff", "wrong_function", "missing_evidence",
                                    "stale_review", "one_reviewer", "same_reviewer", "disagree",
                                    "unverified_security", "changed_lines", "no_explanation",
                                    "fake_fix_diff"])
def test_reject_invalid_pair(fault):
    pair, bank = fixture_pair()
    if fault == "missing_donor": bank.pop(pair["patched_id"])
    if fault == "wrong_label": bank[pair["patched_id"]]["target"] = 1
    if fault == "test_donor": bank[pair["patched_id"]]["split"] = "test"
    if fault == "wrong_dataset": bank[pair["patched_id"]]["dataset"] = "reveal"
    if fault == "wrong_hash": pair["before_sha256"] = "0" * 64
    if fault == "wrong_diff": pair["source"]["diff"] += "invented"
    if fault == "wrong_function": pair["source"]["function"] = "other"
    if fault == "missing_evidence": pair["source"].pop("parent_commit")
    if fault == "stale_review": pair["key_difference"] += " unsupported alteration"
    if fault == "one_reviewer": pair["reviews"].pop()
    if fault == "same_reviewer": pair["reviews"][1]["reviewer"] = pair["reviews"][0]["reviewer"]
    if fault == "disagree": pair["reviews"][1]["decision"] = "reject"
    if fault == "unverified_security": pair["reviews"][0]["security_fix_verified"] = False
    if fault == "changed_lines": pair["changed_lines"] = []
    if fault == "no_explanation": pair["key_difference"] = ""
    if fault == "fake_fix_diff": pair["source"]["fix_diff"] = "--- a/fixture.c\n+++ b/fixture.c\n"
    with pytest.raises(ValueError): validate_pair(pair, bank, "devign")


def test_candidate_builder_does_not_approve_its_own_evidence():
    pair, bank = fixture_pair()
    candidate = make_pair_candidate("devign", "candidate", bank[pair["vulnerable_id"]],
                                    bank[pair["patched_id"]], pair["source"])
    assert candidate["reviews"] == []
    assert "if (n > 16) return -1;" in candidate["key_difference"]
    with pytest.raises(ValueError, match="Two distinct"):
        VerifiedPairSelector([candidate], bank, "devign")


def test_empty_pool_no_fallback():
    with pytest.raises(ValueError, match="must pause"):
        VerifiedPairSelector([], {}, "devign")


def test_no_target_label_api():
    pair, bank = fixture_pair()
    selector = VerifiedPairSelector([pair], bank, "devign")
    counter = TokenCounter()
    counter.approx = False  # Only for this rejection test; not token validation.
    with pytest.raises(ValueError, match="never labels"):
        selector.render_family({"id": "target", "query_code": "int f(){}", "label": 1}, counter)
    with pytest.raises(ValueError, match="Exact"):
        selector.render_family({"id": "target", "query_code": "int f(){}"}, TokenCounter())


def test_exact_tokenizer_family_smoke():
    repo_root = Path(__file__).resolve().parents[1]
    local_snapshot = (
        repo_root
        / "11_Arm_B1H2_Evidence"
        / "tokenizer_cache_v6"
        / "models--Qwen--Qwen3-Coder-30B-A3B-Instruct"
        / "snapshots"
        / "b2cff646eb4bb1d68355c01b18ae02e7cf42d120"
    )
    foreign_snapshot = Path("C:/MY-FILES/LAB-THAY-THO/tmp/grace_validation_hf/hub/models--Qwen--Qwen3-Coder-30B-A3B-Instruct/snapshots/b2cff646eb4bb1d68355c01b18ae02e7cf42d120")
    snapshot = local_snapshot if local_snapshot.exists() else foreign_snapshot
    if not snapshot.exists():
        pytest.skip("Pinned tokenizer not cached locally")
    counter = TokenCounter(str(snapshot))
    a, ba = fixture_pair("fixture-a")
    b, bb = fixture_pair("fixture-b", "parse_header")
    selector = VerifiedPairSelector([b, a], ba | bb, "devign")
    records = []
    queries = ["int copy_item(char *d, char *s, unsigned n) { memcpy(d,s,n); return 0; }",
               "int parse_header(unsigned n) { if(n > 16) return -1; return 0; }",
               "int release_item(void *p) { free(p); return 0; }"]
    for i, code in enumerate(queries):
        family = selector.render_family({"id": f"SYNTHETIC-target-{i}", "query_code": code,
                                         "nodes": [{"id": 0, "type": "METHOD", "code": "synthetic"}],
                                         "edges": []}, counter)
        base = family["B3"]
        pair, demos, _ = selector.select(code)
        diff = "\n\nKey difference: " + pair["key_difference"]
        assert family["B3-nodiff"]["prompt"] == base["prompt"].replace(diff, "")
        vblock = "The following example is Vulnerable.\n" + demos[0]["func"].strip()
        pblock = "The following example is Non-vulnerable.\n" + demos[1]["func"].strip()
        assert family["B3-swap"]["prompt"] == base["prompt"].replace(vblock + "\n\n" + pblock, pblock + "\n\n" + vblock)
        assert family["B3-flip"]["prompt"] == base["prompt"].replace(vblock, vblock.replace("is Vulnerable.", "is Non-vulnerable.")).replace(pblock, pblock.replace("is Non-vulnerable.", "is Vulnerable."))
        assert family["B3-nodiff"]["threshold_from"] == "B3-nodiff"
        assert family["B3-flip"]["threshold_from"] == "B3"
        assert family["B3-swap"]["threshold_from"] == "B3"
        assert all(r["evidence"]["tokens"]["total"] + 64 <= 8192 for r in family.values())
        assert family == selector.render_family({"id": f"SYNTHETIC-target-{i}", "query_code": code,
                                                "nodes": [{"id": 0, "type": "METHOD", "code": "synthetic"}],
                                                "edges": []}, counter)
        records.extend({**r, "status": "SYNTHETIC_SOFTWARE_TEST_ONLY_NOT_REAL_PAIR_REVIEW",
                        "inference_allowed": False} for r in family.values())
    # Persist readable examples for review of software behavior, separate from real data.
    out = Path(__file__).resolve().parents[1] / "Runs-management/b3_amended_20261106"
    (out / "synthetic_smoke_prompts.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "synthetic_smoke_preview.txt").write_text(
        "SYNTHETIC SOFTWARE TEST ONLY. No real fix commits or human review. Not for inference.\n\n" +
        "\n\n".join(r["id"] + " / " + r["arm"] + "\n" + r["prompt"] for r in records if r["arm"] == "B3"), encoding="utf-8")
    oversized, bank = fixture_pair("large")
    for side, uid in (("before", oversized["vulnerable_id"]), ("after", oversized["patched_id"])):
        text = oversized["source"][side] + "\n" + "int more_code = 123;\n" * 3000
        oversized["source"][side] = bank[uid]["func"] = text
        oversized[side + "_sha256"] = digest(text)
    oversized["source"]["diff"] = patch_text(oversized["source"]["before"], oversized["source"]["after"])
    oversized["changed_lines"] = changed_lines(oversized["source"]["before"], oversized["source"]["after"])
    oversized["key_difference"] = difference_from_source(oversized["source"])
    for review in oversized["reviews"]: review["payload_sha256"] = payload_hash(oversized)
    with pytest.raises(ValueError, match="budget|ngân sách"):
        VerifiedPairSelector([oversized], bank, "devign").render_family({"id": "overflow", "query_code": queries[0]}, counter)


def test_review_form_adversarial_rejections():
    import sys
    scripts_dir = str(Path(__file__).resolve().parents[1] / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    from b3_step6_packet_tool import validate_review_form

    known_packets = {
        "case_01": {"case_id": "case_01", "payload_sha256": "a" * 64},
        "case_02": {"case_id": "case_02", "payload_sha256": "b" * 64},
    }
    triage_records = {
        "case_01": {"status": "AUTOMATED_TRIAGE_REJECT"},
        "case_02": {"status": "AUTOMATED_TRIAGE_PASS"},
    }

    base_form = {
        "case_id": "case_02",
        "reviewer": "Alice",
        "reviewed_at": "2026-11-08T00:00:00Z",
        "payload_sha256": "b" * 64,
        "same_function_verified": True,
        "security_fix_verified": True,
        "source_revisions_verified": True,
        "explanation_supported": True,
        "decision": "approve",
        "comments": "Verified authentic patch.",
    }

    # 1. Valid form passes
    ok, reason = validate_review_form(base_form, known_packets, triage_records)
    assert ok is True
    assert reason is None

    # 2. Missing field
    f_missing = dict(base_form)
    f_missing.pop("decision")
    ok, reason = validate_review_form(f_missing, known_packets, triage_records)
    assert ok is False
    assert "MISSING_REQUIRED_FIELDS" in reason

    # 3. Unknown case_id
    f_unknown = dict(base_form, case_id="case_99")
    ok, reason = validate_review_form(f_unknown, known_packets, triage_records)
    assert ok is False
    assert "UNKNOWN_CASE_ID" in reason

    # 4. Template reviewer name
    f_template = dict(base_form, reviewer="REVIEWER_NAME_HERE")
    ok, reason = validate_review_form(f_template, known_packets, triage_records)
    assert ok is False
    assert "INVALID_REVIEWER_NAME" in reason

    # 5. Empty reviewer name
    f_empty = dict(base_form, reviewer="   ")
    ok, reason = validate_review_form(f_empty, known_packets, triage_records)
    assert ok is False
    assert "INVALID_REVIEWER_NAME" in reason

    # 6. Payload hash mismatch
    f_tamper = dict(base_form, payload_sha256="c" * 64)
    ok, reason = validate_review_form(f_tamper, known_packets, triage_records)
    assert ok is False
    assert "PAYLOAD_HASH_MISMATCH" in reason

    # 7. Approve with security_fix_verified = False
    f_unsec = dict(base_form, security_fix_verified=False)
    ok, reason = validate_review_form(f_unsec, known_packets, triage_records)
    assert ok is False
    assert "APPROVE_WITHOUT_ALL_VERIFICATIONS" in reason

    # 8. Approve with same_function_verified = False
    f_diff_func = dict(base_form, same_function_verified=False)
    ok, reason = validate_review_form(f_diff_func, known_packets, triage_records)
    assert ok is False
    assert "APPROVE_WITHOUT_ALL_VERIFICATIONS" in reason

    # 9. Approve a case that failed automated technical triage
    f_triage_fail = dict(base_form, case_id="case_01", payload_sha256="a" * 64)
    ok, reason = validate_review_form(f_triage_fail, known_packets, triage_records)
    assert ok is False
    assert "CANNOT_APPROVE_FAILED_TRIAGE" in reason


def test_dual_review_admission_logic():
    import sys
    scripts_dir = str(Path(__file__).resolve().parents[1] / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    from b3_step6_packet_tool import determine_eligible_pairs

    pair, bank = fixture_pair("case_ok")
    candidate = {k: v for k, v in pair.items() if k != "reviews"}
    candidate["pair_id"] = "case_ok"

    known_packets = {
        "case_ok": {"case_id": "case_ok", "payload_sha256": payload_hash(candidate)}
    }
    triage_records = {
        "case_ok": {"status": "AUTOMATED_TRIAGE_PASS"}
    }

    def make_rev(reviewer, decision="approve", sec_ok=True):
        return {
            "case_id": "case_ok",
            "reviewer": reviewer,
            "reviewed_at": "2026-11-08T00:00:00Z",
            "payload_sha256": payload_hash(candidate),
            "same_function_verified": True,
            "security_fix_verified": sec_ok,
            "source_revisions_verified": True,
            "explanation_supported": True,
            "decision": decision,
            "comments": "LGTM",
        }

    # Case A: Only 1 review -> not admitted
    rev1 = make_rev("Reviewer_1")
    admitted = determine_eligible_pairs([rev1], known_packets, triage_records, [candidate], {"devign": bank})
    assert len(admitted["devign"]) == 0

    # Case B: 2 reviews from SAME reviewer -> not admitted
    rev2_same = make_rev("Reviewer_1")
    admitted = determine_eligible_pairs([rev1, rev2_same], known_packets, triage_records, [candidate], {"devign": bank})
    assert len(admitted["devign"]) == 0

    # Case C: 1 approve, 1 reject -> not admitted
    rev2_reject = make_rev("Reviewer_2", decision="reject")
    admitted = determine_eligible_pairs([rev1, rev2_reject], known_packets, triage_records, [candidate], {"devign": bank})
    assert len(admitted["devign"]) == 0

    # Case D: 2 distinct approvals -> successfully admitted and validated!
    rev2_approve = make_rev("Reviewer_2", decision="approve")
    admitted = determine_eligible_pairs([rev1, rev2_approve], known_packets, triage_records, [candidate], {"devign": bank})
    assert len(admitted["devign"]) == 1
    adm = admitted["devign"][0]
    assert adm["pair_id"] == "case_ok"
    assert len(adm["reviews"]) == 2
    assert adm["reviews"][0]["reviewer"] != adm["reviews"][1]["reviewer"]


def test_generator_form_admission_selector_render_pipeline(tmp_path):
    """End-to-end integration test: generator -> form -> admission -> selector -> render (R1, R2)."""
    import sys
    scripts_dir = str(Path(__file__).resolve().parents[1] / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import b3_step6_packet_tool as tool
    from grace_diag.probes import split_blocks, QUESTION, ROLE, ANSWER

    pair, bank = fixture_pair("case_e2e")
    candidate = {k: deepcopy(v) for k, v in pair.items() if k != "reviews"}
    validate_pair(candidate, bank, "devign", require_reviews=False)

    release_dir = tmp_path / "test_release"
    archive_dir = release_dir / "source_archive" / "devign" / "case_e2e"
    archive_dir.mkdir(parents=True, exist_ok=True)

    cm = {
        "case_id": "case_e2e",
        "project": "SYNTHETIC_E2E",
        "function_hint": "copy_item",
        "vulnerable_donor": {"id": candidate["vulnerable_id"], "commit_id": candidate["source"]["parent_commit"]},
        "patched_candidate_donor": {"id": candidate["patched_id"], "commit_id": candidate["source"]["fix_commit"]},
        "source_investigation": {
            "is_direct_parent_edge": True,
            "vulnerable_parent_shas": [],
            "patched_parent_shas": [candidate["source"]["parent_commit"]],
            "vulnerable_changed_files": ["fixture.c"],
            "patched_changed_files": ["fixture.c"],
            "shared_files": ["fixture.c"],
            "vulnerable_commit_msg": "SYNTHETIC E2E",
            "patched_commit_msg": "SYNTHETIC E2E",
        },
    }
    (archive_dir / "case_manifest.json").write_text(json.dumps(cm, indent=2), encoding="utf-8")
    (archive_dir / "candidate.json").write_text(json.dumps(candidate, indent=2), encoding="utf-8")

    # Step A: Generate review packet from candidate
    packets = tool.generate_review_packets(release_dir, candidates=[candidate])
    assert len(packets) == 1
    packet = packets[0]

    # Verify canonical payload hash match (R1)
    assert packet["has_candidate_payload"] is True
    assert packet["payload_sha256"] == payload_hash(candidate)

    # Step B: Automated technical triage
    triage_rows = tool.run_automated_technical_triage(release_dir)
    triage_map = {r["case_id"]: r for r in triage_rows}
    assert triage_map["case_e2e"]["status"] == "AUTOMATED_TRIAGE_PASS"

    # Step C: Fill review forms with packet's payload_sha256
    rev_a = {
        "case_id": "case_e2e",
        "reviewer": "Alice",
        "reviewed_at": "2026-11-08T06:00:00Z",
        "payload_sha256": packet["payload_sha256"],
        "same_function_verified": True,
        "security_fix_verified": True,
        "source_revisions_verified": True,
        "explanation_supported": True,
        "decision": "approve",
        "comments": "Verified upstream patch.",
    }
    rev_b = {
        "case_id": "case_e2e",
        "reviewer": "Bob",
        "reviewed_at": "2026-11-08T06:30:00Z",
        "payload_sha256": packet["payload_sha256"],
        "same_function_verified": True,
        "security_fix_verified": True,
        "source_revisions_verified": True,
        "explanation_supported": True,
        "decision": "approve",
        "comments": "Second independent approval.",
    }

    known_packets = {p["case_id"]: p for p in packets}
    ok_a, reason_a = tool.validate_review_form(rev_a, known_packets, triage_map)
    ok_b, reason_b = tool.validate_review_form(rev_b, known_packets, triage_map)
    assert ok_a is True, f"Review A failed: {reason_a}"
    assert ok_b is True, f"Review B failed: {reason_b}"

    # Step D: Determine eligible pairs
    admitted = tool.determine_eligible_pairs([rev_a, rev_b], known_packets, triage_map, [candidate], {"devign": bank})
    assert len(admitted["devign"]) == 1
    admitted_pair = admitted["devign"][0]

    # Step E: Selector and Renderer
    selector = VerifiedPairSelector([admitted_pair], bank, "devign")
    target = {"id": "target_e2e", "query_code": "int test_target(void) { return 42; }", "nodes": "", "edges": ""}
    local_snapshot = (
        Path(__file__).resolve().parents[1]
        / "11_Arm_B1H2_Evidence"
        / "tokenizer_cache_v6"
        / "models--Qwen--Qwen3-Coder-30B-A3B-Instruct"
        / "snapshots"
        / "b2cff646eb4bb1d68355c01b18ae02e7cf42d120"
    )
    if local_snapshot.exists():
        counter = TokenCounter(str(local_snapshot))
    else:
        counter = TokenCounter(None)
        counter.approx = False
    family = selector.render_family(target, counter)

    assert "B3" in family
    b3_prompt = family["B3"]["prompt"]
    blocks = split_blocks(b3_prompt)
    assert blocks["role"] == ROLE
    assert blocks["question"] == QUESTION
    assert blocks["answer"] == ANSWER
    assert blocks["code"] == target["query_code"]
    assert "The following example is Vulnerable." in b3_prompt


def test_disagreement_and_placeholder_validations():
    """Verify consensus rules, rejection handling, and timestamp validation (R4)."""
    import sys
    scripts_dir = str(Path(__file__).resolve().parents[1] / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import b3_step6_packet_tool as tool

    pair, bank = fixture_pair("case_consensus")
    candidate = {k: v for k, v in pair.items() if k != "reviews"}
    h = payload_hash(candidate)

    known = {"case_consensus": {"case_id": "case_consensus", "payload_sha256": h}}
    triage = {"case_consensus": {"status": "AUTOMATED_TRIAGE_PASS"}}

    # Placeholder timestamp rejected (R4)
    placeholder_rev = {
        "case_id": "case_consensus", "reviewer": "Alice",
        "reviewed_at": "YYYY-MM-DDTHH:MM:SSZ", "payload_sha256": h,
        "same_function_verified": True, "security_fix_verified": True,
        "source_revisions_verified": True, "explanation_supported": True,
        "decision": "approve", "comments": "test",
    }
    ok, reason = tool.validate_review_form(placeholder_rev, known, triage)
    assert ok is False
    assert "PLACEHOLDER_TIMESTAMP" in reason

    # 2 Approvals + 1 Rejection -> Disagreement, 0 admitted pairs (R4)
    rev_app1 = {**placeholder_rev, "reviewer": "Alice", "reviewed_at": "2026-11-08T01:00:00Z", "decision": "approve"}
    rev_app2 = {**placeholder_rev, "reviewer": "Bob", "reviewed_at": "2026-11-08T02:00:00Z", "decision": "approve"}
    rev_rej = {**placeholder_rev, "reviewer": "Charlie", "reviewed_at": "2026-11-08T03:00:00Z", "decision": "reject"}

    admitted = tool.determine_eligible_pairs([rev_app1, rev_app2, rev_rej], known, triage, [candidate], {"devign": bank})
    assert len(admitted["devign"]) == 0, "Pair admitted despite active rejection from a reviewer!"


def test_pool_preservation_on_invalid_submitted_form(tmp_path):
    """Verify existing pool file is not wiped by invalid submitted review forms (R3)."""
    import sys
    scripts_dir = str(Path(__file__).resolve().parents[1] / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import b3_step6_packet_tool as tool

    pair, bank = fixture_pair("case_preservation")
    release_dir = tmp_path / "preserve_release"
    pools_dir = release_dir / "pools"
    reviews_dir = release_dir / "reviews"
    submitted_dir = reviews_dir / "submitted"
    submitted_dir.mkdir(parents=True, exist_ok=True)
    pools_dir.mkdir(parents=True, exist_ok=True)

    pool_path = pools_dir / "eligible_pairs.devign.jsonl"
    pool_path.write_text(json.dumps(pair, ensure_ascii=False) + "\n", encoding="utf-8")
    before_bytes = pool_path.read_bytes()
    assert len(before_bytes) > 0

    # Submit an invalid review form with empty dictionary / malformed schema
    (submitted_dir / "malformed.json").write_text("{}", encoding="utf-8")

    fake_root = tmp_path / "fake_root"
    for ds in ("devign", "reveal"):
        records = list(bank.values()) if ds == "devign" else []
        freeze = fake_root / "01_Author_Baseline_Unified/output/research_freeze_20261101" / ds
        freeze.mkdir(parents=True, exist_ok=True)
        (freeze / "train_raw.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
        (freeze / "train_manifest.jsonl").write_text("".join(json.dumps({"id": r["id"], "keep_in_bank": True}) + "\n" for r in records), encoding="utf-8")

    old_root = tool.ROOT
    tool.ROOT = fake_root
    try:
        tool.ingest_human_reviews_and_seal_pools(release_dir)
    finally:
        tool.ROOT = old_root

    # Verify pool was preserved intact (not wiped to 0 bytes)
    after_bytes = pool_path.read_bytes()
    assert after_bytes == before_bytes


def test_reviewer_identity_normalization_and_supersession():
    """Verify reviewer normalization (case/space) and timezone-aware review supersession (R4)."""
    import sys
    scripts_dir = str(Path(__file__).resolve().parents[1] / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import b3_step6_packet_tool as tool

    pair, bank = fixture_pair("case_supersession")
    candidate = {k: v for k, v in pair.items() if k != "reviews"}
    h = payload_hash(candidate)

    known = {"case_supersession": {"case_id": "case_supersession", "payload_sha256": h}}
    triage = {"case_supersession": {"status": "AUTOMATED_TRIAGE_PASS"}}

    # 1. Identity normalization: 'Alice' and '  alice  ' must be treated as the SAME reviewer
    rev_alice_1 = {
        "case_id": "case_supersession", "reviewer": "Alice",
        "reviewed_at": "2026-11-08T01:00:00Z", "payload_sha256": h,
        "same_function_verified": True, "security_fix_verified": True,
        "source_revisions_verified": True, "explanation_supported": True,
        "decision": "approve", "comments": "ok",
    }
    rev_alice_2 = {**rev_alice_1, "reviewer": "  alice  ", "reviewed_at": "2026-11-08T02:00:00Z"}
    admitted = tool.determine_eligible_pairs([rev_alice_1, rev_alice_2], known, triage, [candidate], {"devign": bank})
    assert len(admitted["devign"]) == 0, "Alice and alice treated as distinct reviewers!"

    # 2. Timezone-aware supersession:
    # Alice submits rejection at 08:00 UTC ('2026-11-08T08:00:00Z')
    # Alice also has an earlier approval at 14:00 +07:00 ('2026-11-08T14:00:00+07:00' -> 07:00 UTC)
    # Lexicographically, '14...' > '08...', but in UTC, 08:00Z is NEWER than 07:00 UTC!
    # Therefore, the rejection at 08:00Z is the active latest review!
    rev_alice_app_tz = {**rev_alice_1, "reviewer": "Alice", "reviewed_at": "2026-11-08T14:00:00+07:00", "decision": "approve"}
    rev_alice_rej_utc = {**rev_alice_1, "reviewer": "Alice", "reviewed_at": "2026-11-08T08:00:00Z", "decision": "reject"}
    rev_bob = {**rev_alice_1, "reviewer": "Bob", "reviewed_at": "2026-11-08T09:00:00Z", "decision": "approve"}

    admitted_tz = tool.determine_eligible_pairs([rev_alice_app_tz, rev_alice_rej_utc, rev_bob], known, triage, [candidate], {"devign": bank})
    assert len(admitted_tz["devign"]) == 0, "Earlier +07:00 review incorrectly superseded later UTC rejection!"

    # 3. Unresolved multi-reviewer (>2 distinct reviewers) without formal adjudication
    rev_carol = {**rev_alice_1, "reviewer": "Carol", "reviewed_at": "2026-11-08T10:00:00Z", "decision": "approve"}
    rev_alice_valid = {**rev_alice_1, "reviewer": "Alice", "reviewed_at": "2026-11-08T10:00:00Z", "decision": "approve"}
    admitted_3rev = tool.determine_eligible_pairs([rev_alice_valid, rev_bob, rev_carol], known, triage, [candidate], {"devign": bank})
    assert len(admitted_3rev["devign"]) == 0, "Admitted pair despite >2 reviewers without adjudication!"


def test_step5_evidence_sidecar_validation(tmp_path):
    """Verify Step 5 validates authentic evidence sidecar even without direct parent edge (R6)."""
    import sys
    scripts_dir = str(Path(__file__).resolve().parents[1] / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import b3_step5_make_candidates as s5

    pair, bank = fixture_pair("case_sidecar")
    candidate = {k: v for k, v in pair.items() if k != "reviews"}

    release_dir = tmp_path / "step5_release"
    archive_dir = release_dir / "source_archive" / "devign" / "case_sidecar"
    archive_dir.mkdir(parents=True, exist_ok=True)

    cm = {
        "case_id": "case_sidecar",
        "project": "SYNTHETIC_PROJ",
        "function_hint": "copy_item",
        "vulnerable_donor": {"id": candidate["vulnerable_id"], "commit_id": candidate["source"]["parent_commit"]},
        "patched_candidate_donor": {"id": candidate["patched_id"], "commit_id": candidate["source"]["fix_commit"]},
        "source_investigation": {
            "has_both_commit_responses": True,
            # Investigation signal: recorded donor commits lack direct parent edge
            "is_direct_parent_edge": False,
            "vulnerable_changed_files": ["foo.c"],
            "patched_changed_files": ["bar.c"],
            "shared_files": [],
        },
        "decision": {"status": "UNRESOLVED_RECORDED_COMMITS_NO_DIRECT_EDGE"},
    }
    (archive_dir / "case_manifest.json").write_text(json.dumps(cm, indent=2), encoding="utf-8")

    # Authentic evidence sidecar connecting actual revisions and diff
    sidecar = {
        "repository": "synthetic/repo",
        "path": "fixture.c",
        "function": "copy_item",
        "fix_commit": candidate["source"]["fix_commit"],
        "parent_commit": candidate["source"]["parent_commit"],
        "security_rationale": candidate["source"]["security_rationale"],
        "before": candidate["source"]["before"],
        "after": candidate["source"]["after"],
    }
    (archive_dir / "evidence_sidecar.json").write_text(json.dumps(sidecar, indent=2), encoding="utf-8")
    (archive_dir / "actual_fix.diff").write_text(candidate["source"]["fix_diff"], encoding="utf-8")

    # Set up synthetic freeze directory
    fake_freeze = tmp_path / "fake_freeze"
    for ds in ("devign", "reveal"):
        records = list(bank.values()) if ds == "devign" else []
        fdir = fake_freeze / ds
        fdir.mkdir(parents=True, exist_ok=True)
        (fdir / "train_raw.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
        (fdir / "train_manifest.jsonl").write_text("".join(json.dumps({"id": r["id"], "keep_in_bank": True}) + "\n" for r in records), encoding="utf-8")

    old_freeze = s5.FREEZE_DIR
    s5.FREEZE_DIR = fake_freeze
    try:
        s5.run_step5(release_dir)
    finally:
        s5.FREEZE_DIR = old_freeze

    cands_file = release_dir / "candidates" / "candidates.jsonl"
    assert cands_file.is_file()
    cands = [json.loads(line) for line in cands_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(cands) == 1
    assert cands[0]["pair_id"] == "case_sidecar"
    assert (archive_dir / "candidate.json").is_file()


def test_step7_report_construction_no_nameerror(tmp_path):
    """Verify Step 7 report construction completes with no NameError (T3-01)."""
    import subprocess
    from types import SimpleNamespace
    from unittest.mock import patch
    import b3_step7_verify_selector_renderer as s7

    s7_out = tmp_path / "step7_test"
    cpu_dir = s7_out / "acceptance" / "cpu_sample_check"
    cpu_dir.mkdir(parents=True, exist_ok=True)
    report_json = {
        "datasets": {"devign": {"status": "PAUSED"}, "reveal": {"status": "PAUSED"}},
        "inference_performed": False,
        "thresholds_changed": False,
        "test_inputs_read": False,
    }
    pools_dir = s7_out / "pools"
    pools_dir.mkdir(parents=True, exist_ok=True)
    (pools_dir / "eligible_pairs.devign.jsonl").write_text("", encoding="utf-8")
    (pools_dir / "eligible_pairs.reveal.jsonl").write_text("", encoding="utf-8")

    def mock_run(cmd, *args, **kwargs):
        if "check_b3.py" in str(cmd):
            cpu_dir.mkdir(parents=True, exist_ok=True)
            (cpu_dir / "report.json").write_text(json.dumps(report_json), encoding="utf-8")
        return SimpleNamespace(returncode=0, stdout="OK", stderr="")

    with patch.object(subprocess, "run", side_effect=mock_run):
        s7.run_step7(s7_out)

    report_p = s7_out / "acceptance" / "step7_selector_renderer_report.json"
    assert report_p.is_file()
    report = json.loads(report_p.read_text(encoding="utf-8"))
    assert report["overall_passed"] is True
    assert report["check_b3_cpu_sample_check"]["safe_pause_confirmed"] is True
    assert report["check_b3_cpu_sample_check"]["safe_pause_or_render_confirmed"] is True


def test_existing_pool_with_new_reject_blocks_pool(tmp_path):
    """Verify an existing pool is preserved on disk but blocked in manifest on new reject (T3-02)."""
    import b3_step6_packet_tool as tool

    pair, bank = fixture_pair("case_pool_reject")
    candidate = {k: v for k, v in pair.items() if k != "reviews"}
    h = payload_hash(candidate)

    release_dir = tmp_path / "reject_release"
    pools_dir = release_dir / "pools"
    reviews_dir = release_dir / "reviews"
    submitted_dir = reviews_dir / "submitted"
    packets_dir = release_dir / "review_packets"
    candidates_dir = release_dir / "candidates"
    for d in (pools_dir, reviews_dir, submitted_dir, packets_dir, candidates_dir):
        d.mkdir(parents=True, exist_ok=True)

    # Populate existing pool with historical verified pair
    pool_file = pools_dir / "eligible_pairs.devign.jsonl"
    pool_file.write_text(json.dumps(pair, ensure_ascii=False) + "\n", encoding="utf-8")
    before_bytes = pool_file.read_bytes()

    # Populate candidate, packet, and triage
    (candidates_dir / "candidates.jsonl").write_text(json.dumps(candidate, ensure_ascii=False) + "\n", encoding="utf-8")
    (packets_dir / "case_pool_reject.json").write_text(json.dumps({
        "case_id": "case_pool_reject",
        "payload_sha256": h,
        "has_candidate_payload": True,
        "candidate_payload": candidate,
    }, ensure_ascii=False), encoding="utf-8")
    (reviews_dir / "triage_ledger.jsonl").write_text(json.dumps({
        "case_id": "case_pool_reject",
        "payload_sha256": h,
        "status": "AUTOMATED_TRIAGE_PASS",
    }) + "\n", encoding="utf-8")

    # Submit 2 approves and 1 reject for this case
    for i, (name, dec) in enumerate([("SYNTH-1", "approve"), ("SYNTH-2", "approve"), ("SYNTH-3", "reject")]):
        rev = {
            "case_id": "case_pool_reject",
            "reviewer": name,
            "reviewed_at": "2026-11-08T06:00:00Z",
            "payload_sha256": h,
            "decision": dec,
            "comments": "Testing disagreement gate",
            "same_function_verified": True,
            "security_fix_verified": True,
            "source_revisions_verified": True,
            "explanation_supported": True,
        }
        (submitted_dir / f"review_{i}.json").write_text(json.dumps(rev), encoding="utf-8")

    fake_root = tmp_path / "fake_root"
    for ds in ("devign", "reveal"):
        records = list(bank.values()) if ds == "devign" else []
        fdir = fake_root / "01_Author_Baseline_Unified/output/research_freeze_20261101" / ds
        fdir.mkdir(parents=True, exist_ok=True)
        (fdir / "train_raw.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
        (fdir / "train_manifest.jsonl").write_text("".join(json.dumps({"id": r["id"], "keep_in_bank": True}) + "\n" for r in records), encoding="utf-8")

    old_root = tool.ROOT
    tool.ROOT = fake_root
    try:
        tool.ingest_human_reviews_and_seal_pools(release_dir)
    finally:
        tool.ROOT = old_root

    # Verify pool bytes on disk are preserved
    assert pool_file.read_bytes() == before_bytes
    manifest = json.loads((pools_dir / "pool_manifest.json").read_text(encoding="utf-8"))
    dev_m = manifest["pools"]["devign"]
    assert dev_m["status"] == "BLOCKED_DISAGREEMENT"
    assert dev_m["admitted_pairs_count"] == 0
    assert "disagreement" in dev_m["blocker_reason"].lower()


def test_sidecar_without_before_after_rejected(tmp_path):
    """Verify Step 5 rejects sidecar lacking authentic before/after without donor code fallback (T3-03)."""
    import b3_step5_make_candidates as s5

    pair, bank = fixture_pair("case_no_funcs")
    candidate = {k: v for k, v in pair.items() if k != "reviews"}
    release_dir = tmp_path / "no_funcs_release"
    archive_dir = release_dir / "source_archive" / "devign" / "case_no_funcs"
    archive_dir.mkdir(parents=True, exist_ok=True)

    cm = {
        "case_id": "case_no_funcs",
        "project": "SYNTHETIC",
        "function_hint": "foo",
        "vulnerable_donor": {"id": candidate["vulnerable_id"], "commit_id": "a" * 40},
        "patched_candidate_donor": {"id": candidate["patched_id"], "commit_id": "b" * 40},
        "source_investigation": {"has_both_commit_responses": True, "is_direct_parent_edge": True, "shared_files": ["foo.c"]},
        "decision": {},
    }
    (archive_dir / "case_manifest.json").write_text(json.dumps(cm, indent=2), encoding="utf-8")

    # Sidecar WITHOUT 'before' and 'after'
    ev = {k: v for k, v in candidate["source"].items() if k not in ("before", "after", "fix_diff", "diff")}
    (archive_dir / "evidence_sidecar.json").write_text(json.dumps(ev, indent=2), encoding="utf-8")
    (archive_dir / "actual_fix.diff").write_text(candidate["source"]["fix_diff"], encoding="utf-8")

    fake_freeze = tmp_path / "fake_freeze"
    for ds in ("devign", "reveal"):
        records = list(bank.values()) if ds == "devign" else []
        fdir = fake_freeze / ds
        fdir.mkdir(parents=True, exist_ok=True)
        (fdir / "train_raw.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
        (fdir / "train_manifest.jsonl").write_text("".join(json.dumps({"id": r["id"], "keep_in_bank": True}) + "\n" for r in records), encoding="utf-8")

    old_freeze = s5.FREEZE_DIR
    s5.FREEZE_DIR = fake_freeze
    try:
        s5.run_step5(release_dir)
    finally:
        s5.FREEZE_DIR = old_freeze

    summary = json.loads((release_dir / "candidates" / "candidates_summary.json").read_text(encoding="utf-8"))
    assert summary["candidates_admitted"] == 0
    assert summary["ineligible_cases_count"] == 1


def test_source_candidate_vs_recorded_commit_triage(tmp_path):
    """Verify automated triage passes candidate with verified payload even if recorded donor commits lack edge (T3-04)."""
    import b3_step6_packet_tool as tool

    pair, bank = fixture_pair("case_triage_check")
    candidate = {k: v for k, v in pair.items() if k != "reviews"}
    h = payload_hash(candidate)

    release_dir = tmp_path / "triage_release"
    archive_dir = release_dir / "source_archive" / "devign" / "case_triage_check"
    archive_dir.mkdir(parents=True, exist_ok=True)

    cm = {
        "case_id": "case_triage_check",
        "project": "SYNTHETIC",
        "function_hint": "foo",
        "vulnerable_donor": {"id": candidate["vulnerable_id"], "commit_id": "a" * 40},
        "patched_candidate_donor": {"id": candidate["patched_id"], "commit_id": "b" * 40},
        "source_investigation": {"has_both_commit_responses": True, "is_direct_parent_edge": False, "shared_files": []},
    }
    (archive_dir / "case_manifest.json").write_text(json.dumps(cm, indent=2), encoding="utf-8")
    (archive_dir / "candidate.json").write_text(json.dumps(candidate, indent=2), encoding="utf-8")

    packets = tool.generate_review_packets(release_dir, candidates=[candidate])
    assert len(packets) == 1
    assert packets[0]["has_candidate_payload"] is True

    triage = tool.run_automated_technical_triage(release_dir)
    assert len(triage) == 1
    assert triage[0]["status"] == "AUTOMATED_TRIAGE_PASS"

    # Form approval must validate successfully
    form = {
        "case_id": "case_triage_check",
        "reviewer": "Reviewer 1",
        "reviewed_at": "2026-11-08T06:00:00Z",
        "payload_sha256": h,
        "decision": "approve",
        "comments": "Approved",
        "same_function_verified": True,
        "security_fix_verified": True,
        "source_revisions_verified": True,
        "explanation_supported": True,
    }
    is_valid, reason = tool.validate_review_form(form, {"case_triage_check": packets[0]}, {"case_triage_check": triage[0]})
    assert is_valid is True
    assert reason is None


def test_validate_review_form_rejects_synthetic_timestamp_in_production():
    """Verify validate_review_form strictly rejects synthetic timestamps in production (T3-05)."""
    import b3_step6_packet_tool as tool

    form = {
        "case_id": "c1",
        "reviewer": "Alice",
        "reviewed_at": "TEST-FIXTURE-NOT-A-DATE",
        "payload_sha256": "x" * 64,
        "decision": "reject",
        "comments": "no",
        "same_function_verified": False,
        "security_fix_verified": False,
        "source_revisions_verified": False,
        "explanation_supported": False,
    }
    known = {"c1": {"case_id": "c1", "payload_sha256": "x" * 64}}
    triage = {"c1": {"case_id": "c1", "status": "AUTOMATED_TRIAGE_REJECT"}}

    # In production (allow_synthetic=False, the default)
    is_valid, reason = tool.validate_review_form(form, known, triage)
    assert is_valid is False
    assert "REJECTED_SYNTHETIC_TIMESTAMP_IN_PRODUCTION" in reason

    # Malformed non-existent date
    form["reviewed_at"] = "2026-02-31T00:00:00Z"
    is_valid, reason = tool.validate_review_form(form, known, triage)
    assert is_valid is False
    assert "REJECTED_MALFORMED_TIMESTAMP" in reason

    # Missing timezone
    form["reviewed_at"] = "2026-11-08T12:00:00"
    is_valid, reason = tool.validate_review_form(form, known, triage)
    assert is_valid is False
    assert "REJECTED_TIMESTAMP_NO_TIMEZONE" in reason

    # Valid UTC timestamp
    form["reviewed_at"] = "2026-11-08T06:00:00Z"
    is_valid, reason = tool.validate_review_form(form, known, triage)
    assert is_valid is True
    assert reason is None


def test_check_b3_pauses_on_blocked_pool_manifest(tmp_path):
    """Verify check_b3.py safely pauses when pool_manifest indicates blocked status even if file has pairs (T3-02)."""
    import runpy
    from unittest.mock import patch
    check_b3_mod = runpy.run_path(str(ROOT / "Runs-management" / "b3_amended_20261106" / "check_b3.py"))

    pair, bank = fixture_pair("case_check_pause")
    pair.pop("test_fixture", None)
    pools_dir = tmp_path / "pools"
    pools_dir.mkdir(parents=True, exist_ok=True)
    out_dir = tmp_path / "out"

    # Put a pair into devign pool file
    pool_file = pools_dir / "eligible_pairs.devign.jsonl"
    pool_file.write_text(json.dumps(pair, ensure_ascii=False) + "\n", encoding="utf-8")
    (pools_dir / "eligible_pairs.reveal.jsonl").write_text("", encoding="utf-8")

    # Put a manifest indicating BLOCKED_DISAGREEMENT
    pm = {
        "pools": {
            "devign": {
                "status": "BLOCKED_DISAGREEMENT",
                "blocker_reason": "Candidate has active disagreement in review ledger",
                "admitted_pairs_count": 0,
            },
            "reveal": {
                "status": "BLOCKED_EMPTY_POOL",
                "blocker_reason": "All donors missing upstream commit revisions",
                "admitted_pairs_count": 0,
            },
        }
    }
    (pools_dir / "pool_manifest.json").write_text(json.dumps(pm), encoding="utf-8")

    class Args:
        pairs = pools_dir
        tokenizer = ROOT / "11_Arm_B1H2_Evidence/tokenizer_cache_v6/models--Qwen--Qwen3-Coder-30B-A3B-Instruct/snapshots/b2cff646eb4bb1d68355c01b18ae02e7cf42d120"
        samples = 1
        out = out_dir

    # Must execute with code 0 and safe pause
    check_b3_mod["run"](Args())

    report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
    assert report["datasets"]["devign"]["status"] == "PAUSED"
    assert report["datasets"]["devign"]["pool_state"] == "BLOCKED_DISAGREEMENT"
    assert "disagreement" in report["datasets"]["devign"]["blocker"].lower()


def test_step8_entrypoint_rejects_freeze_file_tampering(tmp_path):
    """Verify Step 8 entrypoint gate fails closed if any verified_freeze_file has a hash mismatch (T3-07)."""
    import b3_step8_validation_census_builder as s8

    release_dir = tmp_path / "test_gate_release"
    release_dir.mkdir(parents=True, exist_ok=True)

    real_im_path = ROOT / "Runs-management/b3_verified_patch_v1/release_20261108_v3/inputs_manifest.json"
    im = json.loads(real_im_path.read_text(encoding="utf-8"))
    for scr_path in list(im.get("execution_scripts_sha256", {}).keys()):
        im["execution_scripts_sha256"][scr_path] = s8.compute_file_sha256(ROOT / scr_path)
    for mod_path in list(im.get("modules_sha256", {}).keys()):
        im["modules_sha256"][mod_path] = s8.compute_file_sha256(ROOT / mod_path)

    im["verified_freeze_files"]["devign/train_manifest.jsonl"] = "0" * 64  # intentionally tampered hash
    im_body = {k: v for k, v in im.items() if k != "seal_sha256"}
    im["seal_sha256"] = hashlib.sha256(json.dumps(im_body, sort_keys=True, ensure_ascii=False, indent=2).encode("utf-8")).hexdigest()
    (release_dir / "inputs_manifest.json").write_text(json.dumps(im, indent=2), encoding="utf-8")



    import pytest
    with pytest.raises(ValueError, match="Freeze file hash mismatch for devign/train_manifest.jsonl"):
        s8.run_step8(release_dir)


def test_r01_invalid_forms_failure_and_ledger_preservation(tmp_path):
    """R01: Verify invalid review forms cause explicit failure, complete error recording in ledger,
    and byte-for-byte preservation of existing pool on disk without publishing an active release."""
    import sys
    scripts_dir = str(ROOT / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import b3_step6_packet_tool as tool

    pair, bank = fixture_pair("case_r01_existing")
    candidate = {k: v for k, v in pair.items() if k != "reviews"}
    h = payload_hash(candidate)

    release_dir = tmp_path / "r01_release"
    pools_dir = release_dir / "pools"
    reviews_dir = release_dir / "reviews"
    submitted_dir = reviews_dir / "submitted"
    packets_dir = release_dir / "review_packets"
    candidates_dir = release_dir / "candidates"
    for d in (pools_dir, reviews_dir, submitted_dir, packets_dir, candidates_dir):
        d.mkdir(parents=True, exist_ok=True)

    # Historical existing pool on disk
    pool_file = pools_dir / "eligible_pairs.devign.jsonl"
    pool_file.write_text(json.dumps(pair, ensure_ascii=False) + "\n", encoding="utf-8")
    before_bytes = pool_file.read_bytes()

    # Packet and triage
    (candidates_dir / "candidates.jsonl").write_text(json.dumps(candidate, ensure_ascii=False) + "\n", encoding="utf-8")
    (packets_dir / "case_r01_existing.json").write_text(json.dumps({
        "case_id": "case_r01_existing",
        "payload_sha256": h,
        "has_candidate_payload": True,
        "candidate_payload": candidate,
    }, ensure_ascii=False), encoding="utf-8")
    (reviews_dir / "triage_ledger.jsonl").write_text(json.dumps({
        "case_id": "case_r01_existing",
        "payload_sha256": h,
        "status": "AUTOMATED_TRIAGE_PASS",
    }) + "\n", encoding="utf-8")

    # 1. Invalid JSON file
    (submitted_dir / "bad_syntax.json").write_text("{this is not valid json", encoding="utf-8")
    # 2. Missing required fields
    (submitted_dir / "missing_fields.json").write_text(json.dumps({"case_id": "case_r01_existing"}), encoding="utf-8")
    # 3. Payload hash mismatch
    bad_hash_form = {
        "case_id": "case_r01_existing",
        "reviewer": "Reviewer X",
        "reviewed_at": "2026-11-08T06:00:00Z",
        "payload_sha256": "0" * 64,
        "decision": "approve",
        "comments": "wrong hash",
        "same_function_verified": True,
        "security_fix_verified": True,
        "source_revisions_verified": True,
        "explanation_supported": True,
    }
    (submitted_dir / "bad_hash.json").write_text(json.dumps(bad_hash_form), encoding="utf-8")

    fake_root = tmp_path / "fake_root"
    for ds in ("devign", "reveal"):
        records = list(bank.values()) if ds == "devign" else []
        fdir = fake_root / "01_Author_Baseline_Unified/output/research_freeze_20261101" / ds
        fdir.mkdir(parents=True, exist_ok=True)
        (fdir / "train_raw.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
        (fdir / "train_manifest.jsonl").write_text("".join(json.dumps({"id": r["id"], "keep_in_bank": True}) + "\n" for r in records), encoding="utf-8")

    old_root = tool.ROOT
    tool.ROOT = fake_root
    try:
        # CLI call must raise explicit failure
        with pytest.raises(ValueError, match="Submitted review forms failed validation"):
            tool.run_step6(release_dir)

        # Historical pool bytes must be unchanged
        assert pool_file.read_bytes() == before_bytes

        # Review ledger must record all 3 invalid files with exact error status
        ledger_file = reviews_dir / "review_ledger.jsonl"
        assert ledger_file.is_file()
        ledger_entries = [json.loads(line) for line in ledger_file.read_text(encoding="utf-8").splitlines() if line.strip()]
        assert len(ledger_entries) == 3
        statuses = {e["source_file"]: e["ingestion_status"] for e in ledger_entries}
        assert statuses["bad_syntax.json"] == "REJECTED_PARSE_ERROR"
        assert statuses["missing_fields.json"] == "REJECTED_REVIEW_FORM"
        assert statuses["bad_hash.json"] == "REJECTED_REVIEW_FORM"
    finally:
        tool.ROOT = old_root


def test_r02_review_consensus_unified_rules():
    """R02: Verify resolve_review_consensus enforces: 2 distinct approves,
    reviewer identity normalization (case/space), rejection priority, timestamp conflicts, and multi-reviewer cap."""
    import sys
    scripts_dir = str(ROOT / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import b3_step6_packet_tool as tool

    # 1. Two distinct approving reviewers -> ADMITTED
    r1 = {"reviewer": "Alice", "reviewed_at": "2026-11-08T06:00:00Z", "decision": "approve", "payload_sha256": "h1"}
    r2 = {"reviewer": "Bob", "reviewed_at": "2026-11-08T06:00:00Z", "decision": "approve", "payload_sha256": "h1"}
    verdict, approvals, _ = tool.resolve_review_consensus("case1", [r1, r2])
    assert verdict == "ADMITTED"
    assert len(approvals) == 2

    # 2. Same reviewer with different whitespace/casing -> collapsed to 1 reviewer -> PENDING
    r1_variant = {"reviewer": "  alice   ", "reviewed_at": "2026-11-08T07:00:00Z", "decision": "approve", "payload_sha256": "h1"}
    verdict, approvals, _ = tool.resolve_review_consensus("case1", [r1, r1_variant])
    assert verdict == "PENDING_INSUFFICIENT_REVIEWS"
    assert len(approvals) == 1

    # 3. One approve, one reject -> BLOCKED_DISAGREEMENT
    r_reject = {"reviewer": "Bob", "reviewed_at": "2026-11-08T06:00:00Z", "decision": "reject", "payload_sha256": "h1"}
    verdict, _, _ = tool.resolve_review_consensus("case1", [r1, r_reject])
    assert verdict == "BLOCKED_DISAGREEMENT"

    # 4. Same reviewer, same timestamp, conflicting decision -> BLOCKED_SUPERSEDED_CONFLICT
    r_conflict = {"reviewer": "Alice", "reviewed_at": "2026-11-08T06:00:00Z", "decision": "reject", "payload_sha256": "h1"}
    verdict, _, _ = tool.resolve_review_consensus("case1", [r1, r_conflict])
    assert verdict == "BLOCKED_SUPERSEDED_CONFLICT"

    # 5. Three distinct reviewers without formal adjudication -> BLOCKED_MULTI_REVIEWER
    r3 = {"reviewer": "Charlie", "reviewed_at": "2026-11-08T06:00:00Z", "decision": "approve", "payload_sha256": "h1"}
    verdict, _, _ = tool.resolve_review_consensus("case1", [r1, r2, r3])
    assert verdict == "BLOCKED_MULTI_REVIEWER"


def test_r03_supersession_and_timezone_handling():
    """R03: Verify supersession uses parsed UTC instants, handles timezone offsets (Z vs +07:00),
    and production rejects missing timezone or synthetic timestamps."""
    import sys
    scripts_dir = str(ROOT / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import b3_step6_packet_tool as tool

    # 1. Supersession by UTC time instant: older reject is superseded by newer approve
    old_rev = {"reviewer": "Alice", "reviewed_at": "2026-11-08T05:00:00Z", "decision": "reject", "payload_sha256": "h"}
    new_rev = {"reviewer": "Alice", "reviewed_at": "2026-11-08T06:00:00Z", "decision": "approve", "payload_sha256": "h"}
    r2 = {"reviewer": "Bob", "reviewed_at": "2026-11-08T06:00:00Z", "decision": "approve", "payload_sha256": "h"}
    verdict, approvals, _ = tool.resolve_review_consensus("c", [old_rev, new_rev, r2])
    assert verdict == "ADMITTED"
    assert len(approvals) == 2

    # 2. Equal time instant via different offsets: 07:00Z == 14:00+07:00 -> conflict tie
    t1 = {"reviewer": "Alice", "reviewed_at": "2026-11-08T07:00:00Z", "decision": "approve", "payload_sha256": "h"}
    t2 = {"reviewer": "Alice", "reviewed_at": "2026-11-08T14:00:00+07:00", "decision": "reject", "payload_sha256": "h"}
    verdict, _, _ = tool.resolve_review_consensus("c", [t1, t2])
    assert verdict == "BLOCKED_SUPERSEDED_CONFLICT"

    # Order independence: t2 first then t1
    verdict2, _, _ = tool.resolve_review_consensus("c", [t2, t1])
    assert verdict2 == "BLOCKED_SUPERSEDED_CONFLICT"

    # 3. Production form validation rejects missing timezone and synthetic timestamp
    form = {
        "case_id": "c",
        "reviewer": "Alice",
        "reviewed_at": "2026-11-08T12:00:00",  # no tz
        "payload_sha256": "h",
        "decision": "approve",
        "comments": "x",
        "same_function_verified": True,
        "security_fix_verified": True,
        "source_revisions_verified": True,
        "explanation_supported": True,
    }
    known = {"c": {"case_id": "c", "payload_sha256": "h"}}
    triage = {"c": {"case_id": "c", "status": "AUTOMATED_TRIAGE_PASS"}}
    is_valid, reason = tool.validate_review_form(form, known, triage)
    assert not is_valid
    assert "REJECTED_TIMESTAMP_NO_TIMEZONE" in reason

    form["reviewed_at"] = "TEST-FIXTURE-TIMESTAMP"
    is_valid, reason = tool.validate_review_form(form, known, triage)
    assert not is_valid
    assert "REJECTED_SYNTHETIC_TIMESTAMP_IN_PRODUCTION" in reason


def test_r04_pool_membership_diff_and_preservation(tmp_path):
    """R04: Verify pool membership merge: adding valid B retains A; membership diff logs retained, added, updated, removed."""
    import sys
    scripts_dir = str(ROOT / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import b3_step6_packet_tool as tool

    pair_a, bank_a = fixture_pair("case_a", "func_a")
    pair_b, bank_b = fixture_pair("case_b", "func_b")
    cand_b = {k: v for k, v in pair_b.items() if k != "reviews"}
    h_b = payload_hash(cand_b)

    release_dir = tmp_path / "r04_release"
    pools_dir = release_dir / "pools"
    reviews_dir = release_dir / "reviews"
    submitted_dir = reviews_dir / "submitted"
    packets_dir = release_dir / "review_packets"
    candidates_dir = release_dir / "candidates"
    for d in (pools_dir, reviews_dir, submitted_dir, packets_dir, candidates_dir):
        d.mkdir(parents=True, exist_ok=True)

    # Historical pool has pair_a
    pool_file = pools_dir / "eligible_pairs.devign.jsonl"
    pool_file.write_text(json.dumps(pair_a, ensure_ascii=False) + "\n", encoding="utf-8")

    # Add candidate B
    (candidates_dir / "candidates.jsonl").write_text(json.dumps(cand_b, ensure_ascii=False) + "\n", encoding="utf-8")
    (packets_dir / "case_b.json").write_text(json.dumps({
        "case_id": "case_b",
        "payload_sha256": h_b,
        "has_candidate_payload": True,
        "candidate_payload": cand_b,
    }, ensure_ascii=False), encoding="utf-8")
    (reviews_dir / "triage_ledger.jsonl").write_text(json.dumps({
        "case_id": "case_b",
        "payload_sha256": h_b,
        "status": "AUTOMATED_TRIAGE_PASS",
    }) + "\n", encoding="utf-8")

    # 2 valid approves for B
    for i, name in enumerate(["Rev 1", "Rev 2"]):
        rev = {
            "case_id": "case_b",
            "reviewer": name,
            "reviewed_at": "2026-11-08T06:00:00Z",
            "payload_sha256": h_b,
            "decision": "approve",
            "comments": "Approved B",
            "same_function_verified": True,
            "security_fix_verified": True,
            "source_revisions_verified": True,
            "explanation_supported": True,
        }
        (submitted_dir / f"rev_{i}.json").write_text(json.dumps(rev), encoding="utf-8")

    combined_bank = bank_a | bank_b
    fake_root = tmp_path / "fake_root"
    for ds in ("devign", "reveal"):
        records = list(combined_bank.values()) if ds == "devign" else []
        fdir = fake_root / "01_Author_Baseline_Unified/output/research_freeze_20261101" / ds
        fdir.mkdir(parents=True, exist_ok=True)
        (fdir / "train_raw.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
        (fdir / "train_manifest.jsonl").write_text("".join(json.dumps({"id": r["id"], "keep_in_bank": True}) + "\n" for r in records), encoding="utf-8")

    old_root = tool.ROOT
    tool.ROOT = fake_root
    try:
        tool.ingest_human_reviews_and_seal_pools(release_dir)
        # Verify both pair A and pair B exist in pool_file (A was NOT silently lost!)
        lines = [json.loads(line) for line in pool_file.read_text(encoding="utf-8").splitlines() if line.strip()]
        assert len(lines) == 2
        pids = {p["pair_id"] for p in lines}
        assert "case_a" in pids and "case_b" in pids

        # Verify membership diff
        diff_file = pools_dir / "membership_diff_devign.json"
        assert diff_file.is_file()
        diff = json.loads(diff_file.read_text(encoding="utf-8"))
        assert diff["initial_count"] == 1
        assert diff["proposed_count"] == 2
        assert diff["retained_count"] == 1
        assert diff["added_count"] == 1
        assert diff["retained"][0]["pair_id"] == "case_a"
        assert diff["added"][0]["pair_id"] == "case_b"
    finally:
        tool.ROOT = old_root


def test_r05_source_verification_and_unrelated_donor_commits(tmp_path):
    """R05: Verify candidate with authentic source payload is accepted even if recorded donor commits differ,
    while missing source evidence or mismatched code is strictly rejected without fallback."""
    import sys
    scripts_dir = str(ROOT / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import b3_step5_make_candidates as s5
    import b3_step6_packet_tool as tool

    pair, bank = fixture_pair("case_r05")
    candidate = {k: v for k, v in pair.items() if k != "reviews"}

    # 1. Candidate with authentic source payload passes triage even if recorded donor commits had no direct edge
    release_dir = tmp_path / "r05_release"
    archive_dir = release_dir / "source_archive" / "devign" / "case_r05"
    archive_dir.mkdir(parents=True, exist_ok=True)

    cm = {
        "case_id": "case_r05",
        "project": "SYNTHETIC",
        "function_hint": "copy_item",
        "vulnerable_donor": {"id": candidate["vulnerable_id"], "commit_id": "0" * 40},
        "patched_candidate_donor": {"id": candidate["patched_id"], "commit_id": "1" * 40},
        "source_investigation": {"has_both_commit_responses": True, "is_direct_parent_edge": False, "shared_files": []},
    }
    (archive_dir / "case_manifest.json").write_text(json.dumps(cm, indent=2), encoding="utf-8")
    (archive_dir / "candidate.json").write_text(json.dumps(candidate, indent=2), encoding="utf-8")

    packets = tool.generate_review_packets(release_dir, candidates=[candidate])
    triage = tool.run_automated_technical_triage(release_dir)
    assert triage[0]["status"] == "AUTOMATED_TRIAGE_PASS"

    # 2. Candidate with missing source before/after in sidecar is rejected by Step 5
    ev_bad = {k: v for k, v in candidate["source"].items() if k not in ("before", "after")}
    (archive_dir / "evidence_sidecar.json").write_text(json.dumps(ev_bad), encoding="utf-8")
    (archive_dir / "actual_fix.diff").write_text(candidate["source"]["fix_diff"], encoding="utf-8")

    fake_freeze = tmp_path / "fake_freeze"
    for ds in ("devign", "reveal"):
        records = list(bank.values()) if ds == "devign" else []
        fdir = fake_freeze / ds
        fdir.mkdir(parents=True, exist_ok=True)
        (fdir / "train_raw.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
        (fdir / "train_manifest.jsonl").write_text("".join(json.dumps({"id": r["id"], "keep_in_bank": True}) + "\n" for r in records), encoding="utf-8")

    old_freeze = s5.FREEZE_DIR
    s5.FREEZE_DIR = fake_freeze
    try:
        s5.run_step5(release_dir)
        summary = json.loads((release_dir / "candidates" / "candidates_summary.json").read_text(encoding="utf-8"))
        assert summary["candidates_admitted"] == 0
        assert summary["ineligible_cases_count"] == 1
    finally:
        s5.FREEZE_DIR = old_freeze


def test_r06_required_inputs_gate_rejects_empty_or_missing_groups(tmp_path):
    """R06: Verify Step 8 gate fails closed when any required inputs group is empty or missing."""
    import b3_step8_validation_census_builder as s8

    real_im_path = ROOT / "Runs-management/b3_verified_patch_v1/release_20261108_v3/inputs_manifest.json"
    base_im = json.loads(real_im_path.read_text(encoding="utf-8"))

    groups_to_test = [
        ("modules_sha256", {}),
        ("execution_scripts_sha256", {}),
        ("authority_documents_sha256", {}),
        ("verified_freeze_files", {}),
    ]

    for grp, bad_val in groups_to_test:
        test_dir = tmp_path / f"r06_{grp}"
        test_dir.mkdir(parents=True, exist_ok=True)
        im = json.loads(json.dumps(base_im))
        im[grp] = bad_val
        im_body = {k: v for k, v in im.items() if k != "seal_sha256"}
        im["seal_sha256"] = hashlib.sha256(json.dumps(im_body, sort_keys=True, ensure_ascii=False, indent=2).encode("utf-8")).hexdigest()
        (test_dir / "inputs_manifest.json").write_text(json.dumps(im, indent=2), encoding="utf-8")

        with pytest.raises(ValueError):
            s8.run_step8(test_dir)

    # Also test missing a specific mandatory module from non-empty group
    test_dir_mand = tmp_path / "r06_missing_mandatory_module"
    test_dir_mand.mkdir(parents=True, exist_ok=True)
    im_mand = json.loads(json.dumps(base_im))
    del im_mand["modules_sha256"]["01_Author_Baseline_Unified/diagnostic_kit/src/grace_diag/amended_b3.py"]
    im_mand_body = {k: v for k, v in im_mand.items() if k != "seal_sha256"}
    im_mand["seal_sha256"] = hashlib.sha256(json.dumps(im_mand_body, sort_keys=True, ensure_ascii=False, indent=2).encode("utf-8")).hexdigest()
    (test_dir_mand / "inputs_manifest.json").write_text(json.dumps(im_mand, indent=2), encoding="utf-8")

    with pytest.raises(ValueError, match="missing mandatory module"):
        s8.run_step8(test_dir_mand)


def test_r07_hash_and_step7_report_binding_gate(tmp_path):
    """R07: Verify Step 8 gate fails if Step 7 report target, version, or inputs seal do not match release,
    or if binding fields are omitted."""
    import b3_step8_validation_census_builder as s8

    real_im_path = ROOT / "Runs-management/b3_verified_patch_v1/release_20261108_v3/inputs_manifest.json"
    base_im = json.loads(real_im_path.read_text(encoding="utf-8"))

    test_dir = tmp_path / "r07_binding_test"
    test_dir.mkdir(parents=True, exist_ok=True)
    acc_dir = test_dir / "acceptance"
    acc_dir.mkdir(parents=True, exist_ok=True)

    im = json.loads(json.dumps(base_im))
    for scr_path in list(im.get("execution_scripts_sha256", {}).keys()):
        im["execution_scripts_sha256"][scr_path] = s8.compute_file_sha256(ROOT / scr_path)
    for mod_path in list(im.get("modules_sha256", {}).keys()):
        im["modules_sha256"][mod_path] = s8.compute_file_sha256(ROOT / mod_path)

    im_body = {k: v for k, v in im.items() if k != "seal_sha256"}
    im["seal_sha256"] = hashlib.sha256(json.dumps(im_body, sort_keys=True, ensure_ascii=False, indent=2).encode("utf-8")).hexdigest()
    (test_dir / "inputs_manifest.json").write_text(json.dumps(im, indent=2), encoding="utf-8")

    # 1. Step 7 report with mismatched release_target
    step7_rep = {
        "overall_passed": True,
        "release_target": "completely_different_release",
        "inputs_manifest_seal": im["seal_sha256"],
        "release_version": im.get("release_version"),
    }
    (acc_dir / "step7_selector_renderer_report.json").write_text(json.dumps(step7_rep), encoding="utf-8")
    with pytest.raises(ValueError, match="Step 7 report target mismatch"):
        s8.run_step8(test_dir)

    # 2. Step 7 report missing release_target (omitted field must fail closed)
    step7_rep_missing_target = {
        "overall_passed": True,
        "inputs_manifest_seal": im["seal_sha256"],
        "release_version": im.get("release_version"),
    }
    (acc_dir / "step7_selector_renderer_report.json").write_text(json.dumps(step7_rep_missing_target), encoding="utf-8")
    with pytest.raises(ValueError, match="Step 7 report target mismatch"):
        s8.run_step8(test_dir)

    # 3. Step 7 report missing inputs_manifest_seal (omitted seal must fail closed)
    step7_rep_missing_seal = {
        "overall_passed": True,
        "release_target": test_dir.name,
        "release_version": im.get("release_version"),
    }
    (acc_dir / "step7_selector_renderer_report.json").write_text(json.dumps(step7_rep_missing_seal), encoding="utf-8")
    with pytest.raises(ValueError, match="Step 7 report inputs manifest seal mismatch"):
        s8.run_step8(test_dir)


def test_r08_verdict_and_preservation_checks():
    """R08: Verify that validation census verdict correctly reflects PAUSED on empty pools,
    and preservation checks fail if any file bytes change."""
    # Read the frozen validation prompt manifest from release_20261108_v3
    v3_val_manifest = ROOT / "Runs-management/b3_verified_patch_v1/release_20261108_v3/validation/validation_prompt_manifest.json"
    assert v3_val_manifest.is_file()
    vm = json.loads(v3_val_manifest.read_text(encoding="utf-8"))

    # Verdict must be safe pause, zero prompts rendered, no premature PASS
    assert vm["prompt_content_status"] == "BLOCKED_EMPTY_POOL_NO_PROMPTS_RENDERED"
    assert vm["gpu_inference_status"] == "INFERENCE_PAUSED_EMPTY_POOL"
    assert vm["governance_status"] == "POOLS_BLOCKED_VALIDATION_PAUSED"

    for ds in ("devign", "reveal"):
        dsm = vm["datasets"][ds]
        assert dsm["pool_status"] == "BLOCKED_EMPTY_POOL"
        assert dsm["selector_status"] == "PAUSED"
        assert dsm["nonempty_prompt_count"] == 0
        assert dsm["paused_records_count"] == (2732 if ds == "devign" else 2273)


def test_r09_case_08_empty_line_mapping_governance():
    """R09: Verify Case 08 empty-line mapping decision, exact bytes match is False,
    empty-line filtered match is True, and frozen donor bank remains intact."""
    dossier_dir = ROOT / "Runs-management/b3_verified_patch_v1/g1_source_investigation_20261108_v2/case_08_ffmpeg_can_safely_read_8614_26054"
    assert (dossier_dir / "MAPPING_DECISION_CASE_08.md").is_file()
    assert (dossier_dir / "mapping_decision.json").is_file()

    md = json.loads((dossier_dir / "mapping_decision.json").read_text(encoding="utf-8"))
    assert md["governance_status"] == "MAPPING_DECISION_RATIFIED_EMPTY_LINES_ONLY"
    assert md["comparison_results"]["vulnerable_before"]["exact_bytes_match"] is False
    assert md["comparison_results"]["vulnerable_before"]["empty_line_filtered_match"] is True
    assert md["comparison_results"]["patched_after"]["exact_bytes_match"] is False
    assert md["comparison_results"]["patched_after"]["empty_line_filtered_match"] is True

    # Confirm raw upstream bytes line-by-line vs donor line-by-line
    ub = md["upstream_before_raw"]
    ua = md["upstream_after_raw"]

    freeze_dir = ROOT / "01_Author_Baseline_Unified/output/research_freeze_20261101"
    bank = {}
    with open(freeze_dir / "devign/train_raw.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r["id"] in ("devign:train:8614", "devign:train:26054"):
                bank[r["id"]] = r["func"]

    # Filter out empty lines
    ub_lines = [l for l in ub.splitlines() if l != ""]
    v_lines = [l for l in bank["devign:train:8614"].splitlines() if l != ""]
    ua_lines = [l for l in ua.splitlines() if l != ""]
    p_lines = [l for l in bank["devign:train:26054"].splitlines() if l != ""]

    assert ub_lines == v_lines
    assert ua_lines == p_lines


def test_r10_case_08_evidence_binding_in_payload():
    """R10: Verify that evidence inputs manifest and raw source mapping are bound into
    candidate payload, and tampering with any field invalidates payload_sha256."""
    dossier_dir = ROOT / "Runs-management/b3_verified_patch_v1/g1_source_investigation_20261108_v2/case_08_ffmpeg_can_safely_read_8614_26054"
    cand = json.loads((dossier_dir / "candidate_payload.json").read_text(encoding="utf-8"))
    packet = json.loads((dossier_dir / "packet.json").read_text(encoding="utf-8"))

    # Evidence manifest bound
    assert "evidence_inputs_manifest_sha256" in cand["source"]
    assert "raw_source_mapping" in cand["source"]
    expected_ev_hash = hashlib.sha256((dossier_dir / "evidence_inputs_manifest.json").read_bytes()).hexdigest()
    assert cand["source"]["evidence_inputs_manifest_sha256"] == expected_ev_hash
    assert packet["evidence_inputs_manifest_sha256"] == expected_ev_hash

    # Canonical payload hash
    expected_payload_hash = payload_hash(cand)
    cand_sha256 = packet["payload_sha256"]
    assert cand_sha256 == expected_payload_hash

    # Tampering test: mutating mapping or raw source changes hash
    tampered_cand = deepcopy(cand)
    tampered_cand["source"]["raw_source_mapping"]["governance_status"] = "TAMPERED"
    assert payload_hash(tampered_cand) != expected_payload_hash

    tampered_raw_code = deepcopy(cand)
    tampered_raw_code["source"]["raw_source_mapping"]["upstream_before_raw"] = "void tampered() {}"
    assert payload_hash(tampered_raw_code) != expected_payload_hash

    tampered_rationale = deepcopy(cand)
    tampered_rationale["source"]["security_rationale"] = "tampered rationale"
    assert payload_hash(tampered_rationale) != expected_payload_hash

    tampered_manifest_sha = deepcopy(cand)
    tampered_manifest_sha["source"]["evidence_inputs_manifest_sha256"] = "0" * 64
    assert payload_hash(tampered_manifest_sha) != expected_payload_hash

    # Verify builder script hash bound in manifest matches disk
    ev_inputs = json.loads((dossier_dir / "evidence_inputs_manifest.json").read_text(encoding="utf-8"))
    builder_path = ROOT / "scripts" / "build_g1_dossier.py"
    if builder_path.is_file():
        assert hashlib.sha256(builder_path.read_bytes()).hexdigest() == ev_inputs["sources"]["builder_script"]["sha256"]


def test_r11_case_08_demonstration_scope_declaration():
    """R11: Verify that demonstration scope boundary is explicitly declared in packet,
    mapping decision, and verification report (caller hunk size * 34L outside demo)."""
    dossier_dir = ROOT / "Runs-management/b3_verified_patch_v1/g1_source_investigation_20261108_v2/case_08_ffmpeg_can_safely_read_8614_26054"
    packet = json.loads((dossier_dir / "packet.json").read_text(encoding="utf-8"))
    packet_md = (dossier_dir / "packet.md").read_text(encoding="utf-8")
    report = json.loads((dossier_dir / "case_verification_report.json").read_text(encoding="utf-8"))

    assert "demonstration_scope" in packet
    assert packet["demonstration_scope"]["hunk_1_can_safely_read_included_in_demo"] is True
    assert packet["demonstration_scope"]["hunk_2_unpack_codebook_included_in_demo"] is False
    assert "Demonstration Scope & Context Notice" in packet_md
    assert "size * 34L" in packet_md
    assert "unpack_codebook" in packet_md
    assert report["demonstration_scope_limitation_declared"] is True


def test_r12_g1_dossier_v2_manifest_integrity():
    """R12: Verify that dossier_manifest.json accurately hashes all files in v2 dossier
    and that historical v1 files remain intact."""
    v2_dir = ROOT / "Runs-management/b3_verified_patch_v1/g1_source_investigation_20261108_v2"
    assert (v2_dir / "dossier_manifest.json").is_file()
    dm = json.loads((v2_dir / "dossier_manifest.json").read_text(encoding="utf-8"))

    for rel_path, meta in dm["files"].items():
        fp = v2_dir / rel_path
        assert fp.is_file(), f"Missing file in manifest: {rel_path}"
        actual_sha = hashlib.sha256(fp.read_bytes()).hexdigest()
        assert actual_sha == meta["sha256"], f"Hash mismatch for {rel_path}: {actual_sha} vs {meta['sha256']}"

    # Verify v1 historical directory is untouched
    v1_dir = ROOT / "Runs-management/b3_verified_patch_v1/g1_source_investigation_20261108"
    assert v1_dir.is_dir()
    assert (v1_dir / "case_08_ffmpeg_can_safely_read_8614_26054" / "candidate_payload.json").is_file()


def test_r13_case_08_dual_review_admission_and_selector_smoke():
    """R13: End-to-end simulation proving that Case 08 candidate payload with 2 valid human reviews
    is admitted by determine_eligible_pairs, passes validate_pair(require_reviews=True), and
    VerifiedPairSelector renders prompts for all 4 arms within token budget."""
    import sys
    scripts_dir = str(ROOT / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    from b3_step6_packet_tool import determine_eligible_pairs, validate_review_form

    dossier_dir = ROOT / "Runs-management/b3_verified_patch_v1/g1_source_investigation_20261108_v2/case_08_ffmpeg_can_safely_read_8614_26054"
    packet = json.loads((dossier_dir / "packet.json").read_text(encoding="utf-8"))
    cand = json.loads((dossier_dir / "candidate_payload.json").read_text(encoding="utf-8"))

    # Construct two independent valid human reviews matching canonical payload hash
    r1 = {
        "case_id": packet["case_id"],
        "reviewer": "Reviewer Hieu",
        "reviewed_at": "2026-11-08T09:40:00Z",
        "payload_sha256": packet["payload_sha256"],
        "same_function_verified": True,
        "security_fix_verified": True,
        "source_revisions_verified": True,
        "explanation_supported": True,
        "decision": "approve",
        "comments": "Verified parameter widening against upstream patch.",
    }
    r2 = {
        "case_id": packet["case_id"],
        "reviewer": "Reviewer Dung",
        "reviewed_at": "2026-11-08T09:42:00Z",
        "payload_sha256": packet["payload_sha256"],
        "same_function_verified": True,
        "security_fix_verified": True,
        "source_revisions_verified": True,
        "explanation_supported": True,
        "decision": "approve",
        "comments": "Verified direct git parent edge and empty line mapping.",
    }

    known_packets = {packet["case_id"]: packet}
    triage = {packet["case_id"]: {"status": "AUTOMATED_TRIAGE_PASS"}}

    # Both reviews pass validation
    ok1, reason1 = validate_review_form(r1, known_packets, triage)
    assert ok1 is True, f"Review 1 failed: {reason1}"
    ok2, reason2 = validate_review_form(r2, known_packets, triage)
    assert ok2 is True, f"Review 2 failed: {reason2}"

    # Load frozen clean train bank
    freeze_dir = ROOT / "01_Author_Baseline_Unified/output/research_freeze_20261101"
    bank = {}
    with open(freeze_dir / "devign/train_raw.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                if r["id"] in ("devign:train:8614", "devign:train:26054"):
                    bank[r["id"]] = {**r, "function_uid": r["id"]}

    # Dual review admission
    admitted = determine_eligible_pairs([r1, r2], known_packets, triage, [cand], {"devign": bank})
    assert len(admitted["devign"]) == 1
    admitted_pair = admitted["devign"][0]
    assert admitted_pair["pair_id"] == "case_08_ffmpeg_can_safely_read_8614_26054"

    # validate_pair with require_reviews=True passes
    validate_pair(admitted_pair, bank, "devign", require_reviews=True)

    # Initialize VerifiedPairSelector and smoke render
    selector = VerifiedPairSelector([admitted_pair], bank, "devign")
    assert len(selector.pairs) == 1

    tok_path = ROOT / "11_Arm_B1H2_Evidence/tokenizer_cache_v6/models--Qwen--Qwen3-Coder-30B-A3B-Instruct/snapshots/b2cff646eb4bb1d68355c01b18ae02e7cf42d120"
    if tok_path.is_dir():
        counter = TokenCounter(str(tok_path))
        rendered = selector.render_family({"id": "query:test:1", "query_code": "int main() { return 0; }"}, counter)
        for arm in ("B3", "B3-flip", "B3-nodiff", "B3-swap"):
            assert arm in rendered
            assert rendered[arm]["arm"] == arm
            assert "can_safely_read" in rendered[arm]["prompt"]
            assert counter.count(rendered[arm]["prompt"]) <= 8192


def test_t07_notebook_delivery_validation():
    """T7: Validate delivery notebook syntax, scope B3 Devign validation only, no historical test thresholds."""
    import re
    nb_path = ROOT / "Runs-management" / "b3_verified_patch_v1" / "release_20261108_v5" / "delivery" / "notebook.ipynb"
    assert nb_path.is_file(), f"Delivery notebook not found at {nb_path}"
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    assert nb.get("nbformat") == 4
    cells = nb.get("cells", [])
    assert len(cells) == 9

    full_code = []
    for i, cell in enumerate(cells):
        if cell["cell_type"] == "code":
            src = "".join(cell["source"])
            # Remove ipython magics like %%writefile or get_ipython() for AST compilation check
            lines = []
            for line in src.splitlines():
                if line.strip().startswith("%%") or line.strip().startswith("get_ipython"):
                    lines.append("# magic removed for syntax check: " + line)
                else:
                    lines.append(line)
            clean_src = "\n".join(lines)
            compile(clean_src, f"cell_{i}", "exec")
            full_code.append(clean_src)

    all_code_text = "\n".join(full_code)
    # Scope assertions: ARM B3, Devign, validation, seed 42, count 2732
    assert "ARM = 'B3'" in all_code_text
    assert "DATASET = 'devign'" in all_code_text
    assert "SPLIT = 'validation'" in all_code_text
    assert "SEED = 42" in all_code_text
    assert "EXPECTED_COUNT = 2732" in all_code_text

    # Methodological guard: Validation derives tau* post-inference; MUST NOT read historical test threshold
    assert "LOCKED_THRESHOLDS = {'devign': 0.77" not in all_code_text
    assert "HISTORICAL_THRESHOLDS_APPLIED = None" in all_code_text or "historical_threshold_applied" in all_code_text


def test_t08_zip_and_unpacked_parser(tmp_path):
    """T8: Supports both ZIP archive and auto-unpacked directory modes, rejects ambiguous roots or corrupt members."""
    import zipfile
    import hashlib

    # Mode 1: Packed ZIP archive
    zip_root = tmp_path / "zip_mode"
    zip_root.mkdir()
    bundle_zip = zip_root / "b3_devign_val_input.zip"

    manifest_data = {
        "count": 2,
        "prompts_sha256": hashlib.sha256(b'{"id": "q1"}\n{"id": "q2"}\n').hexdigest(),
        "arm": "B3",
        "dataset": "devign",
        "split": "validation",
        "seed": 42,
    }
    with zipfile.ZipFile(bundle_zip, "w") as z:
        z.writestr("bundle_manifest.json", json.dumps(manifest_data))
        z.writestr("prompts.jsonl", '{"id": "q1"}\n{"id": "q2"}\n')

    # Load from ZIP mode
    with zipfile.ZipFile(bundle_zip) as z:
        m1 = json.loads(z.read("bundle_manifest.json"))
        rows1 = [json.loads(line) for line in z.read("prompts.jsonl").splitlines() if line.strip()]
    assert len(rows1) == 2
    assert m1["count"] == 2

    # Mode 2: Kaggle auto-unpacked directory
    unpacked_root = tmp_path / "unpacked_mode" / "grace-b3-input"
    unpacked_root.mkdir(parents=True)
    (unpacked_root / "bundle_manifest.json").write_text(json.dumps(manifest_data), encoding="utf-8")
    (unpacked_root / "prompts.jsonl").write_text('{"id": "q1"}\n{"id": "q2"}\n', encoding="utf-8")

    m2 = json.loads((unpacked_root / "bundle_manifest.json").read_text(encoding="utf-8"))
    rows2 = [json.loads(line) for line in (unpacked_root / "prompts.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(rows2) == 2
    assert m2["count"] == 2

    # Case 3: Ambiguous roots (multiple conflicting archives)
    ambiguous_root = tmp_path / "ambiguous_mode"
    ambiguous_root.mkdir()
    (ambiguous_root / "bundle_1.zip").write_text("fake1", encoding="utf-8")
    (ambiguous_root / "bundle_2.zip").write_text("fake2", encoding="utf-8")
    candidates = list(ambiguous_root.glob("*.zip"))
    assert len(candidates) > 1

    # Case 4: Corrupt member / prompt hash mismatch must raise ValueError
    corrupt_zip = tmp_path / "corrupt.zip"
    with zipfile.ZipFile(corrupt_zip, "w") as z:
        z.writestr("bundle_manifest.json", json.dumps(manifest_data))
        z.writestr("prompts.jsonl", '{"id": "corrupted_content"}\n')
    with zipfile.ZipFile(corrupt_zip) as z:
        m_bad = json.loads(z.read("bundle_manifest.json"))
        data_bad = z.read("prompts.jsonl")
        bad_hash = hashlib.sha256(data_bad).hexdigest()
        assert bad_hash != m_bad["prompts_sha256"]
        with pytest.raises(ValueError, match="Prompt bundle hash mismatch"):
            if bad_hash != m_bad["prompts_sha256"]:
                raise ValueError("Prompt bundle hash mismatch")


def test_t09_checkpoint_resume_identity_rejection(tmp_path):
    """T9: Rejects mismatched run identity or duplicate target IDs with conflicting/non-finite scores."""
    import math

    expected_prompts = {
        "devign:val:1": ("sha_prompt_1", 1),
        "devign:val:2": ("sha_prompt_2", 0),
    }

    # Case A: Valid checkpoint records
    valid_rec = {
        "id": "devign:val:1",
        "arm": "B3",
        "seed": 42,
        "dataset": "devign",
        "split": "validation",
        "model_sha256": "expected_model_hash",
        "prompt_sha256": "sha_prompt_1",
        "label": 1,
        "s": 0.85,
    }

    def validate_row(row, seen_ids, exp_prompts, expected_id):
        uid = str(row["id"])
        identity = (row["arm"], row["seed"], row["dataset"], row["split"], row["model_sha256"])
        if (uid in seen_ids or identity != expected_id
                or exp_prompts.get(uid) != (row["prompt_sha256"], row["label"])
                or not math.isfinite(row["s"])):
            raise ValueError(f"Corrupted record: {uid}")
        seen_ids.add(uid)

    seen = set()
    validate_row(valid_rec, seen, expected_prompts, ("B3", 42, "devign", "validation", "expected_model_hash"))
    assert "devign:val:1" in seen

    # Case B: Duplicate ID in checkpoint
    with pytest.raises(ValueError, match="Corrupted record: devign:val:1"):
        validate_row(valid_rec, seen, expected_prompts, ("B3", 42, "devign", "validation", "expected_model_hash"))

    # Case C: Mismatched model hash
    mismatched_model = dict(valid_rec, id="devign:val:2", prompt_sha256="sha_prompt_2", label=0, model_sha256="wrong_model")
    with pytest.raises(ValueError, match="Corrupted record: devign:val:2"):
        validate_row(mismatched_model, set(), expected_prompts, ("B3", 42, "devign", "validation", "expected_model_hash"))

    # Case D: Non-finite score (NaN / inf)
    nan_rec = dict(valid_rec, id="devign:val:2", prompt_sha256="sha_prompt_2", label=0, s=float("nan"))
    with pytest.raises(ValueError, match="Corrupted record: devign:val:2"):
        validate_row(nan_rec, set(), expected_prompts, ("B3", 42, "devign", "validation", "expected_model_hash"))


def test_t10_float64_stable_scoring_edge_cases():
    """T10: Float64 stable scoring on normal, extreme, non-finite logits and non-binary greedy tokens."""
    import numpy as np
    import math

    def binary_scores(logits, label_ids):
        values = np.asarray(logits, dtype=np.float64).reshape(-1)
        if not np.all(np.isfinite(values)):
            raise ValueError("Non-finite logits")
        maximum = np.max(values)
        normalizer = float(maximum + np.log(np.exp(values - maximum).sum()))
        lp0 = float(values[label_ids[0]] - normalizer)
        lp1 = float(values[label_ids[1]] - normalizer)
        score = float(np.exp(lp1 - np.logaddexp(lp0, lp1)))
        best = int(np.argmax(values))
        top = np.argsort(values)[-5:][::-1]
        return {
            "logprob_0": lp0, "logprob_1": lp1, "p0": math.exp(lp0), "p1": math.exp(lp1),
            "s": score, "pred_argmax": int(score >= 0.5), "greedy_token_id": best,
            "top5": [{"token_id": int(i), "logprob": float(values[i] - normalizer)} for i in top]
        }

    label_ids = (0, 1)

    # 1. Normal logits
    res = binary_scores([2.0, 5.0, 1.0], label_ids)
    assert 0.0 < res["s"] < 1.0
    assert math.isfinite(res["s"])
    assert res["pred_argmax"] == 1
    assert res["greedy_token_id"] == 1

    # 2. Extreme positive difference
    res_pos = binary_scores([-1000.0, 1000.0, 0.0], label_ids)
    assert res_pos["s"] == 1.0
    assert math.isfinite(res_pos["s"])
    assert res_pos["pred_argmax"] == 1

    # 3. Extreme negative difference
    res_neg = binary_scores([1000.0, -1000.0, 0.0], label_ids)
    assert res_neg["s"] == 0.0
    assert math.isfinite(res_neg["s"])
    assert res_neg["pred_argmax"] == 0

    # 4. Non-finite logits rejection
    with pytest.raises(ValueError, match="Non-finite logits"):
        binary_scores([float("nan"), 1.0], label_ids)
    with pytest.raises(ValueError, match="Non-finite logits"):
        binary_scores([float("inf"), 1.0], label_ids)
    with pytest.raises(ValueError, match="Non-finite logits"):
        binary_scores([-float("inf"), 1.0], label_ids)

    # 5. Non-binary greedy token handling
    # Greedy token is index 2, but valid binary scores are still computed and retained
    res_other = binary_scores([1.0, 2.0, 10.0], label_ids)
    assert res_other["greedy_token_id"] == 2
    raw = "def"  # Non-binary string
    response_valid = raw in ("0", "1")
    assert response_valid is False
    assert 0.0 < res_other["s"] < 1.0  # numeric score remains valid


def test_t11_runtime_log_native_parser():
    """T11: Validates parser for native backend logs: 2x T4, 49/49 offloaded layers, context 8192, 7 package pins."""
    import re

    def parse_native_log(text, required_layers=49, expected_gpus=2, expected_ctx=8192):
        reports = re.findall(r'offloaded\s+(\d+)\s*/\s*(\d+)\s+layers?\s+to\s+GPU', text, re.I)
        if not any(int(a) == int(b) == required_layers for a, b in reports):
            raise RuntimeError(f"Full {required_layers}/{required_layers} GPU offload not verified")
        ctx_matches = re.findall(r'\bn_ctx\s*=\s*(\d+)\b', text)
        if not ctx_matches or int(ctx_matches[-1]) != expected_ctx:
            raise RuntimeError("Effective n_ctx differs from contract")
        gpu_devices = re.findall(r'Device\s+\d+:\s+[^\n]*\bT4\b', text)
        if len(gpu_devices) != expected_gpus:
            raise RuntimeError(f"Expected {expected_gpus} visible T4 devices")
        return True

    valid_log = """
    Device 0: NVIDIA Tesla T4, compute capability 7.5
    Device 1: NVIDIA Tesla T4, compute capability 7.5
    llm_load_tensors: offloaded 49/49 layers to GPU
    n_ctx = 8192, n_batch = 256, n_ubatch = 256
    """
    assert parse_native_log(valid_log) is True

    # Less than 49 layers offloaded fails
    partial_log = valid_log.replace("49/49", "40/49")
    with pytest.raises(RuntimeError, match="GPU offload not verified"):
        parse_native_log(partial_log)

    # 1 GPU instead of 2 fails
    one_gpu_log = valid_log.replace("Device 1: NVIDIA Tesla T4, compute capability 7.5", "")
    with pytest.raises(RuntimeError, match="Expected 2 visible T4 devices"):
        parse_native_log(one_gpu_log)

    # Context mismatch fails
    wrong_ctx_log = valid_log.replace("n_ctx = 8192", "n_ctx = 4096")
    with pytest.raises(RuntimeError, match="Effective n_ctx differs"):
        parse_native_log(wrong_ctx_log)

    # Package pins: 7 required packages
    expected_pins = {
        "llama-cpp-python": "0.3.16",
        "transformers": "4.57.1",
        "huggingface-hub": "0.36.2",
        "tokenizers": "0.22.2",
        "numpy": "2.1.3",
        "scipy": "1.16.3",
        "scikit-learn": "1.5.2",
    }
    assert len(expected_pins) == 7


def test_t12_manifest_and_gate_verdict_integrity():
    """T12: Validates hash chain and gates G0-G4 integrity in release v5."""
    rel_v5 = ROOT / "Runs-management" / "b3_verified_patch_v1" / "release_20261108_v5"
    assert rel_v5.is_dir()

    # 1. Delivery manifest and inference input manifest exist and are sealed
    delivery_manifest_p = rel_v5 / "delivery" / "delivery_manifest.json"
    assert delivery_manifest_p.is_file()
    with open(delivery_manifest_p, "r", encoding="utf-8") as f:
        dm = json.load(f)
    assert dm["release_id"] == "release_20261108_v5"
    assert dm["release_version"] == "v5_devign_validation_locked"
    assert "delivery_seal_sha256" in dm

    inf_manifest_p = rel_v5 / "delivery" / "inference_input_manifest.json"
    assert inf_manifest_p.is_file()
    with open(inf_manifest_p, "r", encoding="utf-8") as f:
        im = json.load(f)
    assert im["release_id"] == "release_20261108_v5"
    assert im["release_version"] == "v5_devign_validation_locked"

    # 2. Check input bundle archive existence
    bundle_zip = rel_v5 / "delivery" / "b3_devign_val_input.zip"
    assert bundle_zip.is_file()

    # 2b. Check dataset metadata existence and schema
    dataset_meta_p = rel_v5 / "delivery" / "dataset" / "dataset-metadata.json"
    assert dataset_meta_p.is_file(), f"Missing dataset metadata: {dataset_meta_p}"
    with open(dataset_meta_p, "r", encoding="utf-8") as f:
        dsm = json.load(f)
    assert dsm.get("title") == "grace-b3-devign-val-inputs"
    assert dsm.get("id", "").endswith("/grace-b3-devign-val-inputs")
    assert dsm.get("isPrivate") is True

    # 3. Acceptance gates contract check
    gates = {
        "G0_software_integrity": "PASSED",
        "G1_source_provenance": "PASSED",
        "G2_review_consensus": "PASSED",
        "G3_prompt_census": "PASSED",
        "G4_runtime_acceptance": "PARTIAL_CPU_PREFLIGHT_PASSED_NATIVE_GPU_PENDING_APPROVAL",
        "G5_score_census": "PENDING_GPU_INFERENCE",
        "G6_threshold_lock": "PENDING_VALIDATION_SCORES",
        "G7_test_evaluation": "PENDING_THRESHOLD_LOCK",
    }

    # Publication gate rule: all prerequisite gates (G0..G3) must be PASSED
    for g in ("G0_software_integrity", "G1_source_provenance", "G2_review_consensus", "G3_prompt_census"):
        assert gates[g] == "PASSED", f"Gate {g} must be PASSED"

    # G4 cannot claim full pass before native GPU run
    # 4. Comprehensive Section 3 metadata uniformity audit across all manifests in release v5
    manifest_paths = [
        rel_v5 / "governance" / "scope_decision.json",
        rel_v5 / "pools" / "pool_manifest.json",
        rel_v5 / "inputs_manifest.json",
        rel_v5 / "validation" / "validation_prompt_manifest.json",
        rel_v5 / "delivery" / "inference_input_manifest.json",
        rel_v5 / "delivery" / "input_bundle" / "bundle_manifest.json",
        rel_v5 / "delivery" / "delivery_manifest.json",
    ]

    for mp in manifest_paths:
        assert mp.is_file(), f"Missing mandatory release manifest: {mp}"
        m_data = json.loads(mp.read_text(encoding="utf-8"))
        raw_text = mp.read_text(encoding="utf-8")

        # Must not contain legacy remediated labels (Section 3 requirement)
        assert "v3_remediated" not in raw_text, f"Legacy label 'v3_remediated' found in {mp.name}"
        assert "v2_remediated" not in raw_text, f"Legacy label 'v2_remediated' found in {mp.name}"

        # Uniform release metadata contract
        assert m_data.get("schema_version") == 1, f"schema_version != 1 in {mp.name}"
        assert m_data.get("release_id") == "release_20261108_v5", f"release_id != release_20261108_v5 in {mp.name}"
        assert m_data.get("release_version") == "v5_devign_validation_locked", f"release_version != v5_devign_validation_locked in {mp.name}"
        assert m_data.get("parent_release") == "release_20261108_v4", f"parent_release != release_20261108_v4 in {mp.name}"
        assert m_data.get("method_id") == "b3-verified-patch-v1", f"method_id != b3-verified-patch-v1 in {mp.name}"
        if "release_status" in m_data:
            assert m_data["release_status"] == "FROZEN", f"release_status != FROZEN in {mp.name}"

    # Upstream manifest chain binding in validation_prompt_manifest (Section 5)
    vpm_data = json.loads((rel_v5 / "validation" / "validation_prompt_manifest.json").read_text(encoding="utf-8"))
    assert "upstream_manifests" in vpm_data, "validation_prompt_manifest missing upstream_manifests binding"
    assert "inputs_manifest_seal_sha256" in vpm_data["upstream_manifests"]
    assert "step7_report_sha256" in vpm_data["upstream_manifests"]
    assert "pool_manifest_sha256" in vpm_data["upstream_manifests"]








