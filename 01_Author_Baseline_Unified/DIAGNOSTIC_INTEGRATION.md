# Diagnostic integration

The contract is 8192 model tokens including the chat template. Component budgets: target 3000, each demo 1500, graph 1500; prefix <=40 nodes / 80 edges. The pinned Qwen tokenizer is required for real runs. MockTokenizer is only for local tests.

Export with explicit frozen, binary-labelled, graph-enriched JSONL files:

```
python export_diagnostic_specs.py --dataset devign --split validation --train train.jsonl --targets validation.jsonl --other-targets test.jsonl --out data/specs/devign_validation.jsonl
```

The output has specs, a donor JSONL and a manifest with hashes. Use the same full train/validation/test inputs for both split exports. Exact duplicate groups are removed by stripped code text and conflicting labels are excluded. This is not the normalized and near-duplicate audit required for preregistration. --mock-embedding is for integration testing only. The exporter does not create B3 pairs or H2 evidence.

For kit dry-run, pass --protocol diagnostic_kit/configs/protocol.yaml and the donor file, plus an installed model tokenizer. The bundled kit and baseline use the same Figure 6 B2 renderer, 40/80 prefix and chat-token accounting. Verify with the actual tokenizer before inference. The bundled kit marks scores invalid when either label probability is absent; validate tokenizer and backend logprob behavior before AUROC/AUPRC.

For the Transformers baseline, `run_pipeline.py` also writes `logprobs.jsonl`: see RUN_GUIDE.md. The API kit remains top-k based and fails closed if either label is missing. `B2-rep` bypasses cache so that it measures a fresh response. Verify the installed serving backend and whether returned probabilities are unconstrained before using them for the study.

Existing checkpoints from the byte contract must not be reused: use a fresh experiment name. The loader rejects missing/nonbinary labels and the retriever refuses an all-duplicate donor pool. Validation output is exploratory until all provenance and audits are complete.

Prompt B2 uses the vendored Figure 6 renderer; prompt_template.txt is retained only as historical reference. Chat template is counted in total and 64 tokens are reserved by the kit. Historical graph prefix recovered from old prompts is suitable for smoke tests only, not a full CPG dataset.
