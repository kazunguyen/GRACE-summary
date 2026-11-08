# AGY-only B3 discovery handoff

No GPT subagents were used. AGY model: `gemini-3.8-flash-medium`.

Accepted workflow: generic schema-only code generation through AGY; coordinator
reviews code, runs independent synthetic tests and executes it locally. Private
train records/indexes are not supplied to accepted AGY tasks or published here.

Use these reviewed worker deliverables:

- `workers/indexer/outputs/discover_local.py`: frozen-bank hash/row gates and
  exhaustive heuristic opposite-label name matching. Passed 12 independent tests.
- `workers/tests/outputs/test_discover_local.py`: synthetic tests; coordinator
  added a resolved-path cleanup guard. Run with workspace TMP/TEMP and
  `PYTHONUTF8=1`, `PYTHONIOENCODING=utf-8` for Windows subprocess diagnostics.
- `workers/review_contract_fix1/outputs/`: accepted guide/checklist.
- `workers/source_fetcher/outputs/fetch_public_source.py`: statically reviewed
  allowlisted, bounded public GET collector. The first real attempt failed TLS
  issuer validation; this is not evidence of missing source relationships.

**Rejected draft:** `workers/review_contract/outputs/` is retained as review
history only. It invented protocol options and suggested editing frozen threshold
files. Do not use it. Its execution ledger records rejection and the follow-up.

The two local train scans reproduce 21,691 Devign and 17,636 REVEAL donors,
26,700/33,947 heuristic combinations, and zero verified/reviewed pairs. Full
local indexes are ignored by Git. This stage does not create an inference-ready
pool. Next: repair trusted CA configuration without disabling certificate checks,
collect source evidence, resolve REVEAL joins and obtain genuine human reviews.

`coordinator_review.json` records acceptance limits and unchanged source seals.
Task prompts, conversation IDs, model usage, returned artifacts and review
statuses remain in the per-worker execution ledgers.
