"""
GRACE Unified Baseline Verification & Integrity Tests
Validates all 4 architectural pillars:
  1. Prompt 8192 UTF-8 bytes cap and truncation order
  2. Strict binary output parser (no illegal heuristic fallback)
  3. Hybrid reranking formula (0.7 code Jaccard + 0.3 AST)
  4. Benchmark metrics calculation on valid population
  5. End-to-end pipeline execution in mock mode
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from config import config
from parser import parse_prediction
from prompt_builder import PromptBuilder
from retrieval_engine import compute_hybrid_score, jaccard_similarity, ast_similarity
from evaluator import BenchmarkEvaluator, compute_metrics_on_population
from run_pipeline import run_pipeline


class BaselineIntegrityTests(unittest.TestCase):
    def test_strict_parser_compliance(self):
        """Verify strict binary parser behavior."""
        # Exact valid outputs
        self.assertEqual(parse_prediction("1").prediction, 1)
        self.assertEqual(parse_prediction("0").prediction, 0)
        self.assertEqual(parse_prediction("Some reasoning...\n1").prediction, 1)
        self.assertEqual(parse_prediction("Some reasoning...\n0").prediction, 0)

        # Invalid outputs must NOT be coerced to 0 or 1
        self.assertIsNone(parse_prediction("").prediction)
        self.assertIsNone(parse_prediction("Vulnerable").prediction)
        self.assertIsNone(parse_prediction("Non-vulnerable").prediction)
        self.assertIsNone(parse_prediction("1\nExplanation afterwards").prediction)
        self.assertIsNone(parse_prediction("The answer is 1.").prediction)
        self.assertIsNone(parse_prediction("Safe").prediction)

    def test_prompt_budget_strictly_capped_at_8192_bytes(self):
        """Verify that prompts never exceed 8192 UTF-8 bytes."""
        builder = PromptBuilder(context_limit_bytes=8192)

        # Create gigantic target and demo
        huge_target = {
            "func": "void huge_function() {\n" + ("    int a = 1;\n" * 2000) + "}",
            "nodes": [{"id": i, "type": "STMT", "code": f"statement_{i}"} for i in range(100)],
            "edges": [{"src": i, "dst": i + 1, "type": "CFG"} for i in range(99)],
        }
        huge_demo = {
            "target": 1,
            "func": "void huge_demo() {\n" + ("    int demo_var = 2;\n" * 1500) + "}",
        }

        prompt, meta = builder.build_prompt(huge_target, huge_demo)
        encoded_bytes = len(prompt.encode("utf-8"))

        self.assertLessEqual(encoded_bytes, 8192)
        self.assertEqual(meta["prompt_utf8_bytes"], encoded_bytes)
        self.assertLessEqual(meta["graph_nodes_used"], 40)
        self.assertLessEqual(meta["graph_edges_used"], 80)

    def test_hybrid_reranker_formula(self):
        """Verify 0.7 * Jaccard + 0.3 * AST similarity."""
        code1 = "int a = 1; int b = 2;"
        code2 = "int a = 1; int c = 3;"
        ast1 = "METHOD PARAM STMT"
        ast2 = "METHOD PARAM STMT"

        j = jaccard_similarity(code1, code2)
        a = ast_similarity(ast1, ast2)
        hybrid, j_res, a_res = compute_hybrid_score(code1, ast1, code2, ast2)

        self.assertAlmostEqual(j, j_res)
        self.assertAlmostEqual(a, a_res)
        expected = 0.7 * j + 0.3 * a
        self.assertAlmostEqual(hybrid, expected)

    def test_evaluator_metrics_on_valid_population(self):
        """Verify metric calculation and invalid rate tracking."""
        records = [
            {"record_id": "1", "ground_truth": 1, "raw_response": "1"},  # TP
            {"record_id": "2", "ground_truth": 0, "raw_response": "0"},  # TN
            {"record_id": "3", "ground_truth": 0, "raw_response": "1"},  # FP
            {"record_id": "4", "ground_truth": 1, "raw_response": "0"},  # FN
            {"record_id": "5", "ground_truth": 1, "raw_response": "Invalid response"},  # Invalid
        ]
        evaluator = BenchmarkEvaluator()
        result = evaluator.evaluate(records)
        metrics = result["metrics"]

        self.assertEqual(metrics["n_total"], 5)
        self.assertEqual(metrics["n_valid"], 4)
        self.assertEqual(metrics["n_invalid"], 1)
        self.assertAlmostEqual(metrics["invalid_rate"], 0.2)
        self.assertAlmostEqual(metrics["coverage"], 0.8)

        cm = metrics["confusion_matrix"]
        self.assertEqual(cm["tp"], 1)
        self.assertEqual(cm["tn"], 1)
        self.assertEqual(cm["fp"], 1)
        self.assertEqual(cm["fn"], 1)
        self.assertAlmostEqual(metrics["accuracy_valid"], 0.5)

    def test_end_to_end_mock_pipeline(self):
        """Verify that the full pipeline executes cleanly and generates all artifacts."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_path = Path(tmp_dir) / "test_run"
            exp_name = "unit_test_run"
            ckpt_path = config.checkpoint_dir / f"{exp_name}_checkpoint.jsonl"
            if ckpt_path.exists():
                ckpt_path.unlink()
            try:
                metrics = run_pipeline(
                    dataset_name="mock",
                    sample_ratio=1.0,
                    max_targets=10,
                    profile="code",
                    use_mock=True,
                    experiment_name=exp_name,
                    output_dir=out_path,
                )

                self.assertTrue((out_path / "prompts.jsonl").is_file())
                self.assertTrue((out_path / "raw_responses.jsonl").is_file())
                self.assertTrue((out_path / "predictions.jsonl").is_file())
                self.assertTrue((out_path / "evaluation.json").is_file())
                self.assertTrue((out_path / "report.md").is_file())
                self.assertEqual(metrics["n_total"], 10)
                self.assertGreaterEqual(metrics["n_valid"], 1)
            finally:
                if ckpt_path.exists():
                    ckpt_path.unlink()


if __name__ == "__main__":
    unittest.main()
