# Blind manual review — B1-H2 v5 validation candidate

Scope: 60 validation prompts from candidate v5, 30 Devign and 30 ReVeal. No target labels, inference outputs, thresholds, model verdicts, or sample strata are shown in the review packet.
Each reviewer should work independently, complete every criterion, and record their actual name and review time. Do not copy scores between forms.

## Review criteria

For each criterion use `pass`, `fail`, `unclear`, or `not_applicable`; include a short reason and location for every fail/unclear.
- `target_code_intact`: target code matches the expected source and truncation has not removed essential context.
- `graph_valid`: graph belongs to the target and H2 evidence is understandable; a missing CPG must be called out.
- `demo_valid`: B1-H2 has no demonstrations; enter `not_applicable`.
- `no_target_label_leak`: no target label or answer is exposed in the prompt.
- `variant_correct`: prompt follows the B1-H2 H2 execution-evidence presentation specified for this candidate.
- `truncation_acceptable`: truncation leaves a usable prompt within its stated evidence limits.
- `overall_verdict`: `pass`, `fail`, or `unclear`.

## Files

- `manual_packet.md`: readable blind prompt packet.
- `manual_sample.jsonl`: internal sampling audit trail; do not show this file to reviewers.
- `reviewer_1.csv`, `reviewer_2.csv`: separate blank forms; preserve both originals.
- Rubric reference: `../../../Runs-management/prompt_audit_20261102/RUBRIC.md`.

Candidate prompt files remain unchanged. This sample is not a substitute for reviewing inference results or target labels.
