# Latest inference progress check — 2026-11-06 (Asia/Bangkok)

Checked Drive output and Kaggle status/output APIs on the evening of 6 November. The downloaded B1-H2 test analysis was recorded at 21:48:41 GMT+7. Kernel status COMPLETE is distinguished from full dataset completion: the latest B2-rand batch actually timed out with validation incomplete.

## Newly verified B1-H2 Colab test result — I-14

- Downloaded Drive file `1MDE2TAcK-XIuiXre8S6vWQyeILCujdRG`: https://drive.google.com/file/d/1MDE2TAcK-XIuiXre8S6vWQyeILCujdRG/view
- Local output: `11_Arm_B1H2_Evidence/colab_l4_b1h2_test_20261106/downloaded_output/b1h2_test_output.zip`.
- ZIP SHA-256: `2c64a1be6f6026ed4d9b4e12a2196ebf01d7a37cdb8c9a876765b762b9f8fc48`.
- Inference timestamps: **16:36:30–17:40:06 GMT+7 on 6 November**, based on record timestamps (UTC 09:36:30–10:40:06).
- Complete **5,006/5,006 test records**: Devign 2,732; ReVeal 2,274. All IDs are unique; no missing/extra IDs; no prompt hash mismatches against the prepared original test bundle.
- All 5,006 individual checkpoint records match the consolidated records, with no checkpoint content mismatches.
- All model hashes match the pinned Q4_K_M model. No non-finite numeric scores. There are 307 raw response-invalid rows (152 Devign; 155 ReVeal); their scores remain finite and retained.
- Thresholds stored in output: Devign 0.09; ReVeal 0.67; threshold seal `eedb783ebba986cec772bde2bdcca1cb95a2cd9db4bebd8141a44f49342178e5`.
- **The test session's native load log verifies `offloaded 49/49 layers to GPU`**, on NVIDIA L4 23,034 MiB. This verifies the test session, not the earlier validation sessions whose load logs were empty.
- Combined with I-12/I-13: B1-H2 now has 5,005 validation and 5,006 test records, total 10,011. This is inference completion; it does not supply a paired B1 or B2 control on Colab or remove the disclosed platform deviation.
- Full local integrity report: `11_Arm_B1H2_Evidence/colab_l4_b1h2_test_20261106/test_output_analysis.json`; analysis script saved alongside it. No label-based test metrics were computed during this progress check.

## Kaggle status check

Both known B2-flip and B2-rand kernel slugs report COMPLETE. Downloaded the small status/summary JSONs into `Runs-management/progress_check_20261106/` to examine the underlying sample counts.

- **B2-flip:** all 10,011 records complete. Latest returned output is the already known I-10 session, completed 06:07:52 GMT+7 on 5 November.
- **B2-rand:** latest batch summary still shows 7,789/15,015 validation records: seed 42 complete (5,005); seed 43 has 2,784/5,005; seed 44 has 0/5,005. Remaining validation: 7,226 (2,221 ReVeal seed 43 + all 5,005 seed 44). Test count remains zero. Latest returned batch timed out on 5 November; do not interpret COMPLETE kernel status as completed validation.
- B0, B1 and B2 retain their previously verified 10,011 records per arm; this check did not discover/import replacement runs for them.
- For the five arms delegated to Hiếu (B1-full, B1-shuf, B2-nolabel, B2-labelonly, B2-rep), this check has no newly verified output/checkpoint from Hiếu. Their current live completion counts remain unknown, not asserted to be zero. Public searches did not establish authoritative run slugs for those private/delegated sessions.
- No new B3-family output was verified in this check.
