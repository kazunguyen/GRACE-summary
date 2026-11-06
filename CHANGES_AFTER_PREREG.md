# Changes and exposure record for OSF submission

The historical `prereg-v1` Git tag predates the current OSF package. It is not evidence that the current protocol or threshold seal preceded the historical test runs. No OSF registration URL or approval timestamp has been recorded yet.

## 2026-11-03 — pre-submission disclosure correction

- Corrected `configs/protocol.yaml`, its diagnostic-kit copy, and `configs/protocol_en.yaml` to disclose Tier 1 test metrics, B2-flip Devign test raw-label exposure (230 samples), and partial B2-rand validation inference.
- Documented the executed `llama-cpp-python 0.3.16` full-vocabulary-logit scoring path. API top-k handling remains a separate conditional rule. No inference output was changed or rerun by this documentation correction.
- Resealed `configs/thresholds.json` and its diagnostic-kit copy because the corrected protocol has a new SHA-256. All 14 threshold **values remain identical**. The preceding seal and protocol hashes are retained in metadata and Git history; `locked_utc` now records this reseal, not the original validation fitting time. This reseal does not turn earlier test results into prospective results.
- Updated both OSF submission guides and the package README to remove zero-test-exposure claims. A registration URL and timestamp must be added only after actual OSF approval, without changing the submitted PDF/ZIP bytes.

Future changes after OSF registration must be appended here with the date, reason, affected analyses and whether they are exploratory.

## 2026-11-04 — Kaggle validation packaging

- Packaged audited validation prompts and portable notebooks for B1-full, B1-shuf, B2-nolabel, B2-labelonly, B2-rep and B2-rand. B2-rand resumes I-09. B2-rep uses an isolated checkpoint and fresh inference.
- Scope: Step 5 validation delivery. No model calls, threshold fitting, test results or registered analysis rules changed. Operational packaging only. This entry introduces no exploratory analysis.

## 2026-11-04 — B2-rep provenance and Kaggle backend clarification

- Record and validate repeat=true and tag=repeat for the B2-rep validation runner so resume can enforce the registered repeat identity. Legacy checkpoints without those fields require a separate provenance review.
- For these Kaggle notebooks use the direct llama-cpp-python 0.3.16, Q4_K_M, full-logit execution path documented in the submitted preregistration narrative. The frozen YAML serving line lists separate server alternatives. The delivery manifest and README document the execution choice.
- Scope: Step 5 validation provenance and repeat isolation for RQ2. This operational clarification changes no prompt, threshold, frozen artifact, or analysis rule and introduces no exploratory analysis.

## 2026-11-04 — B2-flip inherited threshold and Kaggle session guard

