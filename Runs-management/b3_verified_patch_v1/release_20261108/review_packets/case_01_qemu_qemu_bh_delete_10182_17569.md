# Review Packet: case_01_qemu_qemu_bh_delete_10182_17569

- **Dataset:** Devign
- **Project:** qemu
- **Function Hint:** `qemu_bh_delete`
- **Vulnerable Donor:** `devign:train:10182` (Commit `1b435b10324fe9937f254bb00718f78d5e50837a`)
- **Patched Candidate:** `devign:train:17569` (Commit `4e59b545868a5ee5f59b346337f0c44209929334`)
- **Payload SHA-256:** `a196ee94d59fabdeac14026c594a5cbc354379a4f40be389e7087778252fe33d`

## Source Revisions
- Direct Parent Edge: **False**
- Vulnerable Parents: `['474ad834d2c2637a7e5df527f8a89e2792b572ef']`
- Patched Parents: `['e11480db7ff15a9e878f6b3cc1199b439bf7c825']`

## Changed Files
- Vulnerable commit changed: `['vl.c', 'qemu-common.h']`
- Patched commit changed: `['Makefile.objs', 'qemu-tool.c']`
- Shared files: `[]`

## Commit Messages
- **Vulnerable:** Make bottom halves more robust

Bottom halves are supposed to not complete until the next iteration of the main
loop.  This is very important to ensure that guests can not cause stack
overflows in the
- **Patched:** tools: Use real async.c instead of stubs

It's wrong to call BHs directly, even in tools. The only operations that
schedule BHs are called in a loop that (indirectly) contains a call to
qemu_bh_poll a
