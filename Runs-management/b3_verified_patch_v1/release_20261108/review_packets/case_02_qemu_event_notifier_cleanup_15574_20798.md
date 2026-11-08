# Review Packet: case_02_qemu_event_notifier_cleanup_15574_20798

- **Dataset:** Devign
- **Project:** qemu
- **Function Hint:** `event_notifier_cleanup`
- **Vulnerable Donor:** `devign:train:15574` (Commit `aa262928595d431bfee7914cb7d9d79197f887a2`)
- **Patched Candidate:** `devign:train:20798` (Commit `d0cc2fbfa607678866475383c508be84818ceb64`)
- **Payload SHA-256:** `37338696a7a86494c38f296564cd1823203db2ca5652289b71fb403956bfa5c8`

## Source Revisions
- Direct Parent Edge: **False**
- Vulnerable Parents: `['df9046363220e57d45818312759b954c033c58ab']`
- Patched Parents: `['fc97a652de3e54394ca4d0e5e5d689fd8aba8b6f']`

## Changed Files
- Vulnerable commit changed: `['util/event_notifier-posix.c', 'util/event_notifier-win32.c']`
- Patched commit changed: `['event_notifier.h', 'event_notifier-posix.c']`
- Shared files: `[]`

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
