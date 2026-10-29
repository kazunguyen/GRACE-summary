"""
GRACE Benchmark Evaluator Module
Calculates evaluation metrics compliant with evaluation_contract_v2:
  - Confusion Matrix (TP, TN, FP, FN)
  - Accuracy (Valid only)
  - Precision, Recall, F1
  - Balanced Accuracy, MCC (Matthews Correlation Coefficient)
  - Predicted Vulnerable Rate
  - Invalid Count, Invalid Rate, Coverage
  - Trivial Baselines (Always Vulnerable, Always Non-vulnerable)
"""

from __future__ import annotations

import math
from typing import List, Dict, Any, Optional
from parser import parse_prediction


def compute_metrics_on_population(
    items: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Compute core classification metrics on a given population."""
    if not items:
        return {
            "n": 0,
            "confusion_matrix": {"tp": 0, "tn": 0, "fp": 0, "fn": 0},
            "accuracy_valid": None,
            "precision": None,
            "recall": None,
            "f1": None,
            "balanced_accuracy": None,
            "mcc": None,
            "predicted_positive_rate": None,
        }

    tp = sum(item["prediction"] == 1 and item["ground_truth"] == 1 for item in items)
    tn = sum(item["prediction"] == 0 and item["ground_truth"] == 0 for item in items)
    fp = sum(item["prediction"] == 1 and item["ground_truth"] == 0 for item in items)
    fn = sum(item["prediction"] == 0 and item["ground_truth"] == 1 for item in items)

    n = len(items)
    accuracy = (tp + tn) / n if n > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    balanced_acc = (recall + specificity) / 2.0

    denom = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    mcc = ((tp * tn) - (fp * fn)) / denom if denom > 0 else 0.0

    pos_rate = (tp + fp) / n if n > 0 else 0.0

    return {
        "n": n,
        "confusion_matrix": {"tp": tp, "tn": tn, "fp": fp, "fn": fn},
        "accuracy_valid": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "balanced_accuracy": balanced_acc,
        "mcc": mcc,
        "predicted_positive_rate": pos_rate,
    }


class BenchmarkEvaluator:
    """Evaluates raw model responses against sealed ground-truth labels."""

    def evaluate(
        self,
        records: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        records: list of dicts with:
          - "record_id" (str)
          - "ground_truth" (int: 0 or 1)
          - "raw_response" (str)
          - "request_status" (str, optional)
        """
        parsed_records: List[Dict[str, Any]] = []
        valid_items: List[Dict[str, Any]] = []
        invalid_count = 0

        for r in records:
            res_text = r.get("raw_response", "")
            parse_res = parse_prediction(res_text)

            item = {
                "record_id": r.get("record_id", ""),
                "ground_truth": int(r.get("ground_truth", 0)),
                "prediction": parse_res.prediction,
                "parse_status": parse_res.parse_status,
                "parse_method": parse_res.parse_method,
                "raw_response": res_text,
                "request_status": r.get("request_status", "ok"),
            }
            parsed_records.append(item)

            if parse_res.prediction is not None:
                valid_items.append(item)
            else:
                invalid_count += 1

        total_responses = len(records)
        observed_metrics = compute_metrics_on_population(valid_items)

        # Compute trivial baselines on the same valid population
        always_vuln = compute_metrics_on_population([{**it, "prediction": 1} for it in valid_items])
        always_safe = compute_metrics_on_population([{**it, "prediction": 0} for it in valid_items])

        coverage = len(valid_items) / total_responses if total_responses > 0 else 0.0
        invalid_rate = invalid_count / total_responses if total_responses > 0 else 0.0

        results = {
            "n_total": total_responses,
            "n_valid": len(valid_items),
            "n_invalid": invalid_count,
            "invalid_rate": invalid_rate,
            "coverage": coverage,
            "metric_population": "valid_predictions_only",
            **observed_metrics,
            "trivial_baselines": {
                "always_predict_vulnerable": always_vuln,
                "always_predict_non_vulnerable": always_safe,
            },
        }

        return {
            "metrics": results,
            "predictions": parsed_records,
        }
