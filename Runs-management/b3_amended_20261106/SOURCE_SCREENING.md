# Screening three real Devign name-match candidates

Checked on 6 November 2026. These are discovery candidates, not admitted pairs. None has an authenticated vulnerable-to-patched source edge, archived supporting fix evidence and two completed reviewer decisions in the pair manifest. They must not enter inference. The checks below do not claim that authentic pairs cannot be recovered with further source work.

| Function hint | Vulnerable donor | Opposite-label candidate | Source inspection |
|---|---|---|---|
| `qemu_bh_delete` | `devign:train:10182` | `devign:train:17569` | The recorded revisions refer to different changes and files: [bottom-half robustness](https://github.com/qemu/qemu/commit/1b435b10324fe9937f254bb00718f78d5e50837a) changes `vl.c` and `qemu-common.h`; [tools async implementation](https://github.com/qemu/qemu/commit/4e59b545868a5ee5f59b346337f0c44209929334) changes `qemu-tool.c` and `Makefile.objs`. A shared function name is insufficient to identify the same source function across one fix. |
| `event_notifier_cleanup` | `devign:train:15574` | `devign:train:20798` | Recorded revisions are [prevent use after close](https://github.com/qemu/qemu/commit/aa262928595d431bfee7914cb7d9d79197f887a2) and [pipe support](https://github.com/qemu/qemu/commit/d0cc2fbfa607678866475383c508be84818ceb64). Security-relevant wording in one commit does not establish that these two bank snippets are its exact before/after function versions. |
| `vnc_client_error` | `devign:train:11725` | `devign:train:3267` | Recorded revisions are [VncState release workflow](https://github.com/qemu/qemu/commit/198a0039c5fca224a77e9761e2350dd9cc102ad0) and [TLS code separation](https://github.com/qemu/qemu/commit/5fb6c7a8b26eab1a22207d24b4784bd2b39ab54b). The required fix/parent/function relationship has not been established. |

Decision: retain all three only for source investigation. Do not describe them as validated counterfactuals or generate an invented security explanation from their token differences.
