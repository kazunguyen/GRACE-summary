# Review Packet: case_10_qemu_HELPER_4792_8643

- **Dataset:** Devign
- **Project:** qemu
- **Function Hint:** `HELPER`
- **Vulnerable Donor:** `devign:train:4792` (Commit `8d04fb55dec381bc5105cb47f29d918e579e8cbd`)
- **Patched Candidate:** `devign:train:8643` (Commit `e8ede0a8bb5298a6979bcf7ed84ef64a64a4e3fe`)
- **Payload SHA-256:** `f6be334943bee322b629d62e0502e1ee82edf1be2c15d5486032bc5bb9b59816`

## Source Revisions
- Direct Parent Edge: **False**
- Vulnerable Parents: `['791158d93b27f22a17c2ada06621831d54f09a2c']`
- Patched Parents: `['220c21474535d5a859bb10eff2e2be0a48a15694']`

## Changed Files
- Vulnerable commit changed: `['hw/core/irq.c', 'cpu-exec.c', 'include/qom/cpu.h', 'qom/cpu.c', 'target/i386/smm_helper.c', 'translate-all.c', 'hw/ppc/spapr.c', 'hw/i386/kvmvapic.c', 'memory.c', 'hw/ppc/ppc.c', 'target/arm/op_helper.c', 'target/arm/helper.c', 'exec.c', 'translate-common.c', 'cputlb.c', 'hw/intc/arm_gicv3_cpuif.c', 'cpus.c', 'target/s390x/misc_helper.c']`
- Patched commit changed: `['target-unicore32/ucf64_helper.c', 'target-unicore32/helper.c', 'target-unicore32/Makefile.objs']`
- Shared files: `[]`

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
