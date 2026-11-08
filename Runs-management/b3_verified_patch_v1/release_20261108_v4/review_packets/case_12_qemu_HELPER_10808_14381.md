# Review Evidence Packet: case_12_qemu_HELPER_10808_14381

- **Dataset:** Devign
- **Project:** qemu
- **Function Hint:** `HELPER`
- **Vulnerable Donor:** `devign:train:10808` (Commit `4d9ad7f793605abd9806fc932b3e04e028894565`)
- **Patched Candidate:** `devign:train:14381` (Commit `e8ede0a8bb5298a6979bcf7ed84ef64a64a4e3fe`)
- **Payload SHA-256 (Canonical Candidate Hash):** `INELIGIBLE_NO_CANDIDATE`
- **Admissible Candidate Available:** **False**

## Source Revisions
- Direct Parent Edge in Git: **False**
- Vulnerable Parents: `['cc9453f457888bdd3ab7b37988adbfc4712fa125']`
- Patched Parents: `['220c21474535d5a859bb10eff2e2be0a48a15694']`

## Changed Files
- Vulnerable Commit Modified: `['target-arm/neon_helper.c']`
- Patched Commit Modified: `['target-unicore32/Makefile.objs', 'target-unicore32/helper.c', 'target-unicore32/ucf64_helper.c']`
- Shared Files: `[]`

## Commit Messages
- **Vulnerable:** target-arm: Don't overflow when calculating value for signed VABAL

In the VABAL instruction we take the absolute difference of two
values of size x and store it in a result of size 2x. This means
we 
- **Patched:** unicore32: Split UniCore-F64 instruction helpers from helper.c

This patch just splits ucf64 instruction simulation helpers from
helper.c.
Also, two checkpatch warnings are solved.

v1->v2: adjust cop

## Review Instructions for Human Reviewers
Please fill out a separate review form verifying:
1. `same_function_verified`: Are the two functions genuinely the same function in upstream source?
2. `security_fix_verified`: Does the change represent an authentic security vulnerability fix?
3. `source_revisions_verified`: Do the commit revisions connect via git parentage and actual patch diff?
4. `explanation_supported`: Is the difference rationale supported by reviewed code changes?
Include `payload_sha256` matching above to certify authenticity.