- Updated the B2-flip Kaggle runner to validate all current validation records, inherit the preregistered B2 threshold for each dataset, and require that inherited lock before entering test. The runner no longer independently optimizes tau for B2-flip. Source threshold file hashes and validation identities are recorded in the run worklog and output lock.
- Changed the output root to isolate this run from older migration outputs. Set a 9.5-hour runtime budget and a 10-minute checkpoint reserve under Kaggle's documented 12-hour CPU/GPU session cap ([Kaggle Notebooks documentation](https://www.kaggle.com/docs/notebooks)). The runner packages fsynced records for resume if work remains at the deadline.
- Scope: B2-flip Step 5 donor-migration inference on Devign and ReVeal. No inference was executed during this edit; no prompts, base threshold values, preregistration files, or test metrics were changed. This is an operational correction to implement the existing preregistered inheritance rule, not an exploratory analysis. See [today's run worklog](worklogs/2026-11-04_b2_flip_kaggle_inference.md).


## 2026-11-05 - B3 validation Colab delivery (operational preparation)

Created 09_Arm_B3_Contrastive with CPU notebook to download the exact registered Q4_K_M GGUF directly into Drive, and a separate B3 validation inference notebook. Preserves original rendered prompts from ZIP (1), tokenizer revision, model SHA-256, llama-cpp-python 0.3.16, 8192 context, 256 batch, full first-token logits and seed 42. Requires two T4 GPUs and aborts if unavailable; no implicit hardware/model fallback. Adds Drive checkpoints, scope/identity checks and separate validation threshold candidate only after the full census. Does not edit frozen protocols, specs, donor banks or threshold locks. Existing B3 provenance/content audit remains unresolved; no automatic confirmatory acceptance. No GPU inference or full model download executed in this preparation. See worklogs/2026-11-05_b3_colab_validation_preparation.md for source hashes, tests, upload receipts and operational differences.

## 2026-11-05 - B1-H2 CDG-cluster validation candidate (exploratory variant)

- Assessed the proposal in `REPORT_TO_TEACHER/bao-cao-tien-do-va-kho-khan-gap-phai.md` against `preregistration.md` and the frozen `prereg-v1:configs/protocol.yaml`. The registered H2 source limits are 40 nodes/80 edges and the H2 prompt evidence cap is 1,500 tokens; the closed-node-prefix policy is specified for `graph_full`, not `graph_h2`. Selecting a bounded CDG-centred cluster from the same frozen CPG therefore fits the registered H2 source/budget envelope. The exact fallback selector was not explicitly frozen in the preregistration, so this candidate is disclosed as a post-registration implementation variant/exploratory comparison, not as a preregistered selector or a replacement active prompt.
- Structural checks pass for the separate validation-only candidate `11_Arm_B1H2_Evidence/validation_h2_cluster_v5_20261104/`: all 5,005 IDs and prompt hashes verified; code blocks match B2; H2 source counts stay within 40/80; emitted nodes and CDG/CFG witnesses resolve to the same frozen CPG; unresolved label flags are zero; recorded token metadata is within caps. Exact pinned tokenizer files were unavailable locally, so the independent audit did not recompute token counts.
- **Do not interpret the structural pass as full prompt/audit acceptance.** Candidate v5 still has 1,465/5,005 prompts (29.27%) with no usable guarded H2 evidence: 609 Devign, 856 ReVeal. The CDG fallback recovers 678 rows compared with this candidate's prefix-only path, but the remaining yield concern is material. The renderer's `graph_missing` flag is 30/5,005 (0.60%) because a nonempty “No guarded sink evidence detected” fallback does not set that flag. `preregistration.md` has a >5% missing-graph stop rule but does not explicitly classify this no-guard case or set a minimum guard-yield target; if these 1,465 rows count as missing graph, the rate exceeds 5%. The audit report now separates `structural_integrity_pass=true` from `overall_pass=null`; treatment coverage and stop-rule interpretation remain unresolved.
- A blinded, candidate-specific 60-prompt review packet (30 per dataset, with truncation and long prompts represented) and two blank reviewer forms are prepared under `11_Arm_B1H2_Evidence/validation_h2_cluster_v5_20261104/manual_review_20261105_v2/`; the two independent reviews remain outstanding. Packet audit confirms hashes, candidate prompt identity, 30+30 coverage, and hidden strata. No inference, threshold fitting, test inspection, or active prompt modification occurred.
- Packet audit `11_Arm_B1H2_Evidence/audit/b1_h2_manual_review_packet_audit_20261105.json` confirms packet file hashes, candidate prompt identity/hashes, 30+30 coverage and that reviewer-facing files hide the strata. Both reviewer forms remain blank.
- See `worklogs/2026-11-05_b1_h2_audit_and_feasibility.md` and `11_Arm_B1H2_Evidence/audit/b1_h2_candidate_audit_v5_20261105.json`. This disclosure does not convert the exploratory variant into a confirmatory inference.

## 2026-11-05 — B1-H2 validation graph-sparsity follow-up

- A validation-only diagnostic derived CDG relations from frozen CFGs using post-dominators and calibrated against 100 explicit-CDG graphs per dataset. Derived relations matched a subset of explicit CDG at 100% precision, with 80.15% Devign / 91.83% ReVeal recall in these calibration samples.
- Across the 1,465 candidate-v5 rows without usable guarded evidence, derivation could analyze 1,432 graphs and found a recognized guard-to-operation relation in only 10. This does not materially address the sparse-evidence issue; no new prompt candidate was generated. The derived relation is absent from the frozen CPG, so using it in prompts would be an exploratory post-registration change.
- Preregistration’s >5% missing-graph stop rule does not explicitly define a graph that exists but yields no CDG/guard. Candidate v5 has 1,435 no-guard rows without a Joern error marker; under the interpretation that these count as missing graph, 1,435/4,975 = 28.84%, above the stop threshold. Keep `overall_pass=null`: the structural audit passed, but the complete H2 prompt audit and stop-rule classification remain unresolved. No inference, threshold fitting, test inspection, or active prompt changes.
- Details: `worklogs/2026-11-05_b1_h2_audit_and_feasibility.md`, `11_Arm_B1H2_Evidence/audit/b1_h2_derived_cdg_feasibility_20261105.json`.

## 2026-11-05 — B1-H2 completed review forms and unresolved sample findings

- Two completed forms are now present as `reviewer_1_hieu.csv` and `reviewer_2_dung.csv`; `_filled.csv` aliases are exact byte copies, not additional reviewers. Form names/timestamps are self-reported; the audit verifies completeness and sample/hash identity, not external identity.
- Both forms cover 60/60 blind packet rows. Overall: 47 pass each; HuuHieu03 records 13 fail, Dung records 10 fail and 3 unclear. They agree on 56/60 overall verdicts; four rows need adjudication. Both agree no label leakage in all 60 and mark demos not applicable.
- Both reviewers fail graph validity and variant correctness on the same 9 sampled missing-CPG/flagged-Joern rows because the prompt renders an empty legacy node/edge frame. These rows are excluded from the preregistered missing-graph rate, but the prompt presentation issue remains documented. Code-truncation judgments are mixed; the candidate preserves B2 target code exactly, so a B1-H2-only code change would break shared target input across arms.
- This is not full manual acceptance: reviewer failures/uncertainties and four overall disagreements remain, and the preregistration supplies no acceptance threshold for this sampled-review rate. Keep the candidate exploratory; no inference or threshold fitting. See `11_Arm_B1H2_Evidence/audit_b1_h2_manual_review_results.py` and `11_Arm_B1H2_Evidence/audit/b1_h2_manual_review_results_20261105.json`.

### Clarification — literal missing-graph gate after completed review

Source diagnosis and the completed blind reviews distinguish absent CPG from an existing CPG that yields no guarded operation. The 1,435 non-error no-guard rows still have CPG; all 30 missing-CPG rows are flagged Joern errors. Both reviewers marked sampled no-guard prompts with an existing graph as `graph_valid=pass`, and marked graph/variant failures only for the sampled missing-CPG rows. Applying preregistration's Joern-error exclusion gives 0/4,975 missing graphs (0%), below the 5% stop threshold. The 29.27% no-usable-guard rate remains a treatment-coverage limitation, but no minimum guard-yield criterion was preregistered. Full manual acceptance remains unresolved due fail/unclear judgments and four overall disagreements.

## 2026-11-05 — B1-H2 v6 Joern-error presentation candidate (exploratory)

- Re-read of the 04/11 report confirms the original issue was twofold: missing source CDG edges and CDG edges outside the initial 40/80 slice, plus a renderer that did not flag no-evidence fallback strings. The report's 3,697/5,005 count belongs to an earlier prompt artifact and is not directly comparable to candidate v5.
- Candidate v5 applies the proposed same-CPG CDG-cluster fallback under the 40/80 source cap, recovering 678 rows relative to its own prefix route; 672 selections use nodes outside the prefix. The selector is a post-registration implementation choice, so the candidate remains exploratory. The remaining 1,465/5,005 no-guard rows mostly have CPGs but no source CDG/recognized guard relation; do not equate this with missing CPG.
- Based on source diagnosis and the completed v5 sample review, the 30 missing-CPG rows are all flagged Joern errors, while sampled graph-present/no-guard rows are rated graph-valid. Preregistration excludes flagged Joern errors; literal missing-graph rate is 0/4,975, below 5%. The 29.27% no-usable-guard rate is a coverage limitation; no minimum guard-yield threshold is registered.
- Built separate candidate v6: only the 30 flagged Joern-error prompts change, replacing the empty B1 Node/Edge frame with explicit `CPG_UNAVAILABLE`; B2 target code remains identical and `graph_missing` provenance remains true. Independent exact-tokenizer audit over all 5,005 prompts passes token metadata, caps, identities, hashes, provenance, 40/80 graph limits and label checks. No active prompts or preregistration files changed.
- A fresh blinded 60-prompt v6 packet passes identity/hash/quota/blinding checks. Both v6 reviewer forms are blank, so full manual acceptance is pending. No inference or threshold fitting. See worklog and `11_Arm_B1H2_Evidence/audit/b1_h2_candidate_audit_v6_20261105.json`.
- The v5 and v6 blinded samples contain the same 60 IDs; 51 prompt hashes are unchanged and the 9 changed hashes are the sampled missing-CPG rows. Existing v5 judgments can be referenced only for those 51 exact-hash prompts; the nine revised prompts require fresh review. No judgments were copied into the v6 forms.


## 2026-11-05 — B1-H2 evidence artifact organization

- Relocated the exploratory B1-H2 candidate versions, review packets, dedicated scripts, pinned tokenizer cache, and audit outputs into `11_Arm_B1H2_Evidence/`; updated artifact paths and source hashes and reran packet/form and candidate audits. The v6 structural and registered prompt gates still pass; `overall_pass` remains unresolved for the same supplemental-review/truncation limitations.
- This is an organizational change only. No preregistered matrix, active prompts, thresholds, or test data changed. Shared `Runs-management/remediate_validation_extensions.py` remains in place for B3 dependencies.


## 2026-11-06 - Temporarily remove uncommitted B3 Colab folder

At the user's request, deleted the local untracked 09_Arm_B3_Contrastive preparation folder and appended its removal to worklogs/2026-11-05_b3_colab_validation_preparation.md. No commit/push or Drive deletion. No frozen protocol, data or threshold changes.


## 2026-11-06 - Prepare exploratory B1-H2 Colab L4 pilot

- Added a separate 100-row hardware pilot using 50 Devign and 50 ReVeal original Hiếu B1-H2 validation prompts from the original ZIP. The frozen 15-arm specs, thresholds, and confirmatory outputs were not changed.
- Added a Colab notebook that pins the registered model/tokenizer and inference package versions, requests full L4 offload, captures llama.cpp load/buffer logs, and records canonical first-token logprobs. The run is explicitly exploratory and cannot be used to select thresholds or as confirmatory evidence.
- This changes the execution GPU from the registered Kaggle 2×T4 setup to one Colab L4; the pilot is therefore a hardware feasibility check and records the deviation.
- Preparation only: no Drive upload or Colab execution has happened yet. No Drive link is available; the local bundle is retained until an upload is verified.


## 2026-11-06 - Commit imported runs and audit workspace

Prepared all non-ignored pending notebooks, I-10/I-11 run records and audit/worklog artifacts for publication on the current feature branch. Four original ZIP specs exceed 100 MiB each; kept their exact local bytes, added exact ignore entries and a SHA-256 manifest at grace_15arms_prompts_and_clean_specs/local_specs_manifest.json. Existing ignored output/checkpoint archives remain local. Updated the notebook-source test to distinguish executed provenance notebooks from unexecuted templates, requiring completed execution metadata, no error outputs and exact embedded-helper agreement with the imported Kaggle runtime for executed notebooks. Frozen OSF artifacts, protocols, data sources and threshold locks are unchanged.
