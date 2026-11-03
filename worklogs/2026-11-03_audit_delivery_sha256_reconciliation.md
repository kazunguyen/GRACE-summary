---
id: "audit-delivery-sha256-reconciliation-20261103"
title: "Đối chiếu và tái niêm phong SHA-256 của artifact prompt audit và dry-run validation"
author: "Codex (trợ lý AI)"
author_type: "AI assistant"
requested_by: "Người dùng"
recorded_at: "2026-11-03T20:55:00+07:00"
timezone: "Asia/Bangkok"
work_date: "2026-11-03"
record_type: "artifact_hash_reconciliation"
status: "delivery_hashes_reconciled_with_historical_limits"
---

# Đối chiếu SHA-256 artifact audit

- Mốc Git trước chỉnh sửa: `a15145c`. Chỉ sửa hai bảng `DELIVERY_SHA256.json` và chạy lại verifier prompt audit; không sửa record inference, prompt, nhãn hoặc ngưỡng.
- Gói prompt audit: ban đầu 14/26 SHA-256 lệch; sau khi cập nhật delivery và chạy `python Runs-management/verify_prompt_audit.py`, verifier đọc 106/106 nguồn hiện có, kiểm 100.110 prompt, 30.691 score từ logprob, 60 phiếu chấm và tạo lại `verification.json` với hash `audit_summary.json` hiện hành. Vì vậy bảng dưới có 15 dòng thay đổi ở gói này, gồm hash của báo cáo verifier mới.
- Gói dry-run validation: ban đầu 6/159 SHA-256 lệch. Bảng delivery hiện khớp byte của 159 artifact được liệt kê. Không chạy lại verifier lịch sử vì `summary.json.protected_hashes` trỏ tới nhiều đầu vào đã thay đổi theo các lần cập nhật hợp lệ; không tự coi đây là tái nghiệm thu dry-run.
- Kiểm lại sau sửa: cả hai bảng delivery có 0 hash lệch; `python -m pytest -q --disable-warnings -p no:cacheprovider` đạt **111 passed, 3 warnings**; test riêng `Runs-management/test_prompt_integrity.py` đạt **10 passed**.
- Giới hạn còn lại: `dry_run_validation_20261102/final_status.json.raw_summary_sha256` vẫn là tham chiếu của snapshot cũ và không khớp `summary.json` hiện tại. `source_hashes.json` của dry-run là snapshot lịch sử: 21/23 đường dẫn còn có, 16 khớp byte hiện hành, 5 đã đổi; giữ nguyên để không viết lại lịch sử. Việc bảng delivery khớp không chứng minh mọi tham chiếu provenance nội bộ đã được tái xác nhận.
- Chưa commit/push hoặc gửi OSF trong lượt đối chiếu này.

