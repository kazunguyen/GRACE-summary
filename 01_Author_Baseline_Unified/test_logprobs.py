import json
import math
from types import SimpleNamespace
from unittest.mock import patch

import pytest
import torch

from llm_backbone import LLMClient, score_first_token


class TinyTokenizer:
    def encode(self, text, add_special_tokens=False):
        return {"0": [1], "1": [2]}[text]

    def decode(self, ids, skip_special_tokens=False):
        return {0: "other", 1: "0", 2: "1", 3: "x"}[int(ids[0])]


def test_scores_are_exact_even_if_digits_are_not_top_two():
    logits = torch.tensor([5.0, -1.0, 1.0, 4.0])
    out = score_first_token(logits, TinyTokenizer())
    assert out["score_valid"]
    assert out["logprob_0"] == pytest.approx(torch.log_softmax(logits, 0)[1].item())
    assert out["logprob_1"] == pytest.approx(torch.log_softmax(logits, 0)[2].item())
    assert out["s"] == pytest.approx(1 / (1 + math.exp(-2)))
    assert out["pred_argmax"] == 1
    assert out["top5"][0]["token"] == "other"
    json.dumps(out, allow_nan=False)


def test_bad_tokenization_fails_closed():
    tok = TinyTokenizer()
    tok.encode = lambda text, add_special_tokens=False: [1, 2]
    with pytest.raises(ValueError, match="not exactly one"):
        score_first_token(torch.zeros(4), tok)


def test_mock_never_claims_real_logprobs():
    result = LLMClient(use_mock=True).generate("strcpy")
    assert result["score_method"] == "mock_no_logprobs"
    assert result["score_valid"] is False
    assert "logprob_0" not in result


def test_generate_returns_scores_without_replacing_raw_output():
    client = LLMClient(use_mock=False)
    payload = {"raw_response": "other", **score_first_token(torch.tensor([5.0, -1.0, 1.0, 4.0]), TinyTokenizer())}
    with patch.object(client, "_call_provider", return_value=payload):
        result = client.generate("prompt")
    assert result["raw_response"] == "other"
    assert result["pred_argmax"] == 1
    assert result["score_valid"] is True


def test_pipeline_writes_logprobs_with_identity_and_token_evidence(tmp_path):
    from config import config
    from run_pipeline import run_pipeline

    def fake_generation(prompt):
        return {"raw_response": "1", "request_status": "ok", "request_error": None,
                "attempts": 1, "model": "mock-llm-engine",
                **score_first_token(torch.tensor([0.0, -1.0, 1.0, -2.0]), TinyTokenizer())}

    with patch.object(config, "checkpoint_dir", tmp_path), patch.object(LLMClient, "_mock_generate", side_effect=fake_generation):
        run_pipeline(dataset_name="mock", split="validation", max_targets=2, use_mock=True,
                     experiment_name="scores", output_dir=tmp_path / "out")
    records = [json.loads(line) for line in (tmp_path / "out" / "logprobs.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(records) == 2
    assert all(row["score_valid"] and row["s"] is not None and row["id"] and row["prompt_sha256"] for row in records)
    assert all(row["dataset"] == "mock" and row["split"] == "validation" and row["demo_ids"] for row in records)


def test_repeat_does_not_read_or_write_cache():
    import prompt_builder  # registers bundled diagnostic_kit/src on sys.path
    from grace_diag.llm_backend import BackendConfig, FirstTokenScorer

    scorer = FirstTokenScorer.__new__(FirstTokenScorer)
    scorer.cfg = BackendConfig()
    choice = SimpleNamespace(message=SimpleNamespace(content="1"), logprobs=SimpleNamespace(content=[
        SimpleNamespace(top_logprobs=[SimpleNamespace(token="0", logprob=-2.0), SimpleNamespace(token="1", logprob=-1.0)])]))
    response = SimpleNamespace(choices=[choice], usage=None)
    scorer.client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **kw: response)))
    with patch.object(scorer, "_read_cache", side_effect=AssertionError("cache read")), patch.object(scorer, "_write_cache", side_effect=AssertionError("cache write")):
        assert scorer.score("prompt", use_cache=False).valid
