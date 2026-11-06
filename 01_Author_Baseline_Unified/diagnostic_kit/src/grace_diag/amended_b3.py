"""Versioned B3 selector for the proposed 2026-11-06 amendment.

Does not replace the historical selector. Source authenticity/security meaning are
human review obligations; hashes and local diffs alone cannot establish them.
"""
from __future__ import annotations

from copy import deepcopy
from difflib import SequenceMatcher, unified_diff
from fractions import Fraction
import hashlib
import json
import re

from .contrastive_pair_builder import normalize_code_tokens

METHOD = "b3-verified-patch-v1"
ARMS = ("B3", "B3-nodiff", "B3-swap", "B3-flip")


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def payload_hash(pair):
    """Reviewer decisions bind all evidence and explanation, excluding reviews."""
    payload = {k: v for k, v in pair.items() if k != "reviews"}
    return digest(json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")))


def function_hint(code):
    """Discovery heuristic, never a source-identity/security verification."""
    names = re.findall(r"([A-Za-z_]\w*)\s*\(", code.split("{", 1)[0])
    return names[0] if names else None


def patch_text(before, after):
    return "".join(unified_diff(before.splitlines(True), after.splitlines(True),
                                fromfile="vulnerable", tofile="patched"))


def changed_lines(before, after):
    left, right = before.splitlines(), after.splitlines()
    changes = []
    for op, a, b, c, d in SequenceMatcher(None, left, right, autojunk=False).get_opcodes():
        if op != "equal":
            changes.append({"operation": op, "before_start": a + 1,
                            "before_lines": left[a:b], "after_start": c + 1,
                            "after_lines": right[c:d]})
    return changes


def validate_pair(pair, bank, dataset, *, require_reviews=True):
    """Reject unrelated/unreviewed pairs; no keyword-derived security claims.

    bank must be supplied by the frozen-bank loader, not by a target/spec file.
    Each source function is archived verbatim in the evidence record. Two named
    reviewers must check it against the real repository revisions and source diff.
    """
    if pair.get("dataset") != dataset or not pair.get("pair_id"):
        raise ValueError("Missing pair ID or dataset mismatch")
    source = pair.get("source", {})
    for key in ("repository", "path", "function", "fix_commit", "parent_commit",
                "source_url", "security_rationale", "before", "after", "diff"):
        if not isinstance(source.get(key), str) or not source[key].strip():
            raise ValueError("Missing source evidence: " + key)
    for key in ("fix_commit", "parent_commit"):
        if not re.fullmatch(r"[0-9a-f]{40}", source[key]):
            raise ValueError("Full source revision required")
    if source["fix_commit"] == source["parent_commit"]:
        raise ValueError("Source revisions must differ")
    ids = [pair.get("vulnerable_id"), pair.get("patched_id")]
    if ids[0] == ids[1] or any(uid not in bank for uid in ids):
        raise ValueError("Both distinct donors must belong to frozen clean train bank")
    demos = [bank[uid] for uid in ids]
    if [d["target"] for d in demos] != [1, 0]:
        raise ValueError("Donor labels must be vulnerable=1, patched=0")
    for d, side in zip(demos, ("before", "after")):
        if d.get("dataset") != dataset or d.get("split") != "train":
            raise ValueError("Cross-dataset or non-train donor")
        if d["func"] != source[side] or pair.get(side + "_sha256") != digest(d["func"]):
            raise ValueError("Source/donor code or hash mismatch")
        if function_hint(d["func"]) != source["function"]:
            raise ValueError("Function hint differs; explicit source identity resolution required")
    if source["before"] == source["after"] or source["diff"] != patch_text(source["before"], source["after"]):
        raise ValueError("Missing or mismatched source function diff")
    changes = changed_lines(source["before"], source["after"])
    if pair.get("changed_lines") != changes:
        raise ValueError("Changed-line evidence mismatch")
    if not pair.get("key_difference", "").strip():
        raise ValueError("Reviewed difference required; no generic fallback")
    if require_reviews:
        reviews = pair.get("reviews", [])
        if len(reviews) != 2 or len({r.get("reviewer") for r in reviews}) != 2:
            raise ValueError("Two distinct reviewers required")
        for r in reviews:
            if (not r.get("reviewer") or not r.get("reviewed_at") or
                r.get("decision") != "approve" or r.get("payload_sha256") != payload_hash(pair) or
                not all(r.get(k) is True for k in ("same_function_verified", "security_fix_verified",
                                                   "source_revisions_verified", "explanation_supported"))):
                raise ValueError("Unresolved, stale or incomplete pair review")
    return deepcopy(demos)


class VerifiedPairSelector:
    def __init__(self, pairs, bank, dataset):
        if not pairs:
            raise ValueError("No verified pair pool: B3 must pause")
        self.dataset = dataset
        self.pairs = deepcopy(pairs)
        if len({p["pair_id"] for p in pairs}) != len(pairs):
            raise ValueError("Duplicate stable pair ID")
        self.demos = {p["pair_id"]: validate_pair(p, bank, dataset) for p in self.pairs}
        self.tokens = {pid: [set(normalize_code_tokens(d["func"])) for d in ds]
                       for pid, ds in self.demos.items()}

    def select(self, query_code):
        """Exhaustive exact mean Jaccard. No top-k shortcut; no target label API."""
        q = set(normalize_code_tokens(query_code))
        def score(p):
            return sum((Fraction(len(q & t), len(q | t)) if q and t else Fraction(0)
                        for t in self.tokens[p["pair_id"]]), Fraction(0)) / 2
        ranked = sorted(((score(p), p) for p in self.pairs), key=lambda x: (-x[0], x[1]["pair_id"]))
        s, p = ranked[0]
        return deepcopy(p), deepcopy(self.demos[p["pair_id"]]), {
            "method": METHOD, "pair_id": p["pair_id"], "pair_payload_sha256": payload_hash(p),
            "score_numerator": s.numerator, "score_denominator": s.denominator,
            "mean_jaccard": float(s), "eligible_pair_count": len(self.pairs),
        }

    def render_family(self, target, counter):
        """Use the registered renderer and reject lost causal evidence.

        Requires exact tokenizer. Keeps complete donor functions and explanation;
        an oversized chosen pair stops generation instead of changing the ranking.
        """
        from .probes import render_arm, _flip_words
        if counter.approx:
            raise ValueError("Exact registered tokenizer required")
        if set(target) - {"id", "query_code", "nodes", "edges"}:
            raise ValueError("Target accepts only ID, code and graph, never labels/demo hints")
        pair, demos, selection = self.select(target["query_code"])
        spec = {**deepcopy(target), "demonstrations_pair": demos,
                "security_difference": pair["key_difference"]}
        outputs = {}
        for arm in ARMS:
            row = render_arm(spec, arm, counter=counter)
            ev = row.evidence
            if ev["truncated"]["demo"] or (ev["demo"].get("diff_block") or {}).get("truncated"):
                raise ValueError("Selected pair/explanation exceeds budget: causal evidence would be lost")
            expected_diff = _flip_words(pair["key_difference"]) if arm == "B3-flip" else pair["key_difference"]
            if arm != "B3-nodiff" and "Key difference: " + expected_diff not in row.prompt:
                raise ValueError("Explanation missing from displayed prompt")
            if any(d["func"].strip() not in row.prompt for d in demos):
                raise ValueError("Supporting source lines missing from displayed prompt")
            outputs[arm] = {"id": target["id"], "arm": arm, "prompt": row.prompt,
                            "prompt_sha256": ev["prompt_sha256"],
                            "method": METHOD, "selection": selection, "evidence": ev,
                            "threshold_from": "B3" if arm in ("B3-swap", "B3-flip") else arm}
        return outputs
