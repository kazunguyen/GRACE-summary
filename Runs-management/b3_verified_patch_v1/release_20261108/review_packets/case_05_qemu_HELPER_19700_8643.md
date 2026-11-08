# Review Packet: case_05_qemu_HELPER_19700_8643

- **Dataset:** Devign
- **Project:** qemu
- **Function Hint:** `HELPER`
- **Vulnerable Donor:** `devign:train:19700` (Commit `686eeb93d5738c84c59395b2ec6f8181c2b7cbed`)
- **Patched Candidate:** `devign:train:8643` (Commit `e8ede0a8bb5298a6979bcf7ed84ef64a64a4e3fe`)
- **Payload SHA-256:** `aec61ccfb876f575f27ecfff38fcacd5b2664721b3d897b685ca7fc61882640d`

## Source Revisions
- Direct Parent Edge: **False**
- Vulnerable Parents: `['7bbcb0afe715c36545bbbd872441c473927c1a4e']`
- Patched Parents: `['220c21474535d5a859bb10eff2e2be0a48a15694']`

## Changed Files
- Vulnerable commit changed: `['target-arm/helper.c']`
- Patched commit changed: `['target-unicore32/ucf64_helper.c', 'target-unicore32/helper.c', 'target-unicore32/Makefile.objs']`
- Shared files: `[]`

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
