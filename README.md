# GRACE-summary — hướng dẫn chạy và bàn giao

Repo làm việc chung cho baseline GRACE và ma trận arm trên Devign/REVEAL. Đọc file này trước khi nhận một lượt chạy. **Tiến độ đã kiểm local ngày 02/11/2026:** B0/B2 đủ output phiên cũ; B1/flip còn dở; rep/rand chưa inference. Output đầy đủ không đồng nghĩa đã nghiệm thu protocol xác nhận.

- [RUNS.md — sổ mọi lượt chạy](Runs-management/RUNS.md): ai chạy, bước nào, đầu vào/đầu ra, thời gian, số mẫu, checkpoint và bằng chứng.
- [HIEN_TRANG.md — số record hiện tại](Runs-management/HIEN_TRANG.md): bảng sinh từ artifact đã nhập local.
- [MA_TRAN_RUN.md — định nghĩa 15 arm](Runs-management/MA_TRAN_RUN.md): tầng, seed, thay đổi từng arm.
- [Tiến độ và điều kiện nghiệm thu](Runs-management/TIEN_DO_PHUONG_AN_2.md): thiếu gì, khi nào được thêm cải tiến.
- [Mục lục Runs-management](Runs-management/README.md): file nào cần giữ, file nào cần cập nhật.

