# Review Packet: case_12_qemu_HELPER_10808_14381

- **Dataset:** Devign
- **Project:** qemu
- **Function Hint:** `HELPER`
- **Vulnerable Donor:** `devign:train:10808` (Commit `4d9ad7f793605abd9806fc932b3e04e028894565`)
- **Patched Candidate:** `devign:train:14381` (Commit `e8ede0a8bb5298a6979bcf7ed84ef64a64a4e3fe`)
- **Payload SHA-256:** `7b6664f68bb0b4c453696c2eab0c20398d59e1ff27bde9839a3d519701f26206`

## Source Revisions
- Direct Parent Edge: **False**
- Vulnerable Parents: `[]`
- Patched Parents: `['220c21474535d5a859bb10eff2e2be0a48a15694']`

## Changed Files
- Vulnerable commit changed: `[]`
- Patched commit changed: `['target-unicore32/ucf64_helper.c', 'target-unicore32/helper.c', 'target-unicore32/Makefile.objs']`
- Shared files: `[]`

## Commit Messages
- **Vulnerable:** 
- **Patched:** unicore32: Split UniCore-F64 instruction helpers from helper.c

This patch just splits ucf64 instruction simulation helpers from
helper.c.
Also, two checkpatch warnings are solved.

v1->v2: adjust cop
