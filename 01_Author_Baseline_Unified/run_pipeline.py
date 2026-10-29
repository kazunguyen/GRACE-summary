"""
GRACE Unified Baseline End-to-End Orchestrator
CLI entry point to reproduce, run, and benchmark the author's original GRACE baseline.
Compliant with evaluation_contract_v2 (context 8192 bytes, strict parser, valid metrics).
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

# Ensure current directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import config
from data_loader import load_dataset
from embedding_engine import CodeT5Embedder
from retrieval_engine import DemonstrationRetriever
from prompt_builder import PromptBuilder
from llm_backbone import LLMClient
from evaluator import BenchmarkEvaluator

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("GRACE-Baseline")


def write_jsonl(path: Path, items: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def generate_markdown_report(metrics: Dict[str, Any], exp_name: str, out_file: Path) -> None:
    cm = metrics.get("confusion_matrix", {})
    tp, tn, fp, fn = cm.get("tp", 0), cm.get("tn", 0), cm.get("fp", 0), cm.get("fn", 0)

    acc = metrics.get("accuracy_valid", 0.0) or 0.0
    prec = metrics.get("precision", 0.0) or 0.0
    rec = metrics.get("recall", 0.0) or 0.0
    f1 = metrics.get("f1", 0.0) or 0.0
    ba = metrics.get("balanced_accuracy", 0.0) or 0.0
    mcc = metrics.get("mcc", 0.0) or 0.0

    lines = [
        f"# Báo cáo thực nghiệm: {exp_name}",
        "",
        "## 1. Thông số tổng quan",
        f"- Tổng số mẫu kiểm thử: {metrics.get('n_total', 0)}",
        f"- Số phản hồi hợp lệ (Valid): {metrics.get('n_valid', 0)} ({metrics.get('coverage', 0)*100:.2f}%)",
        f"- Số phản hồi không hợp lệ (Invalid): {metrics.get('n_invalid', 0)} ({metrics.get('invalid_rate', 0)*100:.2f}%)",
        "",
        "## 2. Ma trận nhầm lẫn (Confusion Matrix)",
        f"- True Positives (TP): {tp}",
        f"- True Negatives (TN): {tn}",
        f"- False Positives (FP): {fp}",
        f"- False Negatives (FN): {fn}",
        "",
        "## 3. Chỉ số đo lường hiệu năng (Benchmark Metrics)",
        f"- **Accuracy (Valid)**: {acc * 100:.2f}%",
        f"- **Precision**: {prec * 100:.2f}%",
        f"- **Recall**: {rec * 100:.2f}%",
        f"- **F1-Score**: {f1 * 100:.2f}%",
        f"- **Balanced Accuracy**: {ba * 100:.2f}%",
        f"- **MCC**: {mcc:.4f}",
        "",
        "## 4. Trivial Baselines Đối chứng",
        f"- Always Predict Vulnerable (All 1): Accuracy = {metrics.get('trivial_baselines', {}).get('always_predict_vulnerable', {}).get('accuracy_valid', 0)*100:.2f}%",
        f"- Always Predict Non-vulnerable (All 0): Accuracy = {metrics.get('trivial_baselines', {}).get('always_predict_non_vulnerable', {}).get('accuracy_valid', 0)*100:.2f}%",
        "",
        "> Lưu ý: Metric tính nghiêm ngặt trên tập Valid; các phản hồi sai format bị coi là Invalid và không gán ép nhãn 0/1.",
    ]
    out_file.write_text("\n".join(lines), encoding="utf-8")


def run_pipeline(
    dataset_name: str = "devign",
    sample_ratio: float = 1.0,
    max_targets: int | None = None,
    profile: str = "code",
    use_mock: bool = False,
    experiment_name: str = "grace_baseline_unified",
    output_dir: Path | None = None,
) -> Dict[str, Any]:
    out_dir = output_dir or (config.output_dir / experiment_name)
    out_dir.mkdir(parents=True, exist_ok=True)
    ckpt_file = config.checkpoint_dir / f"{experiment_name}_checkpoint.jsonl"

    print("\n" + "=" * 70)
    print("  GRACE AUTHOR BASELINE - UNIFIED EXECUTION PIPELINE")
    print("=" * 70)
    print(f"[*] Experiment : {experiment_name}")
    print(f"[*] Dataset    : {dataset_name} (ratio: {sample_ratio}, max_targets: {max_targets})")
    print(f"[*] Profile    : {profile} (code = CodeT5+Whitening, paper = t-SNE)")
    print(f"[*] Mode       : {'MOCK (Offline dry-run)' if use_mock else 'PINNED LOCAL MODEL'}")
    print(f"[*] Output Dir : {out_dir}")
    print("=" * 70)

    # 1. Load Data
    logger.info("Loading training pool (train split)...")
    train_samples = load_dataset(dataset_name, split="train", sample_ratio=1.0, max_samples=None, use_mock=use_mock)
    logger.info("Loaded %d training samples for candidate pool.", len(train_samples))

    logger.info("Loading evaluation queries (test split)...")
    test_samples = load_dataset(dataset_name, split="test", sample_ratio=sample_ratio, max_samples=max_targets, use_mock=use_mock)
    logger.info("Loaded %d evaluation samples.", len(test_samples))

    # 2. Fit Retrieval Engine
    logger.info("Fitting Demonstration Retrieval Engine on train set (%s profile)...", profile)
    embedder = CodeT5Embedder(force_fallback=use_mock)
    retriever = DemonstrationRetriever(embedder=embedder, profile=profile)
    retriever.fit(train_samples)

    # 3. Prompt Assembly adhering to contract (8192 bytes limit)
    logger.info("Assembling prompts strictly capped at %d UTF-8 bytes...", config.context_limit_bytes)
    prompt_builder = PromptBuilder(
        template_path=config.template_path,
        context_limit_bytes=config.context_limit_bytes,
        graph_nodes_max=config.graph_nodes_max,
        graph_edges_max=config.graph_edges_max,
        target_code_max_chars=config.target_code_max_chars,
        standard_demo_max_chars=config.standard_demo_max_chars,
    )

    prompts = []
    for idx, target in enumerate(test_samples):
        # Retrieve demonstration from candidate pool (searched over full train pool, excluding duplicates)
        retrieval_res = retriever.retrieve_single(target)
        best_demo = retrieval_res["demo"]

        prompt_str, trunc_meta = prompt_builder.build_prompt(target, demonstration_sample=best_demo)
        prompts.append({
            "record_id": target["id"],
            "ground_truth": target["target"],
            "prompt": prompt_str,
            "truncation_metadata": trunc_meta,
            "retrieval_metadata": retrieval_res["metadata"],
        })

    write_jsonl(out_dir / "prompts.jsonl", prompts)
    logger.info("Wrote %d prompts to %s/prompts.jsonl", len(prompts), out_dir)

    # 4. LLM Inference with JSONL Checkpointing
    logger.info("Initializing LLM client (use_mock=%s)...", use_mock)
    client = LLMClient(use_mock=use_mock)

    # Load existing checkpoints if any
    completed_responses = {}
    if ckpt_file.is_file():
        logger.info("Found existing checkpoint file: %s. Resuming...", ckpt_file)
        with ckpt_file.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        record = json.loads(line)
                        completed_responses[record["record_id"]] = record
                    except Exception:
                        pass
        logger.info("Resumed %d already completed responses.", len(completed_responses))

    raw_responses = []
    total = len(prompts)
    with ckpt_file.open("a", encoding="utf-8") as ckpt_f:
        for idx, item in enumerate(prompts):
            rid = item["record_id"]
            if rid in completed_responses:
                raw_responses.append(completed_responses[rid])
                continue

            gen_res = client.generate(item["prompt"])
            response_record = {
                "record_id": rid,
                "ground_truth": item["ground_truth"],
                "raw_response": gen_res["raw_response"],
                "request_status": gen_res["request_status"],
                "request_error": gen_res["request_error"],
                "attempts": gen_res["attempts"],
                "model": gen_res["model"],
                "model_revision": gen_res.get("model_revision"),
            }
            ckpt_f.write(json.dumps(response_record, ensure_ascii=False) + "\n")
            ckpt_f.flush()
            os.fsync(ckpt_f.fileno())

            raw_responses.append(response_record)
            if (idx + 1) % 10 == 0 or (idx + 1) == total:
                logger.info("Inference progress: %d/%d completed.", idx + 1, total)

    write_jsonl(out_dir / "raw_responses.jsonl", raw_responses)

    # 5. Benchmark Evaluation
    logger.info("Evaluating predictions using strict contract parser...")
    evaluator = BenchmarkEvaluator()
    eval_result = evaluator.evaluate(raw_responses)

    metrics = eval_result["metrics"]
    predictions = eval_result["predictions"]

    write_jsonl(out_dir / "predictions.jsonl", predictions)
    (out_dir / "evaluation.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    generate_markdown_report(metrics, experiment_name, out_dir / "report.md")

    print("\n" + "#" * 70)
    print("  EVALUATION SUMMARY REPORT")
    print("#" * 70)
    print(f"Total Queries : {metrics.get('n_total')}")
    print(f"Valid / Invalid: {metrics.get('n_valid')} valid ({metrics.get('coverage')*100:.1f}%) | {metrics.get('n_invalid')} invalid ({metrics.get('invalid_rate')*100:.1f}%)")
    print(f"Accuracy Valid : {metrics.get('accuracy_valid')*100:.2f}%")
    print(f"Precision      : {metrics.get('precision')*100:.2f}%")
    print(f"Recall         : {metrics.get('recall')*100:.2f}%")
    print(f"F1-Score       : {metrics.get('f1')*100:.2f}%")
    print(f"Balanced Acc.  : {metrics.get('balanced_accuracy')*100:.2f}%")
    print(f"MCC            : {metrics.get('mcc'):.4f}")
    print("=" * 70)
    print(f"All artifacts saved to: {out_dir}\n")

    return metrics


def main():
    parser = argparse.ArgumentParser(description="GRACE Unified Baseline Runner")
    parser.add_argument("--dataset", default="devign", choices=["devign", "reveal", "bigvul", "mock"], help="Target dataset")
    parser.add_argument("--sample-ratio", type=float, default=1.0, help="Sampling ratio for test set (0.0 < ratio <= 1.0)")
    parser.add_argument("--max-targets", type=int, default=None, help="Maximum number of test targets to evaluate")
    parser.add_argument("--profile", default="code", choices=["code", "paper"], help="Baseline profile (code or paper)")
    parser.add_argument("--mock", action="store_true", help="Run with deterministic offline mock LLM and mock data")
    parser.add_argument("--experiment-name", default="grace_baseline_unified", help="Experiment identifier")
    parser.add_argument("--output-dir", default=None, help="Directory to save output artifacts")

    args = parser.parse_args()

    out_dir = Path(args.output_dir) if args.output_dir else None
    run_pipeline(
        dataset_name=args.dataset,
        sample_ratio=args.sample_ratio,
        max_targets=args.max_targets,
        profile=args.profile,
        use_mock=args.mock,
        experiment_name=args.experiment_name,
        output_dir=out_dir,
    )


if __name__ == "__main__":
    main()
