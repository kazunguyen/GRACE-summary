# Review Evidence Packet: case_11_qemu_HELPER_19700_7094

- **Dataset:** Devign
- **Project:** qemu
- **Function Hint:** `HELPER`
- **Vulnerable Donor:** `devign:train:19700` (Commit `686eeb93d5738c84c59395b2ec6f8181c2b7cbed`)
- **Patched Candidate:** `devign:train:7094` (Commit `bb8794307252be791f1723eae47983f815882376`)
- **Payload SHA-256:** `67162a8ba8c82afc5d15475ecafa0322ee5dff0e6ddb88cee68350592cdca8c5`

## Source Revisions
- Direct Parent Edge in Git: **False**
- Vulnerable Parents: `['7bbcb0afe715c36545bbbd872441c473927c1a4e']`
- Patched Parents: `['e2d9f902378cc0b8de9bacfc9406e6c63bc236d7']`

## Changed Files
- Vulnerable Commit Modified: `['target-arm/helper.c']`
- Patched Commit Modified: `['target/s390x/helper.h', 'target/s390x/mem_helper.c', 'target/s390x/translate.c']`
- Shared Files: `[]`

## Commit Messages
- **Vulnerable:** target-arm: fix sdiv helper

(INT32_MIN / -1) triggers an overflow, and the result depends on the
host architecture (INT32_MIN on arm, -1 on ppc, SIGFPE on x86). Use a
test to output the correct value
- **Patched:** s390x/tcg: implement TEST PROTECTION

Linux uses TEST PROTECTION to sense for available memory locations.

Let's implement what we can for now (just as for the other instructions,
excluding AR mode an

## Review Instructions for Human Reviewers
Please fill out a separate review form verifying:
1. `same_function_verified`: Are the two functions genuinely the same function in upstream source?
2. `security_fix_verified`: Does the change represent an authentic security vulnerability fix?
3. `source_revisions_verified`: Do the commit revisions connect via git parentage and actual patch diff?
4. `explanation_supported`: Is the difference rationale supported by reviewed code changes?
Include `payload_sha256` matching above to certify authenticity.
