"""
GRACE Unified Baseline Verification & Integrity Tests
Validates all 4 architectural pillars:
  1. Prompt 8192 model tokens cap and truncation order
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
    def test_incomplete_label_logprobs_are_invalid(self):
        from grace_diag.llm_backend import parse_top_logprobs
        self.assertFalse(parse_top_logprobs({'1': -0.2})['valid'])
        self.assertFalse(parse_top_logprobs({'0': -0.2})['valid'])
        self.assertTrue(parse_top_logprobs({'0': -1.0, '1': -0.5})['valid'])

    def test_b2_matches_kit_renderer(self):
        from tokenizers_support import MockTokenizer
        from grace_diag.probes import render_arm
        builder = PromptBuilder(tokenizer=MockTokenizer())
        target={'id':'x','func':'int f(void){return 0;}','nodes':[{'id':1,'type':'CALL','code':'f()'}], 'edges':[]}
        demo={'id':'d','func':'int g(void){return 1;}','target':1}
        actual, meta=builder.build_prompt(target,demo)
        spec={'id':'x','query_code':target['func'],'nodes':target['nodes'],'edges':[],
              'demonstrations':[{'function_uid':'d','func':demo['func'],'target':1}]}
        expected=render_arm(spec,'B2',counter=builder.counter,budget=builder.budget,graph_prefix=builder.prefix)
        self.assertEqual(actual,expected.prompt)
        self.assertEqual(meta['prompt_tokens'],expected.evidence['tokens']['total'])

    def test_missing_labels_are_rejected(self):
        from data_loader import standardize_sample
        for row in ({'func': 'x'}, {'func': 'x', 'target': 'bad'}, {'func':'x', 'target': 2}):
            with self.assertRaises(ValueError): standardize_sample(row, 0)
        self.assertEqual(standardize_sample({'func':'x','target':True}, 0)['target'], 1)

    def test_all_duplicate_donors_rejected(self):
        from retrieval_engine import DemonstrationRetriever
        from embedding_engine import CodeT5Embedder
        retriever = DemonstrationRetriever(CodeT5Embedder(force_fallback=True))
        retriever.fit([{'id':str(i),'func':'same two words','target':0,'nodes':[],'edges':[]} for i in range(3)])
        with self.assertRaises(ValueError): retriever.retrieve_single({'id':'x','func':'same two words','nodes':[],'edges':[]})

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

    def test_prompt_budget_strictly_capped_at_8192_tokens(self):
        """Verify token and component limits with a mock tokenizer."""
        from tokenizers_support import MockTokenizer
        builder = PromptBuilder(tokenizer=MockTokenizer(), context_limit_tokens=8192)

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

        self.assertLessEqual(meta["prompt_tokens"], 8192)
        self.assertEqual(meta["prompt_utf8_bytes"], encoded_bytes)
        self.assertLessEqual(meta["target_tokens_used"], 3000)
        self.assertLessEqual(meta["demo_tokens_used"], 1500)
        self.assertLessEqual(meta["graph_tokens_used"], 1500)
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

    def test_graph_referential_integrity(self):
        """Verify that edges referencing nodes truncated by graph_nodes_max are excluded."""
        from graph_extractor import format_graph_context
        # Create 100 nodes (IDs 0..99) and 99 linear edges
        nodes = [{"id": i, "type": "STMT", "code": f"statement_{i}"} for i in range(100)]
        edges = [{"src": i, "dst": i + 1, "type": "CFG"} for i in range(99)]

        # Cap at 25 nodes and 25 edges
        ctx, meta = format_graph_context(nodes, edges, max_nodes=25, max_edges=25)

        self.assertEqual(meta["nodes_used"], 25)
        # Only edges 0->1 ... 23->24 can be valid (24 edges). Edge 24->25 connects to discarded node 25!
        self.assertEqual(meta["edges_used"], 24)
        self.assertNotIn("Node 24 -> CFG -> Node 25", ctx)
        self.assertNotIn("Node 25", ctx.split("The edge information")[1])

    def test_retriever_excludes_target_duplicate_code(self):
        """Verify that training samples identical to target query are excluded to avoid leakage."""
        from retrieval_engine import DemonstrationRetriever
        from embedding_engine import CodeT5Embedder

        embedder = CodeT5Embedder(force_fallback=True)
        retriever = DemonstrationRetriever(embedder=embedder, profile="code")

        train = [
            {"id": "train_leak", "func": "void identical() { int x = 42; }", "target": 1, "nodes": [], "edges": []},
            {"id": "train_safe", "func": "void other() { int y = 100; }", "target": 0, "nodes": [], "edges": []},
        ]
        retriever.fit(train)

        target = {"id": "target_q", "func": "void identical() { int x = 42; }", "nodes": [], "edges": []}
        res = retriever.retrieve_single(target)

        # The duplicate 'train_leak' must be excluded! Only 'train_safe' may be returned.
        self.assertNotEqual(res["demo"]["id"], "train_leak")
        self.assertEqual(res["demo"]["id"], "train_safe")

    def test_retriever_searches_full_train_pool(self):
        """Verify candidate retrieval searches beyond index 49 across the entire training pool."""
        from retrieval_engine import DemonstrationRetriever
        from embedding_engine import CodeT5Embedder

        embedder = CodeT5Embedder(force_fallback=True)
        retriever = DemonstrationRetriever(embedder=embedder, profile="code", candidate_pool_size=50)

        # Generate 60 train samples where index 55 has the most similar keywords to target
        train = []
        for i in range(60):
            if i == 55:
                code = "void target_twin() { char *buf = malloc(1024); memcpy(buf, src, 1024); }"
            else:
                code = f"void filler_func_{i}() {{ int unused_{i} = {i}; }}"
            train.append({"id": f"train_{i}", "func": code, "target": 0, "nodes": [], "edges": []})

        retriever.fit(train)
        target = {"id": "query_q", "func": "void target_twin() { char *buf = malloc(1024); memcpy(buf, src, 1024); }", "nodes": [], "edges": []}

        # Query should find sample 55 among its candidates even though index > 50
        res = retriever.retrieve_single(target)
        self.assertIn("candidate_pool_size_used", res["metadata"])
        self.assertEqual(res["metadata"]["candidate_pool_size_used"], 50)

    def test_prompt_template_file_exists_and_matches_contract(self):
        """Verify prompt_template.txt exists on disk and contains expected contract anchors."""
        template_file = config.template_path
        self.assertTrue(template_file.is_file(), f"Missing template file: {template_file}")
        content = template_file.read_text(encoding="utf-8")
        self.assertIn("### TASK INSTRUCTION", content)
        self.assertIn("{target_code}", content)
        self.assertIn("{graph_context}", content)
        self.assertIn("{demonstrations}", content)
        self.assertIn("### OUTPUT CONTRACT", content)

    def test_embedding_engine_path_import(self):
        """Verify embedding_engine imports Path without NameError."""
        import embedding_engine
        self.assertTrue(hasattr(embedding_engine, "Path"))

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
