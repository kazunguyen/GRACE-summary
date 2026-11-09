"""Synthetic software checks only, with the actual local pinned tokenizer.

All fixture reviews are explicitly synthetic. No real pair admission or inference.
Does not call the original smoke test, which writes historical preview artifacts.
"""
from fractions import Fraction
import json
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "01_Author_Baseline_Unified/diagnostic_kit/src"))
from grace_diag.amended_b3 import VerifiedPairSelector
from grace_diag.contrastive_pair_builder import normalize_code_tokens
from grace_diag.probes import _flip_words
from grace_diag.token_budget import TokenCounter

fixtures = runpy.run_path(str(ROOT / "tests/test_amended_b3.py"))
pair_a, bank_a = fixtures["fixture_pair"]("SYNTHETIC-a")
pair_b, bank_b = fixtures["fixture_pair"]("SYNTHETIC-b", "parse_header")
selector = VerifiedPairSelector([pair_b, pair_a], bank_a | bank_b, "devign")
snapshot = ROOT / "11_Arm_B1H2_Evidence/tokenizer_cache_v6/models--Qwen--Qwen3-Coder-30B-A3B-Instruct/snapshots/b2cff646eb4bb1d68355c01b18ae02e7cf42d120"
counter = TokenCounter(str(snapshot))
assert counter.approx is False
records = []
for i, code in enumerate([
    "int copy_item(char *d, char *s, unsigned n) { memcpy(d,s,n); return 0; }",
    "int parse_header(unsigned n) { if(n > 16) return -1; return 0; }",
    "int release_item(void *p) { free(p); return 0; }",
]):
    target = {"id": f"SYNTHETIC-ONLY-{i}", "query_code": code,
              "nodes": [{"id": 0, "type": "METHOD", "code": "synthetic"}], "edges": []}
    family = selector.render_family(target, counter)
    assert family == selector.render_family(target, counter)
    chosen, demos, selection = selector.select(code)
    q = set(normalize_code_tokens(code))
    expected = []
    for pair in (pair_a, pair_b):
        tokens = [set(normalize_code_tokens(d["func"])) for d in selector.demos[pair["pair_id"]]]
        score = sum((Fraction(len(q & t), len(q | t)) if q and t else Fraction(0)
                     for t in tokens), Fraction(0)) / 2
        expected.append((score, pair["pair_id"]))
    best = sorted(expected, key=lambda r: (-r[0], r[1]))[0]
    assert chosen["pair_id"] == best[1]
    assert Fraction(selection["score_numerator"], selection["score_denominator"]) == best[0]
    base = family["B3"]["prompt"]
    assert family["B3-nodiff"]["prompt"] == base.replace("\n\nKey difference: " + chosen["key_difference"], "")
    vulnerable = "The following example is Vulnerable.\n" + demos[0]["func"].strip()
    patched = "The following example is Non-vulnerable.\n" + demos[1]["func"].strip()
    assert family["B3-swap"]["prompt"] == base.replace(vulnerable + "\n\n" + patched, patched + "\n\n" + vulnerable)
    assert family["B3-flip"]["prompt"] == base.replace(vulnerable, vulnerable.replace("is Vulnerable.", "is Non-vulnerable.")).replace(patched, patched.replace("is Non-vulnerable.", "is Vulnerable.")).replace("Key difference: " + chosen["key_difference"], "Key difference: " + _flip_words(chosen["key_difference"]))
    for row in family.values():
        assert row["evidence"]["tokens"]["total"] + 64 <= 8192
        assert all(d["tokens"] <= 1500 and not d["truncated"] for d in row["evidence"]["demo"]["demos"])
        assert row["evidence"]["tokens"]["graph"] <= 1500
        assert row["evidence"]["tokens"]["code"] <= 3000
        records.append({**row, "test_fixture": True, "inference_allowed": False})
    try:
        selector.render_family({**target, "label": 1}, counter)
    except ValueError as exc:
        assert "never labels" in str(exc)
    else:
        raise AssertionError("Target label guard did not reject label")
summary = {"status": "PASS_SYNTHETIC_SOFTWARE_ONLY", "targets": 3,
           "family_outputs": len(records), "tokenizer_approx": counter.approx,
           "exact_ranking_determinism_probe_transformations_budgets_and_label_guard_pass": True,
           "real_pairs_reviewed": 0, "inference_performed": False}
(OUT / "synthetic_smoke_outputs.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(OUT / "exact_tokenizer_smoke.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary))
