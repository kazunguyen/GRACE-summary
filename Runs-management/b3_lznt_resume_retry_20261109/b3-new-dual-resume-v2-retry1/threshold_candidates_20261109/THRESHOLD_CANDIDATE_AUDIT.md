# B3 new-algorithm results, runtime, and threshold candidate audit

## Verdict

- **Validation results:** accepted for the next threshold-review step. Complete census: Devign 2,732/2,732 and REVEAL 2,273/2,273; all records have valid score and response. Record IDs, labels, prompts, score/logprob relation, input roots, and run identities passed the independent audit in `execution_audit.json`.
- **Runtime contract:** PASS for the runtime sessions referenced by the scored records. The 7-package contract SHA is `4c9c3bcff5e9fd32532d7edf85df7a961e45ec9c64bee3df8833d986a2eb276e`; pinned packages, runner hash, model/record identity, native offload logs, two Tesla T4s, 49/49 layers, locked context/batch settings, and build-log hashes match. Original and resumed REVEAL records have separate provenance sessions, both matching the same contract.
- **Threshold calculation:** both dataset candidates were computed from raw validation records, not copied from prior reports or historical B3. Independent MCC implementations agree on every grid point. The numbers are computationally ready for governance review.
- **Formal lock:** **not yet sealed**. Plan Step 12 requires review of the full grid and explicit confirmation of authority to apply a threshold to this amended B3 scope. The input roots record that no new scope-ratification timestamp is claimed. No test run should start until a separate lock is approved and sealed.
- Frozen `configs/thresholds.json` and `configs/thresholds_flat.json` remain unchanged.

## Computed validation threshold candidates

| Dataset | N valid / expected | tau candidate | MCC | TP | TN | FP | FN | Tie set |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Devign | 2,732 / 2,732 | 0.99 | 0.0501474890867987 | 491 | 982 | 563 | 696 | {0.99} |
| REVEAL | 2,273 / 2,273 | 0.01 | 0.06487856711606896 | 189 | 383 | 1,680 | 21 | {0.01} |

The extreme grid-edge optima are reported as computed. They were not adjusted or replaced. MCC is optimized on only the prescribed 99-point grid; no continuous search was substituted.

## Exact calculation and cross-check

For each dataset, labels were joined by ID to the frozen validation prompt bundle. Only finite, valid scores were fitted; here valid count equals the full census. For every `tau = i/100`, `i=1..99`, prediction is `s >= tau`; TP/TN/FP/FN and MCC are retained. Undefined MCC points are excluded. MCC ties within `1e-9` choose the threshold closest to 0.5, then the lower threshold.

A separate explicit confusion-count implementation was compared with `Runs-management/validation_lock.py::pick_threshold`. All 99 MCC values and the selected tau/MCC matched (MCC absolute tolerance `1e-12`). Evidence files include the full grid, score-evidence digest, validation-record hash, root/prompt/pool/model/tokenizer/runtime identities, and candidate file SHA.

## Candidate artifacts

- Devign: `threshold_candidates_20261109/devign_threshold_candidate.json`
- REVEAL: `threshold_candidates_20261109/reveal_threshold_candidate.json`
- Summary: `threshold_candidates_20261109/candidate_summary.json`
- Result/runtime audit: `execution_audit.json`

Candidate status is `CANDIDATES_COMPUTED_NOT_LOCKED`. No test artifact was read, no test inference was run, and no frozen threshold/config file was modified.
