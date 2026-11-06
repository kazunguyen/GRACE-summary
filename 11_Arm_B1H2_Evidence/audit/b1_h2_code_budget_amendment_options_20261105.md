# B1-H2 manual-review findings: target-code budget options

Date: 2026-11-05  
Scope: Local decision note only. This file does not amend or replace the preregistration.

## Current evidence

- The preregistered prompt budget is 3,000 tokens for target code, 1,500 for graph, 8,192 total, with 64 reserved.
- B1-H2 v6 keeps each target-code block byte-for-byte equal to its B2 reference prompt. Its exact-token audit passes the registered 3,000/1,500/8,192+64 limits and the 40-node/80-edge H2 source limit.
- The blinded review sample and hash carry-forward leave target-code/truncation findings: reviewer-1 perspective 6 fail and 2 unclear for `target_code_intact`; reviewer-2 perspective 3 fail and 3 unclear. These failures concern clipped query code inherited unchanged from B2, not the H2 graph-selection change.
- Exact-token diagnosis found 94/5,005 validation prompts are code-truncated (60 Devign, 34 ReVeal). Every full source function exceeds 3,000 tokens. With full source code substituted, 83/94 fit the existing total-context limit; 11 exceed the 8,192+64 total. A code cap of 8,000 would cover 85/94 by source length, but some still exceed total context because of graph/template tokens.

## Available paths

### Keep the registered budget

Retain the B2-matched target code and B1-H2 v6 graph presentation. The preregistered automated gates pass: no demo-empty prompts, 0/4,975 missing graphs after excluding flagged Joern errors, and zero unresolved target-label leaks. Report the manually observed truncation failures as a shared input limitation. The CDG-cluster selector and explicit Joern-error presentation remain post-registration exploratory implementation choices.

### Change the target-code allocation

This requires a dated protocol amendment. Raising the code cap only for B1-H2 would break target-code parity with B2. A consistent repair would require rebuilding and auditing every affected prompt set, including both validation and test where applicable, and deciding how to handle at least 11 validation functions that still exceed total context. Existing test exposure also means a new budget cannot be described as prospective confirmatory evaluation without further protocol decisions.

## Suggested disposition

Do not edit frozen protocol or active prompts as part of the current B1-H2 graph repair. Keep v6 as an exploratory validation candidate. Treat the preregistered automated prompt gates as passed, while recording that the stricter sample-level target-code review did not pass. If the study requires all sampled code to remain semantically complete, obtain a protocol amendment and define a shared target-code policy before rebuilding affected arms.

## Evidence files

- `11_Arm_B1H2_Evidence/audit/b1_h2_candidate_audit_v6_20261105.json`
- `11_Arm_B1H2_Evidence/audit/b1_h2_code_truncation_budget_20261105.json`
- `11_Arm_B1H2_Evidence/audit/b1_h2_v6_delegated_review_20261105/summary.json`
- `worklogs/2026-11-05_b1_h2_audit_and_feasibility.md`