- [Hồ sơ audit prompt/output và kết luận Bước 3](#8-hồ-sơ-audit-và-nghiệm-thu-bước-3): vị trí báo cáo, danh sách cờ và bộ phiếu chấm.

## 1. Flow chung: chạy đúng bước đang thiếu

~~~text
Raw cố định + contract
  → Joern CPG + audit graph                 [J-xx]
  → CodeT5 cache + đối chiếu ID/hash code    [E-xx]
  → freeze donor / retrieval / specs
  → prompt + audit + bundle                [P-xx]
  → validation đủ ID → khóa ngưỡng đúng phiên
  → test → checkpoint / records / manifest  [I-xx]
  → nhập output local → kiểm tra → cập nhật RUNS.md + HIEN_TRANG.md
  → bảng metric/CI + mốc Tầng 1 → mở phiên cải tiến riêng
~~~

**Hiện raw/CPG/CodeT5 đã có cache:** người nhận inference chỉ cần đúng bundle + model + checkpoint. Không chạy lại Joern/encoder/retrieval để tiếp tục checkpoint. Lỗi input/hash/model phải được xử lý trước khi chạy; không âm thầm đổi model hoặc bỏ mẫu.

Trước mỗi lượt, ghi nhận người phụ trách, arm/dataset/split/seed, phiên donor/prompt, tài khoản Kaggle và checkpoint cha trong RUNS.md, trạng thái planned/running. Hai người không nhận trùng cùng phần việc nếu không chủ đích repeat. Người nhận tiếp dùng checkpoint mới nhất của cùng run và kiểm identity, không chỉ dựa vào tên ZIP.

## 2. Contract chung và chỗ tinh chỉnh

Nguồn chuẩn: [evaluation_contract.yaml](01_Author_Baseline_Unified/evaluation_contract.yaml) và [QUY_UOC_FRAMEWORK_20261101.md](Runs-management/QUY_UOC_FRAMEWORK_20261101.md).

| Phạm vi | Tinh chỉnh ở đâu | Quy tắc |
|---|---|---|
| Dataset/model/tokenizer/graph/score | Contract + quy ước trên | Thay đổi phải có phiên mới; không sửa riêng một notebook rồi gộp vào run cũ |
| Dữ liệu đóng băng | 01_Author_Baseline_Unified/freeze_research_data.py và output/research_freeze_20261101 | Không ghi đè snapshot; dùng manifest/hash chung |
| Chọn demo/truy hồi B2 | 01_Author_Baseline_Unified/retrieval_engine.py, prepare_kaggle_bundle.py | Đổi donor/retrieval phải dựng và đối chiếu lại prompt; xem migration B2/flip |
| B0 prompt/runtime | 02_Arm_B0_Source_Only/prepare_b0.py, kaggle_b0_runtime.py và notebook tương ứng | Giữ scaffold trống đã chốt |
| B1/rep ghép cặp | tier1_prompt_tools/prepare_cached.py và notebook01 của arm | Giữ code/graph/demonstration đúng phiên tham chiếu |
| Flip donor mới | 04_Arm_B2_Flip/prepare_frozen_flip.py, kaggle_flip_frozen_runtime.py | Sau sửa source dùng update_frozen_notebooks.py để đồng bộ code nhúng; không sửa I-06 |
| Rand | 06_Arm_B2_Rand/prepare_rand.py và hai notebook | Seed 42/43/44; donor mới; kiểm prompt và seed identity |
| Khóa ngưỡng | Runs-management/validation_lock.py; hướng dẫn TU_DONG_KHOA_NGUONG.md | Fit đủ validation đúng phiên; không dùng test; không ghi đè khóa lịch sử |

Giá trị đã chốt: Qwen3-Coder-30B-A3B-Instruct GGUF **Q4_K_M**, SHA256 **f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335**, llama-cpp-python **0.3.16**, tokenizer Qwen revision **b2cff646eb4bb1d68355c01b18ae02e7cf42d120**. Context 8.192 gồm chat wrapper và reserve 64; code 3.000, mỗi demo 1.500, graph 1.500 token, tối đa40 node/80 edge. Score lấy hai logits gốc, top5 chỉ chẩn đoán; valid score/raw response báo riêng. Full validation Devign 2.732/REVEAL 2.273.

Có thể chỉnh đường dẫn input/model, thời lượng phiên, thời gian dự phòng và checkpoint trong cell cấu hình. Đổi LIMIT phải dùng output thử riêng; không ghép subset thử với khóa full validation. Notebook nhúng code không tự thay theo file .py local: phải đồng bộ phần nhúng và kiểm tra trước khi upload bản mới. Sửa code local không sửa tiến trình đang chạy trên Kaggle.

## 3. Các arm đã chạy, còn gì tiếp theo?

Mỗi arm Tầng 1 dự kiến **10.011 mẫu** =5.005 validation+5.006 test. Thứ tự bốn số: Devign val/test; REVEAL val/test.

| Arm | Đã có output | Tiếp theo / điều kiện |
|---|---|---|
| B0 | 2.732/2.732; 2.273/2.274 — đủ 10.011, I-03 | Giữ output. Không rerun vì donor; cần ghi đúng lịch sử khóa sau test và raw invalid |
| B1 | 2.732/429; 2.273/0 — 5.434, I-07 | Còn 4.577. Notebook hiện chưa có gate khóa: đồng bộ/kiểm gate và khóa validation trước test mới; không Run All hiện tại để tiếp tục test |
| B2 | 2.732/2.732; 2.273/2.274 — đủ 10.011, I-05 | Phiên donor mới cần66 Devign (28val+38 test); helper B2 riêng có nhưng notebook B2 cũ chưa nhúng gate |
| B2-flip | 2.732/230; 2.273/0 — 5.235, I-06 | Bundle/runtime donor mới đã chuẩn bị; giữ 5.202 output, sửa 33 và chạy 4.776 thiếu =4.809 lượt bổ sung |
| B2-rep | Chưa có output; mới có notebook prompt | Chốt B2 donor mới, prompt giống từng ký tự, tạo/nghiệm thu runner gọi mới model; không response cache B2 |
| B2-rand | Đủ 12 bundle/3seed, có notebook; chưa có output | Ưu tiên Tầng 1. Notebook hiện chạy B2 rerun-66 trước, sau đó rand; nếu nhận chạy phải nhận cả luồng này, chưa có công tắc rerun-only |
| Arm Tầng 2/3 còn lại | Chưa có inference được xác nhận trong repo | Chọn theo MA_TRAN_RUN.md, chuẩn bị/audit runner trước khi cấp GPU |

**Việc ưu tiên phối hợp:** một người có thể nhận flip donor mới; người còn lại xử lý gate B1/B2 và lên lịch B2 rerun-66. Chỉ nhận GPU khi đầu vào/phiên/gate của phần việc đã được kiểm. Đây là gợi ý phân công, chưa đặt chủ sở hữu hay tự khởi chạy run.

## 4. Chạy arm nào: mở gì, chỉnh gì, input gì?

Các đường dẫn dưới đây tính từ thư mục arm. Mở notebook01 trên local/WSL; notebook02 trên Kaggle. Đọc cell cấu hình theo tên biến, không dựa vào số cell vì có thể thay đổi.

| Arm / folder | Chuẩn bị prompt local | Inference / input Kaggle | Biến vận hành |
|---|---|---|---|
| B0 — [02](02_Arm_B0_Source_Only/README.md) | notebooks/01_prepare_b0_prompts.ipynb → output/bundles/grace_b0_inputs.zip | notebooks/02_kaggle_qwen_q4_b0.ipynb + ZIP + GGUF + checkpoint nếu resume | EXPECTED_RUNS, MAX_RUNTIME_HOURS=8, RESUME, MODEL_OVERRIDE, OUT_ROOT |
| B1 — [03](03_Arm_B1_Graph_Only/README.md) | notebooks/01_prepare_b1_prompts.ipynb → output/bundles/grace_b1_inputs.zip | notebooks/02_kaggle_qwen_q4_b1.ipynb + ZIP + GGUF + grace_b1_checkpoint.zip | EXPECTED_RUNS, MAX_RUNTIME_HOURS=7, RESUME, MODEL_OVERRIDE, OUT_ROOT; gate đang thiếu |
| B2 — [01](01_Author_Baseline_Unified/README.md) | notebooks/01_prepare_grace_b2.ipynb đọc cache; không dùng để đổi donor ngầm | notebooks/02_kaggle_qwen_q4_b2.ipynb cho phiên cũ; donor rerun66 xem folder 07/06 | DATASETS/SPLITS/CPG_ROOT/BUNDLE_ROOT local; EXPECTED_RUNS, RESUME_FROM_CHECKPOINT, CHECKPOINT_INPUT_PATH, MAX_RUNTIME_HOURS=8 trên Kaggle |
| Flip mới — [04](04_Arm_B2_Flip/README.md) | notebooks/01_prepare_b2_flip_prompts.ipynb → output/bundles_frozen_donor_20261101/grace_b2_flip_frozen_donor_inputs.zip | notebooks/02_kaggle_qwen_q4_b2_flip.ipynb + ZIP mới + GGUF + checkpoint I-06 | RESUME_FROM_CHECKPOINT=True, CHECKPOINT_INPUT_PATH, MAX_RUNTIME_HOURS=9+35/60, OUT_ROOT; giữ EXPECTED_VARIANT/donor hash |
| Rep — [05](05_Arm_B2_Rep/README.md) | notebooks/01_prepare_b2_rep_prompts.ipynb; REFERENCE_ROOT hiện vẫn là B2 cũ | Chưa có notebook02. Phải cập nhật tham chiếu tới phiên B2 cuối và nghiệm thu runner trước | PROJECT_ROOT_OVERRIDE, REFERENCE_ROOT, RUNS; không tự đổi tên B2 response thành rep |
| Rand — [06](06_Arm_B2_Rand/README.md) | notebooks/01_prepare_b2_rand_prompts.ipynb → output/bundles/grace_b2_rand_inputs.zip | notebooks/02_kaggle_qwen_q4_b2_rand.ipynb + ZIP rand + ZIP66 + GGUF + checkpoint rand khi tiếp tục | SEEDS=(42,43,44), MAX_RUNTIME_HOURS=9, LIMIT=None, RESUME_FROM_CHECKPOINT (mặc định False; đổi True khi resume), CHECKPOINT_INPUT_PATH |
| B2 rerun66 — [07](07_Arm_B2_Donor_Rerun_66/README.md) | build_bundle.py → output/grace_b2_devign_donor_rerun_66_20261102.zip; verify_bundle.py để kiểm | Chạy trong notebook02 của folder06; không phải arm mới | Giữ28 validation+38 test và2.704 score reusable; không fit tau trên28 mẫu |

Chữ 11h trong tên OUT_ROOT rand là tên thư mục cũ; **ngân sách thực tế đọc MAX_RUNTIME_HOURS=9**, không suy thời lượng từ tên output. EXPECTED_RUNS không tách được phase rand của vòng lặp cuối; muốn chế độ rerun-only phải sửa/nghiệm thu runner riêng trước, không coi đã có sẵn.

### Ví dụ A — nhận tiếp B2-flip từ I-06

1. Gắn ZIP frozen_donor mới, GGUF đúng SHA và checkpoint I-06 vào Kaggle Input, bật2 × T4 + Internet.
2. Trong cell cấu hình, giữ RESUME_FROM_CHECKPOINT=True; chỉ đặt CHECKPOINT_INPUT_PATH nếu có nhiều checkpoint trùng tên.
3. Chạy theo thứ tự. Runtime giữ 5.202 record, sửa 28 validation, ghép đủ validation để khóa ngưỡng, sửa 5 test rồi chạy phần thiếu. Không đổi model, seed, donor hash/variant.
4. Tải checkpoint và diagnostics khi phiên dừng; đọc checkpoint_status.json/migration_plan.json để biết dừng đến đâu. Phiên sau dùng **checkpoint mới**, không trở lại I-06 nếu đã có kết quả mới.
5. Nhập vào output/<run_id_mới>/, kiểm hash/ID và ghi I-xx mới có parent I-06 vào RUNS.md. Đây là resume/migration của cùng arm, không phải repeat.

Chi tiết: [B2_FLIP_DONOR_MOI_RESUME.md](Runs-management/B2_FLIP_DONOR_MOI_RESUME.md).

### Ví dụ B — chuẩn bị tiếp B1

Trong cell cấu hình notebook02:

~~~python
EXPECTED_RUNS = [('devign', 'validation'), ('reveal', 'validation')]
RESUME = True
~~~

Gắn bundle B1 và checkpoint I-07. Hai validation đã có đủ nên không cần suy luận lại nếu hash/identity khớp. **Đây chỉ là cấu hình validation; chưa thay cho gate**. Trước khi thêm test vào EXPECTED_RUNS: tích hợp helper, tạo khóa đúng phiên từ đủ validation, kiểm gate/runtime và lưu khóa cùng checkpoint. Sau đó mới resume4.577 test thiếu; giữ lịch sử429 test đã chạy. Chưa thực hiện sửa runtime hoặc khóa mới trong đợt viết README này.

## 5. Dữ liệu lưu ở đâu?

| Giai đoạn | Artifact chính | Vị trí local / nơi bàn giao |
|---|---|---|
| Raw | train/validation/test.jsonl, manifest nguồn | 01_Author_Baseline_Unified/output/local_full/<dataset>/raw/ |
| Joern | CPG JSONL, manifest, journal retry/audit | output/local_full/cpg_recovered_joern_final_20261031/ của baseline; bản mới phải dùng thư mục phiên mới |
| CodeT5 | vectors.npy + manifest.json theo split, float32/768d | output/local_full/<dataset>/embedding_cache/<split>/ của baseline |
| Freeze | raw/manifest/donors/stats và freeze_manifest.json | baseline/output/research_freeze_20261101/ |
| B2 tham chiếu donor mới | prompts.jsonl + manifest từng dataset/split | Runs-management/donor_reconciliation_20261101/new_reference/B2/ — vẫn là input đang dùng |
| Prompt/bundle | prompts.jsonl, pairing_audit, manifest/hash, ZIP | output/bundles/ của arm; flip mới dùng output/bundles_frozen_donor_20261101/ |
| Inference | records.jsonl, run_manifest.json, evaluation.json, checkpoint_status.json; khóa khi runtime đã tích hợp | Kaggle OUT_ROOT rồi tải về <arm>/output/<run_id>/, giữ ZIP/log gốc |
| Flip migration | migration_plan, history/stale_records, original_checkpoint | OUT_ROOT flip mới; không ghi đè I-06 |
| B2 rerun66/rand | B2 ở b2_donor_rerun_66/; rand ở seed_<seed>/<dataset>/<split>/ | OUT_ROOT của notebook rand; không cộng66 như arm mới hoặc nhân đôi record reusable |
| Quản lý | nhật ký, trạng thái, ngưỡng, bằng chứng liên kết | Runs-management; không bỏ cả prediction/embedding vào đây |

B2 lịch sử đã hợp nhất ở baseline/output/local_full/inference_qwen_q4_b2_20261101/. Các nguồn B0/B1/flip gốc được liên kết trong RUNS.md. Không đè file cũ khi tải run mới; không gộp checkpoint khác prompt/model chỉ vì ID giống nhau.

### Người nhận chỉ chạy inference

Cần notebook inference đúng phiên, ZIP prompt, model GGUF đúng SHA, checkpoint mới nhất nếu resume; rand còn cần ZIP66. Khi dừng, gửi lại ZIP checkpoint + diagnostics + đường dẫn/tài khoản phiên và thông tin RUNS.md. Không gửi token API hoặc .env trong gói.

### Người nhận tái tạo prompt/dữ liệu

Đợt bàn giao input 02/11/2026 đưa raw gốc/frozen, manifest, CodeT5 vectors cho cả train/validation/test của hai dataset, compact donor bank mới và B2 new_reference vào Git. **CPG Joern, donors frozen kèm graph và specs nguyên bản vượt 100 MiB được skip**, nên clone/pull vẫn chưa đủ để tái dựng mọi bước từ đầu. Tải file skip qua Google Drive ở mục bên dưới và khôi phục đúng đường dẫn/hash. Không cần gửi .venv-wsl/ hoặc uv-cache/; tạo môi trường lại từ requirements.

Nếu thật sự cần dựng lại: notebook01 B2 mặc định DOWNLOAD_RAW=False, REBUILD_CPG=False và chỉ đọc sáu cache hoàn tất. Đổi CPG_ROOT/BUNDLE_ROOT sang phiên mới trước khi rebuild; chỉnh JOERN_HOME, BATCH_SIZE/JAVA_OPTS trong notebook recovery. CodeT5 encoder nằm ở prepare_embedding_cache.py (--raw-dir, --out, --batch-size), chạy WSL/Linux do có fcntl; không nhầm việc notebook01 đọc CachedEmbedder với chạy encoder mới. Hướng dẫn cũ của baseline có đoạn lịch sử; lấy cell cấu hình hiện tại và contract làm chuẩn.

### Tình trạng input trong Git — 02/11/2026

Danh mục **78 file đủ điều kiện**, trong đó 2 contract đã có trước và 76 file được bổ sung; **16 file trên 100 MiB không push Git; tải qua Google Drive ở mục bên dưới**. [Danh sách từng file/size/hash và file skip](Runs-management/PROMPT_INPUTS_GIT_20261102.md), [inventory JSON](Runs-management/prompt_input_inventory_20261102.json).

| Input | Phạm vi đã đưa vào Git |
|---|---|
| Contract | evaluation_contract.yaml và diagnostic_kit/configs/protocol.yaml của baseline |
| Raw/freeze | Đủ Devign/REVEAL validation/test; kèm train, train_manifest/keep_in_bank, stats, near_pairs và freeze_manifest |
| CodeT5 | Sáu bộ vectors.npy + manifest/provenance: train/validation/test của mỗi dataset; N×768 float32, đã khớp ID/hash code và checksum retrieval |
| Donor mới | Compact bank 21.691 Devign + 17.636 REVEAL, manifest/retrieval/whitening hiện có và prompt B2 new_reference đủ bốn tập |
| Graph/specs | Manifest/audit nhỏ và bốn ZIP B2 cũ có specs; CPG nguyên bản 6 file, donors graph 2 file, specs/donor copies 8 file vượt ngưỡng nên skip |

Bốn vector mục tiêu lần lượt 2.732/2.732/2.273/2.274 dòng (Devign val/test, REVEAL val/test), mỗi file 6,66–8,00 MiB. Vector train 64,03/53,28 MiB cũng được đưa vào Git. Raw train frozen vẫn gồm mẫu bị loại; dùng keep_in_bank hoặc compact new_bank khi lấy donor đã chốt. Compact AST representation không thay thế full CPG nodes/edges.

Kiểm input đã lấy từ remote, dùng Python chuẩn:

~~~bash
python -B Runs-management/verify_prompt_inputs_git.py --git-ref origin/baseline-unified
~~~

Pass xác nhận 78 file đủ điều kiện có đúng byte/hash ở local và ref Git. Các graph lớn vẫn cần chuyển riêng; ZIP B2 cũ giúp khôi phục specs cũ, không chứa toàn bộ graph donor và không phải phiên donor mới.

Đã xác minh push dữ liệu tại commit `bef5d2e` trên `origin/baseline-unified`: 78/78 file khớp byte/hash, 16 file skip không có trong tree remote. [Bằng chứng kiểm remote](Runs-management/prompt_inputs_git_verification_20261102.json), [worklog bàn giao](worklogs/2026-11-02_prompt_inputs_git_delivery.md).

### Bundle và checkpoint B2-rand trên Google Drive

[Google Drive — output B2-rand, bundle và checkpoint I-09](https://drive.google.com/drive/folders/17VoIiqOO0yArU4_bWYCzkLA2f20rbGzH?usp=sharing). Link do người dùng cung cấp; chưa tải lại hoặc xác minh nội dung trên Drive. Gói bàn giao local gồm 97 file, 347.745.695 byte, kể cả notebook có output; đối chiếu theo [manifest SHA-256](Runs-management/b2_rand_drive_manifest_20261102.json).

Bundle Kaggle `grace_b2_rand_inputs.zip` SHA-256: `684167868f69b55c62409eb1c97802a9bda10a8bac613404b527096933ef0014`. Checkpoint `grace_b2_rand_checkpoint.zip` SHA-256: `9b8f1e3c365085a684490928a200b6a4cd065f12dcf0dcf90d5a9f59738d6e92`. Khi khôi phục, đặt các file dưới `06_Arm_B2_Rand/output/` đúng cấu trúc trong manifest; notebook có output lưu riêng trong `06_Arm_B2_Rand/notebooks/`. Model GGUF và bundle donor rerun là nguồn riêng.

### Tải cache lớn từ Google Drive

**[Google Drive — cache Joern/donor/specs để tái sử dụng dựng prompt](https://drive.google.com/drive/folders/1oV49c5JgLJl5sD1_v7NPlDOs0Hik_0Zl?usp=sharing)**. Đây là nguồn tải 16 file lớn không được đưa vào Git, do người dùng cung cấp ngày 02/11/2026.

1. Clone/pull repo để lấy contract, raw/freeze, sáu cache CodeT5 và B2 reference đã đưa vào Git.
2. Mở link Drive trên, tải GRACE_large_inputs_20261102.zip (2.272.473.727 byte, khoảng 2,12 GiB).
3. Kiểm SHA256 của ZIP so với giá trị đã kiểm từ gói local:

~~~text
ba930b27c769af4c53594f2ce912595ea9276416c392a18139ef09d43c6c63e0
~~~

Trên PowerShell:

~~~powershell
Get-FileHash .\GRACE_large_inputs_20261102.zip -Algorithm SHA256
~~~

4. Giải nén ZIP vào **gốc thư mục GRACE-summary**, giữ nguyên cấu trúc 01_Author_Baseline_Unified/output/...; không đặt thêm một tầng thư mục. Ví dụ trên Windows:

~~~bash
python -m zipfile -e D:/Downloads/GRACE_large_inputs_20261102.zip D:/JUNIOR/LabThayTho/GRACE-summary
~~~

5. Từ gốc repo, kiểm 16 file vừa khôi phục và 78 input đã lấy qua Git:

~~~bash
python -B VERIFY_RESTORE.py --root .
python -B Runs-management/verify_prompt_inputs_git.py --git-ref origin/baseline-unified
~~~

ZIP có đủ 16 payload (22,35 GiB sau giải nén), kèm DRIVE_INPUTS_MANIFEST_20261102.json, README_RESTORE.md và VERIFY_RESTORE.py. Sáu CPG Joern và hai donor frozen kèm graph giúp phục hồi các input lớn; bốn specs/bốn donor copies B2 cũ giữ đúng phiên lịch sử. **B2 donor mới dùng new_reference/B2 trong Git**; giữ riêng phiên donor cũ/mới khi dựng prompt.

## 6. Chạy xong một lượt phải ghi vào file nào?

**Bắt buộc với mọi lượt, kể cả timeout/lỗi:** cập nhật [Runs-management/RUNS.md](Runs-management/RUNS.md).

| Lượt vừa chạy | Mục trong RUNS.md | Tối thiểu phải liên kết |
|---|---|---|
| Parse/retry/merge/audit Joern | Mục1, J-xx | input/output CPG, manifest/journal, số recovered/still_missing, đã merge hay chỉ candidate |
| Encode/nhập/kiểm cache CodeT5 | Mục2, E-xx | ID/hash code, model revision, chiều/số vector, manifest; phân biệt encode mới với reuse/import |
| Retrieval/specs/prompt/ZIP | Mục3, P-xx | arm/dataset/split/seed, donor/ref version, số prompt, audit, token/graph thiếu, hash ZIP/manifest |
| Inference/resume/migration | Mục4, I-xx | arm/dataset/split/seed, owner/account, parent checkpoint, count duy nhất, score/raw invalid riêng, khóa đúng phiên, hash output/checkpoint và thời gian từ log |

Không lấy mtime hoặc thời gian commit làm runtime. Run có chuẩn bị nhưng chưa gọi LLM ghi rõ prepared/planned, không gán completed. Sau mỗi phiên resume có kết quả mới, thêm dòng phiên mới và liên kết parent; không cộng toàn bộ checkpoint lũy kế thành số lượt mới.

Sau khi nhập và đối chiếu output inference:

~~~bash
python -B Runs-management/refresh_current_status.py
~~~

Lệnh này chỉ đọc các nguồn trong SOURCES và ghi current_status.json + HIEN_TRANG.md; **không tự tải Kaggle, không tự chọn khóa ngưỡng và không sửa RUNS.md**. Khi có nguồn canonical mới, cập nhật SOURCES và đường dẫn prompt tương ứng trong script sau khi xác minh phiên. Không trỏ source full-split vào riêng66 prompt hoặc trộn ba seed rand: helper hiện chưa tự merge migration/đa seed; cần adapter theo phiên/seed trước khi đưa các nguồn đó vào bảng tự động. Chưa nhập/kiểm output mới thì giữ số đã xác minh và ghi pending verification trong sổ.

Đổi tiến độ/kế hoạch → cập nhật MA_TRAN_RUN.md và TIEN_DO_PHUONG_AN_2.md nếu cần. Đổi protocol/phương pháp → ghi CHANGES_AFTER_ANALYSIS_LOCK.md. Không sửa tay HIEN_TRANG.md/current_status.json cho đẹp, không ghi đè thresholds.json bằng ngưỡng phiên mới.

## 7. Khi nào thêm cải tiến?

1. **Làm trước run tiếp:** sửa lỗi contract/gate, donor migration, audit và provenance; lưu đúng lịch sử test đã chạy trước khóa.
2. **Có thể tích hợp sớm:** group-aware OOF, routing paired CI, evaluator offline của Hiếu nếu giữ nguyên prompt/model/score và dữ liệu inference, có kiểm thử/ghi cấu hình phân tích mới.
3. **Chốt mốc Tầng 1:** B0/B1/B2/flip/rep đủ hai dataset và hai split cùng phiên contract; repeat độc lập; ngưỡng đúng validation; audit được nghiệm thu; có bảng metric/CI/net sensitivity làm mốc; đã chốt cách diễn giải run lịch sử với thầy. Hiện **chưa đạt mốc này**.
4. **Sau mốc đó mới mở cải tiến phương pháp** như retrieval/demo/graph/model/prompt mới: branch/variant + input/output/ngưỡng riêng, amendment có thời điểm, so ghép cặp với baseline đã khóa. Không thay baseline đang chạy để thử cải tiến rồi trộn output.

Các arm Tầng 2/3 đã định nghĩa trong ma trận là ablation theo kế hoạch, không phải cải tiến phát sinh. Chi tiết điều kiện ở [TIEN_DO_PHUONG_AN_2.md](Runs-management/TIEN_DO_PHUONG_AN_2.md).


## 8. Hồ sơ audit và nghiệm thu Bước 3

**Nơi lưu audit:** [Runs-management/prompt_audit_20261102/](Runs-management/prompt_audit_20261102/README.md).

- [Kết luận và các cờ cần theo dõi](Runs-management/prompt_audit_20261102/KET_QUA.md); [đối chiếu chính xác Bước 3](Runs-management/prompt_audit_20261102/BUOC_3_DOI_CHIEU.md).
- [audit_summary.json](Runs-management/prompt_audit_20261102/audit_summary.json): thống kê theo arm/phiên/seed/dataset/split, token p50/p95, cắt, demo rỗng, graph thiếu; [audit_rows.csv](Runs-management/prompt_audit_20261102/audit_rows.csv): kết quả từng prompt.
- [final_status.json](Runs-management/prompt_audit_20261102/final_status.json): kết luận sau phân loại cảnh báo nhầm; [verification.json](Runs-management/prompt_audit_20261102/verification.json): kiểm nguồn/hash/score và hồ sơ chấm; [source_hashes.json](Runs-management/prompt_audit_20261102/source_hashes.json): provenance.
- [Danh sách cờ cuối](Runs-management/prompt_audit_20261102/remediation_final.csv), [68 dòng đã inference cần xem](Runs-management/prompt_audit_20261102/executed_needing_review.csv), [ví dụ demo dưới 25%](Runs-management/prompt_audit_20261102/VI_DU_CAN_XU_LY.md).
- [Bộ 60 prompt chấm](Runs-management/prompt_audit_20261102/manual_packet.md), [mẫu JSONL](Runs-management/prompt_audit_20261102/manual_sample.jsonl), [rubric](Runs-management/prompt_audit_20261102/RUBRIC.md), [phiếu người 1](Runs-management/prompt_audit_20261102/reviewer_1.csv), [phiếu người 2](Runs-management/prompt_audit_20261102/reviewer_2.csv), [biên bản phân xử](Runs-management/prompt_audit_20261102/BIEN_BAN_PHAN_XU.md). Hai phiếu đã được Reviewer 1 (HuuHieu03) và Reviewer 2 (Dung) điền độc lập; Cohen's Kappa đạt κ = 0.8507 (đa lớp) và κ = 0.8485 (nhị phân); biên bản phân xử giải quyết thống nhất toàn bộ trường hợp.

**Phạm vi 100.110 prompt/40 tập:** B0 10.011, B1 10.011, B2 20.022 (donor cũ + mới), B2-flip 20.022 (cũ + mới), B2-rep 10.011, B2-rand 30.033 (seed42/43/44). Đây là số dòng audit, có prompt trùng giữa phiên và rep, không phải 100.110 lượt inference độc lập. Output đã đối chiếu là 30.691; toàn bộ score khớp phép tính lại từ logprob. Cache/output lớn vẫn ở local, không tự có sau clone.

**Dry-run validation mới — 02/11/2026:** đã dựng **70.070 dòng prompt/28 tập** cho **10 arm**: B0, B1, B1-full, B1-shuf, B2, B2-rand, B2-nolabel, B2-labelonly, B2-flip, B2-rep. B1-shuf và B2-rand có seed42/43/44; các arm khác seed42. Sau đối chiếu nguồn, **28/28 tập đạt audit tự động**, 0 lỗi dựng và 0 cờ nhãn chưa giải quyết trong phạm vi kiểm tra. Bộ dò gốc giữ 27 pass + 1 needs_review; cảnh báo còn lại là chuỗi Label trong node donor bị cắt, đã truy đúng nguồn frozen. [Báo cáo](Runs-management/dry_run_validation_20261102/KET_QUA.md), [hồ sơ và lệnh tái tạo](Runs-management/dry_run_validation_20261102/README.md), [kiểm bàn giao](Runs-management/dry_run_validation_20261102/verification.json), [kết luận cuối](Runs-management/dry_run_validation_20261102/final_status.json).

Giữ **176 dòng cờ demo** và **390 dòng thiếu graph** trong [562 dòng cần theo dõi](Runs-management/dry_run_validation_20261102/review_flags.csv); các loại có giao nhau. 30 target thiếu graph vẫn xuất hiện ở cả ba seed B1-shuf với graph trống/cờ missing. Mỗi tập đạt demo rỗng ≤1%, cao nhất 24/2.732 = 0,878%. Đã tạo [60 mẫu chấm đúng phiên dry-run](Runs-management/dry_run_validation_20261102/manual_packet.md), [rubric cho 10 arm](Runs-management/dry_run_validation_20261102/RUBRIC.md) và hai phiếu trống. Năm arm B1-H2/B3/B3-nodiff/B3-swap/B3-flip giữ blocked do thiếu đầu vào. Không inference LLM hoặc tính ngưỡng; số output đã nhập giữ nguyên.

### Kết luận Bước 3 trong Phương án 2

Nguồn: [đề cương PDF, trang 18–19](../REPORT_TO_TEACHER/20261029/PhuongAn2_De_cuong_nghien_cuu_GRACE_hop_nhat.pdf). **Chưa hoàn thành toàn bộ Bước 3.**

| Yêu cầu | Tình trạng |
|---|---|
| pytest tests/test_probes.py | 20/20 pass; thêm 4/4 test bộ chạy dry-run; không tuyên bố mọi test notebook đều xanh |
| Dry-run/audit validation đủ 15 arm | Đã đủ validation 10 arm/28 tập, 70.070 dòng; 5 arm H2/B3 blocked do thiếu đầu vào |
| Báo cáo toàn vẹn, token p50/p95, cờ cắt/graph thiếu và rò rỉ nhãn | Có trên 40 tập hậu kiểm và 28 tập dry-run; đọc kết luận sau phân loại cảnh báo cùng số liệu bộ dò gốc |
| Demo rỗng ≤1% | Đạt ở cả 40 tập hậu kiểm và 28 tập dry-run; cao nhất 24/2.732 = 0,878% |
| Hai người đọc 30 prompt mỗi dataset | Đã chuẩn bị 60 mẫu/phiếu đúng phiên dry-run 10 arm; chưa có chấm thực tế |
| Audit trước khi gọi LLM | Dry-run mới là chuẩn bị trước inference tương lai; hồ sơ hậu kiểm không đổi lịch sử các run đã chạy |

**Lưu ý quan trọng:** demo dưới 25% gốc là cờ ở cấp từng prompt, còn tiêu chí nghiệm thu trong PDF là tỷ lệ demo rỗng **≤1%**. Trong hồ sơ hậu kiểm 100.110 dòng có 403 dòng bị gắn cờ, trong đó 68 dòng đã inference, không tự động đồng nghĩa toàn bộ arm trượt hoặc phải chạy lại; mọi tập hiện có đều dưới 1%. Giữ danh sách để theo dõi, không xóa cờ. Các nhãn cần xử lý trong báo cáo audit ban đầu phải đọc cùng ngưỡng 1% khi đánh giá Bước 3.

Cách ghi tiến độ: **Đã hoàn tất dry-run/audit toàn validation cho 10 arm đủ đầu vào; Bước 3 còn thiếu 5 arm H2/B3 và hai người chấm.** Audit 100.110 dòng là hồ sơ hậu kiểm riêng, không cộng với dry-run thành số lượt inference. Các artifact cũ ghi 9 arm chưa chuẩn bị phản ánh phạm vi trước lượt dry-run này. Trước inference tiếp theo, dùng đúng phiên prompt/manifest đã audit; giữ nguyên score/ngưỡng/snapshot và trạng thái OSF.
