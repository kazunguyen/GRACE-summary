# Đầu vào dựng prompt đã đưa vào Git — 02/11/2026

Phạm vi: Devign validation/test, REVEAL validation/test, cùng train donor dùng chung. Giới hạn từng file: **100 MiB = 104.857.600 byte**. Các file trên ngưỡng được skip và giữ local; không chia nhỏ hoặc sinh cache/model mới.

Trước đợt này chỉ hai contract trong danh sách được Git theo dõi. Đợt này bổ sung 76 file dữ liệu/metadata, tổng danh mục đủ điều kiện 78 file, khoảng 726,35 MiB. [Inventory JSON](prompt_input_inventory_20261102.json) ghi từng đường dẫn, byte, SHA256 và trạng thái trước khi bổ sung. Trạng thái remote được kiểm bằng lệnh verifier dưới đây sau push.

## Nguồn tải các file lớn ngoài Git

[Google Drive — 16 cache/input lớn](https://drive.google.com/drive/folders/1oV49c5JgLJl5sD1_v7NPlDOs0Hik_0Zl?usp=sharing). Tải **GRACE_large_inputs_20261102.zip**, 2272473727 byte (2,12 GiB); dung lượng payload sau giải nén 22,35 GiB.

SHA256 ZIP đã kiểm từ gói local: `ba930b27c769af4c53594f2ce912595ea9276416c392a18139ef09d43c6c63e0`.

Giải nén vào gốc GRACE-summary, giữ cấu trúc đường dẫn; sau đó chạy `python -B VERIFY_RESTORE.py --root .`. ZIP kèm manifest SHA256 từng file và hướng dẫn khôi phục. [Hướng dẫn đầy đủ trong README](../README.md#tải-cache-lớn-từ-google-drive). Link do người dùng cung cấp; checksum lấy từ gói local đã kiểm, không phải kết quả tải lại từ Drive.

## Đã đưa vào Git

| Nhóm | Đường dẫn tính từ repo | Nội dung |
|---|---|---|
| Contract | 01_Author_Baseline_Unified/evaluation_contract.yaml; diagnostic_kit/configs/protocol.yaml trong cùng baseline | Contract/model/tokenizer/budget đã có trước đợt này |
| Raw gốc đang dùng | 01_Author_Baseline_Unified/output/local_full/{devign,reveal}/raw/ | train/validation/test + data_manifest |
| Raw và manifest frozen | 01_Author_Baseline_Unified/output/research_freeze_20261101/ | train/validation/test raw, manifest, stats, near_pairs, freeze_manifest; donors.jsonl có graph bị skip |
| CodeT5 | 01_Author_Baseline_Unified/output/local_full/{devign,reveal}/embedding_cache/{train,validation,test}/ | vectors.npy, manifest, import_provenance; không đưa file .lock |
| Bank frozen dạng compact | Runs-management/donor_reconciliation_20261101/cache/*_new_* | Code/label/AST representation, manifest; Devign có retrieval/whitening cache. Không phải graph nodes/edges đầy đủ |
| B2 donor mới | Runs-management/donor_reconciliation_20261101/new_reference/B2/{dataset}/{validation,test}/ | prompts.jsonl và manifest đủ bốn tập |
| B2 tham chiếu cũ | 01_Author_Baseline_Unified/output/local_full/bundles_recovered_joern_final_20261031/{dataset}/{split}/ | prompts, manifests và bốn ZIP sẵn có dưới ngưỡng; ghi rõ đây là phiên donor cũ |
| Audit CPG nhỏ | 01_Author_Baseline_Unified/output/local_full/cpg_recovered_joern_final_20261031/ | merge_manifest, remaining_missing và summary |

CodeT5 pin: Salesforce/codet5-base@02cd2d31bb7c6d0e4d91156167b2de044989c733. Đã đối chiếu sáu manifest/vector với provenance retrieval, shape N×768 float32, ID và hash code raw frozen. Train Devign có 21.854 vector, REVEAL 18.187; donor hợp lệ sau lọc tương ứng 21.691/17.636. train_raw chứa train gốc; dùng keep_in_bank trong train_manifest khi lấy donor đã chốt.

## Bốn tập mục tiêu

| Tập | Raw frozen | Vector | Vector MiB | CPG Joern MiB (skip) |
|---|---:|---:|---:|---:|
| Devign validation | 2.732 | 2.732 × 768 | 8,00 | 414,51 |
| Devign test | 2.732 | 2.732 × 768 | 8,00 | 392,77 |
| REVEAL validation | 2.273 | 2.273 × 768 | 6,66 | 215,86 |
| REVEAL test | 2.274 | 2.274 × 768 | 6,66 | 237,77 |

Hai vector train lần lượt 64,03 và 53,28 MiB, cũng được đưa vào Git.

## File vượt 100 MiB — tải qua Drive, không push Git

| Đường dẫn từ repo | MiB |
|---|---:|
| 01_Author_Baseline_Unified/output/research_freeze_20261101/devign/donors.jsonl | 3269.00 |
| 01_Author_Baseline_Unified/output/research_freeze_20261101/reveal/donors.jsonl | 1799.67 |
| 01_Author_Baseline_Unified/output/local_full/cpg_recovered_joern_final_20261031/devign/cpg/test.jsonl | 392.77 |
| 01_Author_Baseline_Unified/output/local_full/cpg_recovered_joern_final_20261031/devign/cpg/train.jsonl | 3297.66 |
| 01_Author_Baseline_Unified/output/local_full/cpg_recovered_joern_final_20261031/devign/cpg/validation.jsonl | 414.51 |
| 01_Author_Baseline_Unified/output/local_full/cpg_recovered_joern_final_20261031/reveal/cpg/test.jsonl | 237.77 |
| 01_Author_Baseline_Unified/output/local_full/cpg_recovered_joern_final_20261031/reveal/cpg/train.jsonl | 1828.18 |
| 01_Author_Baseline_Unified/output/local_full/cpg_recovered_joern_final_20261031/reveal/cpg/validation.jsonl | 215.86 |
| 01_Author_Baseline_Unified/output/local_full/bundles_recovered_joern_final_20261031/devign/test/specs.jsonl | 398.91 |
| 01_Author_Baseline_Unified/output/local_full/bundles_recovered_joern_final_20261031/devign/test/specs.jsonl.donors.jsonl | 3275.29 |
| 01_Author_Baseline_Unified/output/local_full/bundles_recovered_joern_final_20261031/devign/validation/specs.jsonl | 420.50 |
| 01_Author_Baseline_Unified/output/local_full/bundles_recovered_joern_final_20261031/devign/validation/specs.jsonl.donors.jsonl | 3275.29 |
| 01_Author_Baseline_Unified/output/local_full/bundles_recovered_joern_final_20261031/reveal/test/specs.jsonl | 241.44 |
| 01_Author_Baseline_Unified/output/local_full/bundles_recovered_joern_final_20261031/reveal/test/specs.jsonl.donors.jsonl | 1799.67 |
| 01_Author_Baseline_Unified/output/local_full/bundles_recovered_joern_final_20261031/reveal/validation/specs.jsonl | 218.95 |
| 01_Author_Baseline_Unified/output/local_full/bundles_recovered_joern_final_20261031/reveal/validation/specs.jsonl.donors.jsonl | 1799.67 |

**Clone/pull vẫn thiếu CPG Joern nguyên bản và donors frozen kèm graph**, nên chưa thể chạy mọi bước dựng lại từ đầu chỉ từ Git. Tải các file này từ link Drive ở đầu tài liệu, rồi khôi phục đúng đường dẫn và hash trong freeze/bundle manifest. Không chạy lại Joern/encoder để lấp thiếu một cách âm thầm.

Bốn ZIP B2 cũ đã tồn tại sẵn (18–34 MiB/file) chứa specs.jsonl, prompts.jsonl, bundle_manifest và specs manifest. Có thể giải nén vào chính thư mục dataset/split tương ứng để khôi phục specs cũ bị skip; kiểm spec_sha256 trước khi dùng. ZIP không chứa donors.jsonl/CPG train đầy đủ và không phải bundle donor mới. B2 new_reference chứa prompt đã chốt donor mới; không ghép lẫn phiên.

## Kiểm sau clone/pull

~~~bash
python -B Runs-management/verify_prompt_inputs_git.py --git-ref origin/baseline-unified
~~~

Verifier chỉ dùng thư viện chuẩn, kiểm size/SHA256 và blob Git của 78 file đủ điều kiện. Các file skip được báo riêng; pass chỉ xác nhận phần đã đưa vào Git, không xác nhận đã có toàn bộ graph local. Git attributes giữ nguyên byte raw/cache để SHA256 không thay đổi do chuyển LF/CRLF.

Các cache donor phiên cũ, môi trường Python, model GGUF/CodeT5 weights và output inference không thuộc lần bàn giao input này. Model/tokenizer pin và nơi cấu hình đã ghi trong README gốc; tải đúng phiên khi dựng môi trường.

## Bằng chứng bàn giao

Commit dữ liệu: `bef5d2ea983c095b2b4e5388ef1ef931da678646`, đã push và kiểm trực tiếp trên `origin/baseline-unified`. Verifier đạt 78/78 file; 16 đường dẫn skip không có trong tree remote. [Kết quả JSON](prompt_inputs_git_verification_20261102.json), [worklog](../worklogs/2026-11-02_prompt_inputs_git_delivery.md).

## Output và bundle B2-rand — nguồn riêng

[Google Drive — bundle prompt, output và checkpoint B2-rand I-09](https://drive.google.com/drive/folders/17VoIiqOO0yArU4_bWYCzkLA2f20rbGzH?usp=sharing). Đây là gói riêng với cache 16 file ở đầu tài liệu. Danh sách 97 file và SHA-256 trong [b2_rand_drive_manifest_20261102.json](b2_rand_drive_manifest_20261102.json); checksum ghi từ bản bàn giao local đã so với nguồn, chưa được xác minh lại trên Drive. Khi tải về, đặt file đúng các đường dẫn `06_Arm_B2_Rand/...` trong manifest. Model GGUF và bundle B2 donor rerun không thuộc gói này.
