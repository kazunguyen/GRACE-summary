# Review Evidence Packet: case_05_qemu_HELPER_19700_8643

- **Dataset:** Devign
- **Project:** qemu
- **Function Hint:** `HELPER`
- **Vulnerable Donor:** `devign:train:19700` (Commit `686eeb93d5738c84c59395b2ec6f8181c2b7cbed`)
- **Patched Candidate:** `devign:train:8643` (Commit `e8ede0a8bb5298a6979bcf7ed84ef64a64a4e3fe`)
- **Payload SHA-256 (Canonical Candidate Hash):** `INELIGIBLE_NO_CANDIDATE`
- **Admissible Candidate Available:** **False**

## Source Revisions
- Direct Parent Edge in Git: **False**
- Vulnerable Parents: `['7bbcb0afe715c36545bbbd872441c473927c1a4e']`
- Patched Parents: `['220c21474535d5a859bb10eff2e2be0a48a15694']`

## Changed Files
- Vulnerable Commit Modified: `['target-arm/helper.c']`
- Patched Commit Modified: `['target-unicore32/Makefile.objs', 'target-unicore32/helper.c', 'target-unicore32/ucf64_helper.c']`
- Shared Files: `[]`

## Commit Messages
- **Vulnerable:** target-arm: fix sdiv helper

(INT32_MIN / -1) triggers an overflow, and the result depends on the
host architecture (INT32_MIN on arm, -1 on ppc, SIGFPE on x86). Use a
test to output the correct value
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
