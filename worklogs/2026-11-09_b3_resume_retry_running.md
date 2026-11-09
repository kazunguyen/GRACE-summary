# B3 resume retry reached RUNNING

- Date: 2026-11-09, 16:36 Asia/Saigon (09:36 UTC).
- The previous v2 queued session reached Kaggle `CANCEL_ACKNOWLEDGED`. Reissued the same corrected notebook against the canonical Kaggle kernel slug; API accepted version 3.
- Kernel: https://www.kaggle.com/code/lznt123/grace-b3-checkpoint-resume-v2
- Remote source readback: all notebook cells match; private=true; GPU=true; machine NvidiaTeslaT4; original Devign/REVEAL input datasets and verified checkpoint dataset attached. Live status `RUNNING`, no failure message.
- Resume payload remains externally pinned and unchanged: Devign 2,732/2,732; REVEAL 1,713/2,273, 560 pending. Seven-package runtime contract SHA `4c9c3bcff5e9fd32532d7edf85df7a961e45ec9c64bee3df8833d986a2eb276e`.
- This confirms scheduling/execution started only. Native runtime acceptance awaits this session's provenance, model/offload/build logs, and resumed records. Receipts: `Runs-management/b3_lznt_resume_retry_20261109/b3-new-dual-resume-v2-retry1/`.
