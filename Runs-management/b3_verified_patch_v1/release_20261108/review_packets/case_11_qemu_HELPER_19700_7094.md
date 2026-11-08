# Review Packet: case_11_qemu_HELPER_19700_7094

- **Dataset:** Devign
- **Project:** qemu
- **Function Hint:** `HELPER`
- **Vulnerable Donor:** `devign:train:19700` (Commit `686eeb93d5738c84c59395b2ec6f8181c2b7cbed`)
- **Patched Candidate:** `devign:train:7094` (Commit `bb8794307252be791f1723eae47983f815882376`)
- **Payload SHA-256:** `ce874ec744675f361e746a3e8cd93749d6febda95b467256bd983e6e0b22db38`

## Source Revisions
- Direct Parent Edge: **False**
- Vulnerable Parents: `['7bbcb0afe715c36545bbbd872441c473927c1a4e']`
- Patched Parents: `['e2d9f902378cc0b8de9bacfc9406e6c63bc236d7']`

## Changed Files
- Vulnerable commit changed: `['target-arm/helper.c']`
- Patched commit changed: `['target/s390x/mem_helper.c', 'target/s390x/translate.c', 'target/s390x/helper.h']`
- Shared files: `[]`

## Commit Messages
- **Vulnerable:** target-arm: fix sdiv helper

(INT32_MIN / -1) triggers an overflow, and the result depends on the
host architecture (INT32_MIN on arm, -1 on ppc, SIGFPE on x86). Use a
test to output the correct value
- **Patched:** s390x/tcg: implement TEST PROTECTION

Linux uses TEST PROTECTION to sense for available memory locations.

Let's implement what we can for now (just as for the other instructions,
excluding AR mode an