| Gói | Artifact | SHA-256 trong manifest cũ | SHA-256 hiện hành |
|---|---|---|---|
| `prompt_audit_20261102` | `audit_summary.json` | `44f619c5de0f31f9925c3c9b0c904bcda9084d613d7c8f6b968107f0077d44d5` | `d4d3c63caa3923e167905a7bb7b4cc20db5ee4a0170ac49abced028054f9312d` |
| `prompt_audit_20261102` | `donor_scope.json` | `827f6d4d170d379a9cba10cbb2282793aeab43a924812ed2300e9f45b18b9ef7` | `fa03a7420f51032a2f6cad3b25e73d20258893189057525bff5fb53ed31e33a0` |
| `prompt_audit_20261102` | `inference_audit.json` | `8666c5fc582385949eb3c9f4b89b8d98b23432f1e482707396cc0bfbe64b3bbc` | `0802a865bcab8dc0040164bb831329f550c6e5c0ac15f2e014c0d4f12c9af6d0` |
| `prompt_audit_20261102` | `KET_QUA.md` | `2d3465c4ac2d9a0c518f240be0a4d9e267c0dd9b220f5799a49cd43fe636cead` | `2afae60b3c3ed7ff356fba5f197911b1a109e02b9dfcbef19749716d5b348a03` |
| `prompt_audit_20261102` | `leak_flags.json` | `994d00208c307e2c1c7ab6c530220cbaf8e0fba8078895d815acbc70a2eb2771` | `3716d2d153367562c6b30f04ab91e5186439b58c3281ec201768536a13f90bb3` |
| `prompt_audit_20261102` | `manual_packet.md` | `f3e61da1b5d3bd16c9df510bcedd09fefd346b555a709f1e1d329f6312e618c7` | `1a42377de84e858f87566f9354dac976c183ef6de70d106f5b2b77a57916070b` |
| `prompt_audit_20261102` | `manual_sample.jsonl` | `5dcd69f8bd32e6911ab0afdda9e8bc47f1bb98621c334b86e264fa73f4f8c431` | `ab628b712d32f359540c88a7b2c17c97c8553688240c0e5b1f62336b8d68816d` |
| `prompt_audit_20261102` | `random_selection.json` | `eb19326995f51d16eef3091ca717074228444a0b26a71c5925db42cf8e0bca3b` | `80d4ac624dce225636166be05c24f79d873eddd01dd2e937978b811b0164e70c` |
| `prompt_audit_20261102` | `raw_response_coverage.json` | `8935a7593edb47c078286a3bb15620735adba14792b7152adc4fba83c25a5b22` | `6a51a50192a7fc7513b67396c215bc7166c48b3e2560bd62d04135489b9a4060` |
| `prompt_audit_20261102` | `README.md` | `2380e6a4edddbfda410bfec2453fa7dd2d724d3d13fa768770343ab6aa143a2f` | `d4b3df172f4483ce5f652856c10327cb8c12d0f12f10c46261340e291f9618c1` |
| `prompt_audit_20261102` | `RUBRIC.md` | `912a1953200fcef08716532fc09789595cd3563ce524a30de6980c5bdae075fe` | `a834b7b9ffa28b2611c87bbe9b99439040fc6258a036f3d50a845633187b08aa` |
| `prompt_audit_20261102` | `source_hashes.json` | `932ffdf2e446a23384876c1ca4c8cd1a4750ff6ebbf148cafa55cfc041b83d58` | `c6c135dbe3551a63820972ae6a3ebea8a23f5681cbb8731be47dd491bff198ba` |
| `prompt_audit_20261102` | `USER_DECISIONS.json` | `b81d4f27c8a44f3b406d858a6cb6a9f56f2c026553551cfa6ed02d5000b944b1` | `bfa61b2a5cf0c52ce8f2e40f074463b697ca8ca2ef661b41d4265ece85ee9c42` |
| `prompt_audit_20261102` | `verification.json` | `f1a4bd75575aa301fc982399178d82d24a903a62daa59cbcc8d09f0fe94fcd2c` | `ddef32f2564c22e659b4dd32e61e8bcf5f68c419cd55255a8400d088466fb4c7` |
| `prompt_audit_20261102` | `VI_DU_CAN_XU_LY.md` | `52206bb3d1b467e5d4e389c4d994c35f2002f5fe96db5fda0501289395792600` | `b93ae7e0dc8c8d3ed73afce9fa4b292db0bc37c029142dd5ec9c5ab79959520d` |
| `dry_run_validation_20261102` | `blocked_arms.json` | `602ca99ac893b1f2b2819e1f2e79b0a110fe7ec3e520940d8837442a57cd2146` | `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570` |
| `dry_run_validation_20261102` | `KET_QUA.md` | `5272611f51f585c5543871e28ac71e81f6ebb18f0687d1970d9ee56cf0748b6b` | `21951913eca187a25d3512e58dcf3bf31a32da42df17284bef3a10b6a765d8e4` |
| `dry_run_validation_20261102` | `reveal/validation/B1-shuf/44/audit_summary.json` | `ca815d81d1a9606d4a5ec806655d2949153fe83b449dab2efdba30950aa739dc` | `cae9f6d5d679141d29c6af44613293147a68ff11f53135e4afad26aad067579f` |
| `dry_run_validation_20261102` | `source_hashes.json` | `2f2859e240bbdadf469278d93a951a2420a8edc9728ee1c527f7d9d632cdfff5` | `e77b099578aa8b6a7013677136381365d0f2e6f43ec4739be4fdb51a11ae55a9` |
| `dry_run_validation_20261102` | `summary.json` | `1c2d4dbff2765b34297ea78ea581dcf50a25c66d5f547f272e2831aa52229fb1` | `7f28a8b72c8c4733e8e25d9f8ec56ccdfd27b715138733fff64cc272d0fc7674` |
| `dry_run_validation_20261102` | `verification.json` | `409dbb6caeb6c79b6fd0c4a5edd0bba50e8e00c5901702eaca565e64719f45e2` | `dcbbceb5b1a7faa1c2e9fb0bc295c19f731af6b8cb7eda475b74568a4db83dfd` |
