# Review Evidence Packet: case_10_qemu_HELPER_4792_8643

- **Dataset:** Devign
- **Project:** qemu
- **Function Hint:** `HELPER`
- **Vulnerable Donor:** `devign:train:4792` (Commit `8d04fb55dec381bc5105cb47f29d918e579e8cbd`)
- **Patched Candidate:** `devign:train:8643` (Commit `e8ede0a8bb5298a6979bcf7ed84ef64a64a4e3fe`)
- **Payload SHA-256:** `aecc7ecc0bcab18fd6cbd4bf3c25bf722b8eb492dd0b4f377fddb027292898fc`

## Source Revisions
- Direct Parent Edge in Git: **False**
- Vulnerable Parents: `['791158d93b27f22a17c2ada06621831d54f09a2c']`
- Patched Parents: `['220c21474535d5a859bb10eff2e2be0a48a15694']`

## Changed Files
- Vulnerable Commit Modified: `['cpu-exec.c', 'cpus.c', 'cputlb.c', 'exec.c', 'hw/core/irq.c', 'hw/i386/kvmvapic.c', 'hw/intc/arm_gicv3_cpuif.c', 'hw/ppc/ppc.c', 'hw/ppc/spapr.c', 'include/qom/cpu.h', 'memory.c', 'qom/cpu.c', 'target/arm/helper.c', 'target/arm/op_helper.c', 'target/i386/smm_helper.c', 'target/s390x/misc_helper.c', 'translate-all.c', 'translate-common.c']`
- Patched Commit Modified: `['target-unicore32/Makefile.objs', 'target-unicore32/helper.c', 'target-unicore32/ucf64_helper.c']`
- Shared Files: `[]`

## Commit Messages
- **Vulnerable:** tcg: drop global lock during TCG code execution

This finally allows TCG to benefit from the iothread introduction: Drop
the global mutex while running pure TCG CPU code. Reacquire the lock
when enter
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
