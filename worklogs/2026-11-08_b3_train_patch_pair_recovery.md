# B3 train vulnerable donor patch recovery

Date: 2026-11-08

## Scope

Used the frozen, finalized donor banks at `01_Author_Baseline_Unified/output/research_freeze_20261101`. Processed only `target=1` donors in the train split; validation and test inputs were not read for candidate construction.

| Dataset | Finalized vulnerable train donors | Commit IDs in frozen donor metadata |
|---|---:|---:|
| Devign | 9,933 | 9,933 donor rows; 5,587 distinct commits |
| ReVeal | 1,522 | 0 |

## Method

For Devign, used each row's recorded project and commit ID to retrieve the upstream commit patch from the corresponding FFmpeg or QEMU GitHub repository. For each donor, compared the patch's removed/context hunk tokens with the donor function. A candidate was created only when a hunk matched the donor function and changed its code tokens. The post-patch function is reconstructed by applying those matching hunks while retaining the donor source outside the changed region. The output stores the original donor, reconstructed function, commit URL/message, file path, hunk evidence, and hashes.

For ReVeal, inspected the frozen train rows and donor metadata. They retain a numeric `source_id`/hash and a broad project label (`debian` or `chrome`), but have no commit ID or source file/repository path. Those fields are insufficient to identify the corresponding patch without guessing.

## Results

| Dataset | Extracted patch pair candidates | Could not link donor to patch hunk | Hunk was formatting/comment-only after token normalization | Total |
|---|---:|---:|---:|---:|
| Devign | 7,061 | 2,823 | 49 | 9,933 |
| ReVeal | 0 | 1,522 | 0 | 1,522 |

All 5,587 distinct Devign commit patches downloaded successfully. The 2,823 unresolved Devign records have the reason `NO_PATCH_HUNK_CONTEXT_MATCHES_DONOR_FUNCTION`; their commit is known, but its patch could not be linked to the donor function by matching hunk context. The 49 formatting/comment-only records were not emitted as code pairs because their normalized before/after function tokens are identical. These records should not be treated as security fixes based on the dataset label alone.

The 7,061 extracted Devign records are **review candidates**, not a finalized security dataset. Every row remains `PENDING_REVIEW`; no reviewer outcome was assigned. The commit and diff establish a source-linked code change, but a reviewer must still decide whether it fixes the relevant security issue and whether the reconstructed function is an acceptable pair. For example, some Devign source commits are ordinary API or runtime-error changes rather than confirmed security patches.

## Files

Artifacts are in `13_Arm_B3_Contrastive/output/train_patch_recovery_20261108/`:

- `devign_patched_review_pairs.jsonl` — 7,061 vulnerable/post-patch function candidates, pending review.
- `devign_unresolved_review_queue.jsonl` — 2,872 Devign rows without a usable code pair, including the 49 formatting/comment-only changes.
- `devign_patched_candidates.jsonl` — complete 9,933-row Devign audit table.
- `reveal_unresolved_vulnerable_train.jsonl` — all 1,522 ReVeal vulnerable donors with their source IDs and the missing-provenance reason.
- `review_decision_template.csv` — one reviewer-tracking row for every vulnerable donor in both datasets. `reviewer`, `review_decision`, and `review_notes` are intentionally blank.
- `recovery_report.json` — counts and status summary.
- `patch_download_errors.json` — failed upstream patch downloads (empty for this run).

The reproducible retrieval/reconstruction script is `13_Arm_B3_Contrastive/scripts/recover_train_patch_pairs.py`. It reads the frozen train data, writes the review artifacts here, and caches the retrieved upstream `.patch` files under `tmp/b3_recovery_src/patches/` so a rerun does not need to download them again. All review decisions remain pending.

## Follow-up needed

1. Review the 7,061 Devign candidates in `review_decision_template.csv` and the paired source/hunk evidence in the JSONL. Retain only pairs reviewers accept as security-relevant and correctly linked.
2. To recover ReVeal pairs, obtain the original source provenance for each donor: at minimum the repository URL and vulnerable/fixing commit (or an equivalent issue/patch identifier). [COMPLETED 2026-11-09: All 1,522 ReVeal unresolved vulnerable donors have been traced to their original source files, advisories, and upstream repositories via the original ReVeal dataset files and Debian Security Tracker; see detailed worklog `2026-11-08_b3_reveal_vulnerable_train_patch_trace.md` and output files in `13_Arm_B3_Contrastive/output/train_patch_recovery_20261108/`].
3. Do not call either output a finalized `devign/patched` or `reveal/patched` dataset until review is complete. The present files are candidate and unresolved queues.
