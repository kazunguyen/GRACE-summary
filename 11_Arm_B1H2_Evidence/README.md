# B1H2 Evidence — exploratory arm

This directory holds the exploratory B1-H2 evidence-presentation variant and its validation-only prompt candidates. It is separated from the preregistered 15-arm matrix; it is not added to `configs/arms.yaml`, and it does not replace the frozen B1-H2 prompt contract.

## Current status

- Candidate v5 and the follow-up v6 are frozen validation artifacts with 5,005 prompts each (Devign 2,732; ReVeal 2,273; seed 42).
- v6 explicitly marks rows without a usable CPG as `CPG_UNAVAILABLE`.
- Structural and exact-token audit gates passed for v6. The supplemental human review found truncation/uncertainty issues; there is no preregistered acceptance threshold for that supplemental review. Treat the candidate as exploratory and do not infer that it is accepted for confirmatory inference.
- No inference, threshold fitting, or test-set inspection was done for this arm.

## Contents

- `validation_h2_cluster_v5_20261104/`: previous validation candidate and its review packets.
- `validation_h2_cluster_v6_joern_error_20261105/`: current candidate, manual-review packet, and prompt/audit files.
- `audit/`: machine reports, feasibility and truncation diagnostics, review mappings, delegated-review proxy artifacts, and the Hieu ZIP comparison output.
- `refine_h2_validation*.py`, `select_h2_cluster.py`: candidate builders and evidence selector.
- `audit_*.py`, `diagnose_*.py`, `prepare_*.py`, `map_*.py`, `prototype_*.py`: reproducibility and audit tools for this arm.
- `tokenizer_cache_v6/`: pinned tokenizer snapshot used to recompute v6 token counts offline.
- `worklogs/2026-11-05_b1_h2_audit_and_feasibility.md`: copy of the dated project worklog; canonical worklog remains under the repository `worklogs/` directory.

## Reproduction

Run commands from the repository root with the project Python environment. The candidate scripts import shared preparation utilities from `Runs-management/` and diagnostic code from `01_Author_Baseline_Unified/`. `Runs-management/remediate_validation_extensions.py` remains a shared dependency because other arms use it; it is intentionally not moved into this folder.

Example audit commands:

```powershell
python 11_Arm_B1H2_Evidence/audit_b1_h2_manual_review_packet.py
python 11_Arm_B1H2_Evidence/audit_b1_h2_manual_review_packet_v6.py
python 11_Arm_B1H2_Evidence/audit_b1_h2_candidate_v5.py
python 11_Arm_B1H2_Evidence/audit_b1_h2_candidate_v6.py
```

See `audit/b1_h2_candidate_audit_v6_20261105.json` and the dated worklog for the detailed findings and limitations.
