# B3 new-algorithm checkpoint resume on lznt123

- Date: 2026-11-09, 15:49 Asia/Saigon (08:49 UTC).
- Parent: `lznt123/grace-b3-new-dual-linuxfix-20261109`, Kaggle terminal status `COMPLETE`; internal dual status `checkpointed`.
- Independently restored and validated both per-dataset checkpoints before transfer: Devign 2,732/2,732 (SHA-256 `21e1832c31298e2a20be61901f12170f2ce592e958f4edfb0f311134676d7552`); REVEAL 1,713/2,273 (SHA-256 `8069d2051386f0dd3b110b58d4b63cae0b611aa430ca795306e8ed08c6e2d4a5`), 560 remaining. Checkpoint identity, member hashes, records, source/prompt hashes, scoring and native provenance validated by `b3_delivery_runtime.restore_checkpoint` / `checked_records`.
- Created private ready dataset `lznt123/grace-b3-new-dual-checkpoints-20261109` containing these exact archives. Original Devign/REVEAL input datasets, roots, worker, model, prompts, selector, scorer and seven-package runtime contract SHA `4c9c3bcff5e9fd32532d7edf85df7a961e45ec9c64bee3df8833d986a2eb276e` remain unchanged.
- Launched version 1 at 15:49 Asia/Saigon: https://www.kaggle.com/code/lznt123/grace-b3-new-algorithm-checkpoint-resume. Kaggle source readback matched every cell; private=true, GPU=true, machine `NvidiaTeslaT4`; original two inputs plus checkpoint dataset attached. Latest status at 15:49: `RUNNING`, no failure message.
- Resume keeps fixed Devign -> REVEAL order. Devign is restored at census and revalidated; REVEAL resumes from 1,713 and has 560 pending. Native runtime certification for this new session awaits its own runtime provenance/logs and first resumed records.
- Preparation and launch receipts: `Runs-management/b3_lznt_resume_20261109/b3-new-dual-resume-20261109/`; CPU/delivery preflight is explicitly scoped to delivery and does not claim native certification.
