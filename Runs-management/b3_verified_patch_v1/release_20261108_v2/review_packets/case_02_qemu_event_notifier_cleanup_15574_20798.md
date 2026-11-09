# Review Evidence Packet: case_02_qemu_event_notifier_cleanup_15574_20798

- **Dataset:** Devign
- **Project:** qemu
- **Function Hint:** `event_notifier_cleanup`
- **Vulnerable Donor:** `devign:train:15574` (Commit `aa262928595d431bfee7914cb7d9d79197f887a2`)
- **Patched Candidate:** `devign:train:20798` (Commit `d0cc2fbfa607678866475383c508be84818ceb64`)
- **Payload SHA-256:** `378aaa74ec3492e1adff9aa5ac9401fe58c723fd16aff6d92d9df15c37851d55`

## Source Revisions
- Direct Parent Edge in Git: **False**
- Vulnerable Parents: `['df9046363220e57d45818312759b954c033c58ab']`
- Patched Parents: `['fc97a652de3e54394ca4d0e5e5d689fd8aba8b6f']`

## Changed Files
- Vulnerable Commit Modified: `['util/event_notifier-posix.c', 'util/event_notifier-win32.c']`
- Patched Commit Modified: `['event_notifier-posix.c', 'event_notifier.h']`
- Shared Files: `[]`

## Commit Messages
- **Vulnerable:** event_notifier: prevent accidental use after close

Let's set the handles to the underlying facilities to their extremal
value so no accidental misuse can happen, and to make it obvious that the
notif
- **Patched:** event_notifier: enable it to use pipes

This takes the eventfd emulation code from the main loop.  When the
EventNotifier is used for the main loop too, we need this compatibility
code.

Without CONFI

## Review Instructions for Human Reviewers
Please fill out a separate review form verifying:
1. `same_function_verified`: Are the two functions genuinely the same function in upstream source?
2. `security_fix_verified`: Does the change represent an authentic security vulnerability fix?
3. `source_revisions_verified`: Do the commit revisions connect via git parentage and actual patch diff?
4. `explanation_supported`: Is the difference rationale supported by reviewed code changes?
Include `payload_sha256` matching above to certify authenticity.
