"""Synthetic fixtures verify software behavior, not actual pair security quality."""
from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path

import pytest

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
    snapshot = Path("C:/MY-FILES/LAB-THAY-THO/tmp/grace_validation_hf/hub/models--Qwen--Qwen3-Coder-30B-A3B-Instruct/snapshots/b2cff646eb4bb1d68355c01b18ae02e7cf42d120")
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
