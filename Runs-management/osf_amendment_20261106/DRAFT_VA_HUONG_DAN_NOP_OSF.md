# Dự thảo cập nhật đăng ký OSF và hướng dẫn nộp

Ngày soạn: 06/11/2026 (Asia/Bangkok). Trạng thái: DRAFT, chưa nộp OSF.

Bản tiếng Anh để điền form: [OSF_UPDATE_EN.md](OSF_UPDATE_EN.md). Lý do cập nhật để sao chép: [OSF_JUSTIFICATION_EN.txt](OSF_JUSTIFICATION_EN.txt). Quy trình nộp từng bước: [HUONG_DAN_NOP_OSF.md](HUONG_DAN_NOP_OSF.md). Bản update dẫn bằng chứng B0/B1 ở commit d9127fc7b12a128d8499012454ad134733f810ff, Kaggle B1-H2 ở 4838a55135e2d9a5b19292815e3c4b5a12467ed9, retrospective I-14/reanalysis ở 90c5b3ff5f5e86927ab2a8b451c99c458fcddcaf, B3 algorithm implementation/feasibility ở f445a30c8315aeb6c49337acde6cf9df0ac0d6f8 và source screening/smoke-test log ở 6f6dfd2ecf02530b73a8e9576fbe1f87b9121297; phần bên dưới được giữ làm bản làm việc và đối chiếu.

Bổ sung B1-H2: Kaggle đã hoàn tất validation 5.005 mẫu và khóa tau từ validation-only: Devign 0,09 (MCC 0,0667928192), ReVeal 0,21 (MCC 0,0836323479). Ngưỡng Colab 0,09/0,67 chỉ là bằng chứng lịch sử exploratory/superseded. Chưa ghi nhận inference test Kaggle mới trong hồ sơ hiện tại; chỉ được chạy sau khóa này.

Đăng ký gốc: https://osf.io/fqgh2/overview

Tài liệu gốc: `Runs-management/osf_registration_draft_20261102/output/pdf/GRACE_OSF_PREREGISTRATION_20261102.pdf`.
SHA-256 PDF gốc: `22648ead896baf5c1032de700c12fb97bd6dc44f0a8049292532ae6c0468b14c`.

Đây là tài liệu mới, không thay PDF/ZIP gốc. Thuật toán B3 theo phương án người dùng chọn đã được implement và kiểm thử phần mềm; tuy nhiên chưa có cặp thật được duyệt, prompt B3 thực được đóng băng hay inference B3 nào được chạy. Phương án: thay B3 trong ma trận bằng cặp cùng hàm trước/sau vá, cùng các probe tương ứng.

## 1. Quy trình trên OSF

1. Đăng nhập bằng tài khoản có quyền Admin của đăng ký. Mở đăng ký gốc, chọn `Updates` rồi `Update`. Cũng có thể vào `My Registrations` > `Submitted` > `Update`.
2. Dán phần A bên dưới vào ô `Justification`.
3. Sửa các câu trả lời liên quan trong form bằng phần B. Nếu form ban đầu chỉ chứa một mục mô tả và PDF đính kèm, bổ sung nội dung thay thế vào mục văn bản cập nhật được, ghi rõ các mục/trang của PDF được đính chính. Chỉ ghi lý do trong Justification chưa đủ: OSF yêu cầu thay ít nhất một trường câu trả lời.
4. OSF không cho thêm/xóa/thay tệp trong Update. Nếu cần chia sẻ bản đính chính dưới dạng tệp, lưu riêng trên OSF Project liên kết hoặc kho Git công khai; dẫn URL tới phiên bản/commit cố định và SHA-256 trong câu trả lời cập nhật. File trên Project là tài liệu hỗ trợ; phần phương pháp cốt lõi vẫn phải nằm trong nội dung update. Chỉ thêm URL công khai đã tồn tại, không dán đường dẫn máy tính hoặc URL dự kiến.
5. Chọn Review, đọc lại nội dung thay đổi rồi Submit. Các Admin nhận email phê duyệt; OSF mô tả thời gian tự phê duyệt 48 giờ nếu không có phản đối, với ngoại lệ registry có kiểm duyệt. Ghi trạng thái thực tế, không ghi đã duyệt khi còn `Update in progress`.
6. Sau khi update được công khai, lưu URL/version/thời điểm hiển thị và bản sao nội dung update vào thư mục mới. Ghi nhận trong `CHANGES_AFTER_PREREG.md`. Tạo commit/tag mới nếu cần, sau khi kiểm tra tên chưa dùng; không sửa tag hoặc nhánh niêm phong cũ. Khóa Colab cũ được giữ nguyên làm bằng chứng lịch sử; khóa Kaggle mới phải là artifact/version mới, không ghi đè lịch sử.

Nguồn quy trình: [OSF Support - Update a Registration](https://help.osf.io/article/330-welcome-to-registrations#Update-a-Registration). Tên câu hỏi cụ thể tùy template đã dùng; đây không phải xác nhận trực tiếp form trong tài khoản của nhóm.

## 2. Đối chiếu nội dung cần cập nhật

| Vị trí trong PDF gốc | Nội dung cần đính chính hoặc bổ sung |
|---|---|
| Trang 1-2, mục 1 và exposure ledger | Khai báo phân tích lại 06/11, Colab B1-H2 validation/test exploratory đã thực hiện, cùng kết quả Kaggle validation đã hoàn tất và khóa; không khẳng định các hoạt động này chưa xảy ra. |
| Trang 4, mục 3.2 | Sửa bốn ngưỡng B0/B1 theo toàn bộ validation; giữ quy tắc tối ưu và ngưỡng kế thừa cho probe. |
| Trang 4, mục 3.2 và trang 6, ma trận B1-H2 | Bổ sung kết quả Kaggle validation đã khóa: Devign tau=0,09 (MCC 0,0667928192); ReVeal tau=0,21 (MCC 0,0836323479), cùng checksum và bằng chứng E19-E22. Ghi rõ Colab 0,09/0,67 là lịch sử exploratory/superseded. |
| Trang 5-6, mục 4 | Cập nhật theo thuật toán B3 đã implement để chọn cặp cùng hàm trước/sau vá; khai báo rõ chưa xác thực được pair pool thật, nên chưa sinh prompt thật hoặc chạy inference. Phân biệt phiên bản cũ và mới. |
| Trang 6-7, mục 5 | Giữ quy tắc scoring/validity trên nền tảng Kaggle đã đăng ký. |
| Trang 9, mục 7.2 | Giữ Kaggle 2×T4 theo preregistration; không xin thêm Colab. Khai báo Colab B1-H2 đã chạy là deviation exploratory. |
| Trang 9-10, mục 8 | Các ô tick không chứng minh mọi công việc đã hoàn tất; cập nhật từng trạng thái bằng artifact thực có. |

Không sửa giả thuyết, biên hiệu ứng thực tiễn, cỡ mẫu, seed, định nghĩa metric, số bootstrap, cluster unit, họ Holm, nguồn graph, thứ tự prompt hoặc ngân sách token ngoài các thay đổi B3 được nêu rõ dưới đây.

## A. Justification - văn bản tiếng Anh để dán vào OSF

We request a transparent amendment to the existing GRACE registration to (1) correct B0/B1 decision thresholds that were carried into the submitted threshold table as fixed values rather than recomputed from the complete validation splits; (2) document the validation-only threshold-selection procedure for the already registered B1-H2 arm, whose numeric thresholds were absent from the original 14-value lock; and (3) replace the B3 demonstration-pair construction and difference-generation procedure with a verified same-function, vulnerable/patched design. The registered Kaggle environment with two Tesla T4 GPUs remains the execution environment for all arms; this update does not request Colab as an alternative platform.

This is an amendment to an ongoing study. B0/B1/B2/B2-flip inference outputs and metrics, and a post-hoc reanalysis including validation-selected thresholds and paired bootstrap contrasts, existed before this amendment. B1-H2 validation and test inference were also performed on Colab L4 as platform-deviant exploratory runs. The resulting Colab thresholds (Devign 0.09; ReVeal 0.67) and Colab test inference are disclosed as exploratory and superseded. The complete B1-H2 Kaggle validation census is now finished: Devign selected tau=0.09 (MCC 0.066793, n=2,732); ReVeal selected tau=0.21 (MCC 0.083632, n=2,273). The Devign value coincides numerically with the old Colab value but was independently selected from Kaggle validation records; the ReVeal value differs. No test records, labels or metrics were read for this Kaggle threshold selection. These activities and deviations are disclosed retrospectively; this update does not establish that they were preregistered before execution or analysis. The original registration and its PDF/ZIP attachments remain preserved. The revised methods below apply from the actual amendment date to the work to which they relate. Hypotheses, sample sizes, data partitions, model weights, quantization, tokenizer, scoring, decoding, seeds, statistical decision rules and the registered Kaggle execution environment remain as registered except for the specific threshold and B3 method changes stated below.

Reproducible validation-only threshold evidence is archived at commit d9127fc7b12a128d8499012454ad134733f810ff. The original optimizer is byte-identical to the 1 November implementation. The verifier reproduces all four corrected thresholds using complete validation only; source/input hashes and file-read audits are provided: https://github.com/kazunguyen/GRACE-summary/blob/d9127fc7b12a128d8499012454ad134733f810ff/Runs-management/osf_amendment_20261106/README.md

The complete Kaggle validation census contained 2,732 Devign and 2,273 ReVeal records (5,005 total). We verified unique IDs, score validity, exact joins to the frozen validation labels, and prompt hashes, then independently reproduced the registered 99-point MCC grid and tie-break rule from the downloaded Kaggle records. The resulting validation-only locks are Devign tau=0.09 (MCC 0.0667928192) and ReVeal tau=0.21 (MCC 0.0836323479). The Devign number happens to equal the preliminary Colab number, but the Kaggle result was recomputed from Kaggle outputs; ReVeal differs from the superseded Colab value 0.67. Test records, labels and metrics were not read for this threshold selection. The exact Kaggle lock, input/output hashes, independent audit and runtime provenance are listed under E19-E22. The earlier Colab lock at commit 846279676b60ca1185210642e75699b914e36a4d remains preserved as historical evidence, not as the current threshold source. No new confirmatory Kaggle test inference is represented as completed by this threshold lock.

## B. Nội dung phương pháp cập nhật để dán vào các câu trả lời phù hợp

### B1. Threshold correction and analysis status

This section supersedes the four B0/B1 values in Section 3.2 of the submitted PDF. Threshold selection uses all valid records from the official validation split: 2,732 Devign and 2,273 ReVeal samples. The registered search grid remains 0.01 through 0.99 in increments of 0.01, maximizing validation MCC. Thresholds with undefined MCC are excluded; ties select the threshold closest to 0.5, then the smaller threshold. No test-based threshold optimization is authorized.

| Dataset | Arm | Submitted threshold | Corrected full-validation threshold | Validation MCC at corrected threshold |
|---|---|---:|---:|---:|
| Devign | B0 | 0.08 | 0.98 | 0.076010 |
| ReVeal | B0 | 0.44 | 0.30 | 0.080120 |
| Devign | B1 | 0.88 | 0.98 | 0.074755 |
| ReVeal | B1 | 0.74 | 0.63 | 0.083264 |

The B2 thresholds remain 0.70 for Devign and 0.12 for ReVeal. B2-flip and B2-rep continue to inherit their corresponding B2 thresholds. Other previously registered threshold values are not changed by this amendment. Existing B0/B1 test scores are retained and may be rescored offline; no new model inference is needed solely to apply a different decision threshold. Threshold-independent metrics do not change solely because the threshold changes. Results under both submitted and corrected thresholds will be identified explicitly.

The B0 values 0.98 and 0.30 are present in the historical validation threshold artifact at commit 282033d3ed30b9f91392fec063bd2b2ce10266f4 on 2026-11-01, and remain present at commit 31a37a3d3e11af249a620f1cf68dcd1724c6a592. This establishes historical presence of those values in the repository, but is not proof of absence of prior test exposure. The full-validation reanalysis on 2026-11-06 also produced the B1 corrected thresholds. Test metrics and selected bootstrap contrasts from that reanalysis had already been inspected before this amendment. Corrected-threshold analyses of those previously examined test outputs will be reported as retrospective/post-hoc reanalyses, alongside the original registered-threshold results. They will not be relabelled as prospectively confirmed merely by submitting this update.

The corrected thresholds were additionally reproduced by executing the original `Runs-management/validation_lock.py` implementation, byte-identical to the version at commit 282033d (SHA-256 `9d83acbe5a1767d0e91c6e5950ab73e92c6b4d05980422486a1876564e4db711`), using exclusively the four complete validation record files. An enforced file-read allowlist restricted that verification run to those validation files and the two source files. It reproduced all four corrected thresholds without reading test records, test metrics or submitted threshold values. The verification evidence records input/source hashes, all 99 MCC grid points and actual file-read paths. See the separate computational-provenance note and `validation_threshold_verification.json`; historical test exposure remains disclosed separately.

Evidence: `scripts/lock_full_validation_thresholds.py`, the unchanged submitted threshold table, `Runs-management/analysis_lock_20261101/thresholds.initial.json`, and the input identities/hashes in `Runs-management/reanalysis_20261106/results.json`. No unsupported claim is made that a specific merge conflict caused the discrepancy, that the optimum must be unique, or that a difference between validation and test optima proves absence of test-informed decisions.

### B1a. B1-H2 threshold selection and current status

B1-H2 is already listed in Section 4 of the submitted PDF (page 6) and in the research proposal's experimental matrix. However, neither Section 3.2 of that PDF (page 4) nor the original attached threshold files contains numeric B1-H2 thresholds. This update supplements the threshold record for the existing arm; the experimental matrix is not expanded by this addition. The blanket checklist statement that every arm's threshold was already locked is corrected accordingly.

The registered per-arm validation-MCC rule applies independently to B1-H2; it does not inherit B1's threshold. A prior Colab run covered all 5,005 validation IDs and produced preliminary values 0.09/0.67, but this platform-deviant lock is superseded and excluded from confirmatory use. The Colab test inference that used those values is also exploratory; no label-based test metrics are treated as confirmatory evidence.

The complete Kaggle validation census contained 2,732 Devign and 2,273 ReVeal records (5,005 total). We verified unique IDs, score validity, exact joins to the frozen validation labels, and prompt hashes, then independently reproduced the registered 99-point MCC grid and tie-break rule from the downloaded Kaggle records. The resulting validation-only locks are Devign tau=0.09 (MCC 0.0667928192) and ReVeal tau=0.21 (MCC 0.0836323479). The Devign number happens to equal the preliminary Colab number, but the Kaggle result was recomputed from Kaggle outputs; ReVeal differs from the superseded Colab value 0.67. Test records, labels and metrics were not read for this threshold selection. The exact Kaggle lock, input/output hashes, independent audit and runtime provenance are listed under E19-E22. The earlier Colab lock at commit 846279676b60ca1185210642e75699b914e36a4d remains preserved as historical evidence, not as the current threshold source. No new confirmatory Kaggle test inference is represented as completed by this threshold lock.


### B2. Replacement of the B3 method

This section supersedes the B3-family construction in Section 4 of the submitted PDF. It is a substantive post-registration change to demonstration selection and difference generation. The B3 hypotheses and outcome definitions remain unchanged, but results using the replacement prompts will be identified as obtained under the amended method rather than the original prompt specification. Any outputs from the original B3 implementation will be kept under a separate version identity and will not be mixed with amended B3 outputs.

The original implementation uses a retrieved example and an opposite-label donor selected by token overlap with the target, with heuristic difference descriptions. It does not require the examples to be a verified vulnerable/patched pair. Fallback descriptions and unrelated examples are implementation limitations; they do not by themselves establish a measured B3 AUROC or prove that the research hypothesis is false.

The proposed replacement specification is:

1. An eligible pair contains the vulnerable and patched versions of the same source function across an identified security-fix commit. Record repository, path, function identity, fixing commit and parent revision, both donor IDs, both code hashes, labels and supporting patch evidence. A shared commit alone is insufficient. A patch must have a verified security rationale; it is not assumed that every function after any edit is non-vulnerable.
2. Both examples must remain eligible members of the corresponding frozen clean training donor bank. Targets and validation/test functions must never enter the donor pool. No new external donor dataset is authorized by this amendment. If no adequate verified pair pool can be constructed under this restriction, B3 pauses; broadening the donor data requires a separately disclosed decision before inference.
3. Validate each pair against its source diff and security rationale before use. Record two reviewer judgments and resolve disagreement before admitting a pair. Archive the eligible-pair manifest and the deterministic selection code before B3 validation inference.
4. Implemented deterministic target-to-pair selection: the code uses the existing code-token normalization and ranks eligible pairs by the mean token-set Jaccard similarity between the target and each function. It selects the highest-scoring pair; exact ties use lexicographic stable pair ID. The target label and validation/test performance do not select donors or alter this rule. The B2 retrieved example is no longer required to be an anchor; this is part of the declared B3 method replacement.
5. Generate Key difference from verified changes visible in the two displayed snippets and supported by the fix diff. Store the relevant changed lines and evidence. Commit messages may provide context but are not sufficient by themselves. Do not infer a security property from a generic keyword match. If truncation removes the evidence necessary to support the explanation, do not silently substitute a generic security claim; correct the pair/snippet construction and complete the registered input audit before inference.
6. Retain the registered section order, tokenizer, token budget, graph input, output schema and scoring. Freeze and hash all amended B3-family prompts before the corresponding inference. Verify that the selected pairs and their supporting changed lines fit the existing demonstration budget without removing the causal distinction.
7. B3-nodiff uses exactly the same examples and omits only Key difference; B3-swap changes only example order; B3-flip changes only both demonstration labels, under the existing probe convention. Apart from each stated intervention, prompt contents remain matched to the amended B3 base.
8. Select the amended B3 threshold on complete validation only. B3-swap and B3-flip inherit that threshold. B3-nodiff retains its registered independent validation-threshold policy: the frozen arms configuration does not specify inheritance for this arm. Complete required prompt audits before inference; lock validation thresholds before the corresponding new test inference.

The amended B3 selector algorithm is implemented according to the proposed method (E26). Its software tests passed and synthetic B3-family prompts were rendered with the pinned tokenizer; synthetic revision IDs and programmatic reviewer fixtures are test fixtures only, not real source evidence or approvals (E27, E30). The remaining blocker is empirical: the CPU feasibility check searched the frozen clean training banks and attempted six real validation targets, but all six paused because no two-person-reviewed verified pair pool was supplied. A manual source-screening note checked three short Devign name-match candidates; none established the required before/after source-function relationship or was admitted (E29). The broader discovery pass found no opposite-label candidates sharing both the recorded commit and extracted function hint; this heuristic result does not establish that no valid security-fix pairs exist. ReVeal's current frozen raw export lacks commit IDs for all 17,636 eligible donors, so source-revision pairing cannot be authenticated from that export alone. No real B3 pair has been approved, no amended real prompt set frozen, and no B3 inference or threshold fitting has occurred. The algorithm implementation is complete; B3 execution remains paused until authentic source revisions/security fixes are verified and reviewed by two people within the frozen clean training donor bank. Expanding the donor bank requires a separate disclosed decision. The original frozen specs and donor banks remain preserved.

### B3. Registered execution platform and runtime

The registered Kaggle environment with two NVIDIA Tesla T4 GPUs remains the required execution platform for all arms, including B1-H2. This amendment does not add Colab or an L4 as an authorized alternative. The prior Colab L4 B1-H2 validation and test runs are retained in the exposure record as platform-deviant exploratory work; their threshold values and test outputs are excluded from the confirmatory Kaggle analysis. All subsequent B1-H2 validation and test work will use Kaggle. A threshold must be selected from the complete Kaggle validation split and locked before any new B1-H2 Kaggle test inference.

All other registered experimental settings remain unchanged:

- Model: Qwen/Qwen3-Coder-30B-A3B-Instruct; GGUF Q4_K_M; SHA-256 `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`.
- Tokenizer revision: `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`.
- Inference backend: `llama-cpp-python==0.3.16`, direct Llama invocation; retain the registered inference dependency versions and build settings.
- `n_ctx=8192`, `n_batch=256`, `n_gpu_layers=-1`, `logits_all=True`; greedy decoding, temperature 0, and the registered seeds.
- First-token logprobs for both binary labels and the same normalized score; separate score validity from raw greedy-response validity.
- Frozen data partitions, sample census, graph inputs, non-B3 prompts, prompt section order, token budgets, cache isolation, threshold-selection rules and statistical analysis rules, except the explicit B0/B1 values and B3 method replacement described above.

Log the actual Kaggle runtime version, GPU model/count/VRAM, OS, Python, CUDA toolkit, driver, package versions, backend build flags, model/tokenizer/prompt hashes, code commit, model-load/offload evidence and GPU utilization for each run.

For B2-rep, retain the registered within-Kaggle comparison with its Kaggle reference run; do not substitute Colab results into that comparison.

### B4. Retrospective disclosure of work already completed

At preparation of this draft on 2026-11-06:

- B0, B1, B2 and B2-flip have full validation/test inference outputs on both datasets. Historical raw scores and provenance remain preserved.
- B2-rand has 7,789 of 15,015 planned three-seed validation records in the imported I-11 checkpoint; its test outputs have not been produced in that checkpoint. B2-rep remains unexecuted in the local run ledger.
- B1-H2 Colab L4 exploratory work: I-12/I-13 produced all 5,005 original validation predictions; the exploratory Colab-derived 0.09/0.67 lock was recorded. I-14 subsequently produced all 5,006 original test predictions using those values. Native logs for I-14 verify 49/49 model layers offloaded to the L4 GPU; this does not validate the earlier I-12/I-13 offload. Those runs remain platform-deviant exploratory work; their threshold lock is superseded and their test outputs are excluded from confirmatory analysis. The I-14 output audit and prediction archive are available at E23-E24; the output records contain no label fields, and the separate progress check computed no label-based test metrics. A completed Kaggle 2xT4 validation run covered all 5,005 records and independently selected Devign 0.09 (MCC 0.066793) and ReVeal 0.21 (MCC 0.083632). The Devign value coincides numerically with Colab but was independently recomputed; ReVeal differs. No test records, labels or metrics were read for the Kaggle threshold selection. Any new confirmatory B1-H2 test inference must use Kaggle and the locked Kaggle thresholds.
- The 2026-11-06 reanalysis recalculated validation thresholds, test metrics, sensitivity results and selected paired-bootstrap contrasts. These results were inspected before this update; the original blanket statement that all bootstrap analyses remained unperformed is superseded for this work. This reanalysis is not equivalent to a completed confirmatory Holm analysis of all 11 registered contrasts.
- No verified amended B3 inference output is established by this draft. Update this statement if additional runs or outputs are known at the actual submission time.

The submitted PDF's page footers saying "Not yet submitted" reflect preparation status of that historical attachment. They do not describe the current public registration. Its Appendix C checkmarks must not be interpreted as evidence that all future inference, model fitting, final tables and audits were already completed; actual completion is determined item by item from dated artifacts.

## 3. Những điểm cần khóa trước inference B3 mới

- Chốt đặc tả B2 ở trên, đặc biệt nguồn donor, tiêu chí xác minh nhãn/pair, hàm xếp hạng và giới hạn snippet; không ghi thuật toán đã hoàn thành khi mới là đề xuất.
- Xây dựng và nghiệm thu manifest cặp thật, đối chiếu nguồn và khả năng hiển thị diff dưới ngân sách đã đăng ký. Nếu không làm được trong bank cũ thì dừng để quyết định có thay nguồn donor hay không; không dùng ngầm cặp không liên quan làm fallback.
- Sinh bộ prompt B3 mới trong thư mục phiên bản mới, kiểm tra quan hệ giữa base/probe, ghi mã băm. Không thay bytes của specs/OSF artifact gốc.
- Sau nộp/công khai amendment, ghi rõ các hoạt động đã xảy ra trước đó và bắt đầu inference mới theo thời điểm thực tế. Một amendment không tự động biến các kết quả đã xem thành xác nhận tiến cứu.

## 4. Nguồn đối chiếu và phạm vi

- PDF gốc và SHA-256 ở đầu tài liệu.
- `Runs-management/reanalysis_20261106/REPORT.md` và `results.json`: bốn ngưỡng sửa, nguồn record và phân tích hậu nghiệm đã có.
- `Runs-management/RUNS.md`: I-10, I-11, I-12, I-13; số liệu là snapshot local, cần cập nhật nếu thêm kết quả trước lúc Submit.
- `configs/arms.yaml`: B3-nodiff không có threshold_from; B3-swap/B3-flip có threshold_from B3.
- `Runs-management/b1h2_threshold_lock_20261106.json` và `Runs-management/lock_b1h2_validation_thresholds.py` tại commit `846279676b60ca1185210642e75699b914e36a4d` là bằng chứng lịch sử cho lock Colab đã bị supersede, không phải nguồn tau Kaggle hiện tại. Bằng chứng khóa Kaggle mới và kiểm tra độc lập nằm ở E19-E22.
- [OSF - quy trình cập nhật](https://help.osf.io/article/330-welcome-to-registrations): quyền Admin, Justification, câu trả lời sửa, hạn chế tệp và phê duyệt.

Không dùng riêng commit timestamp làm bằng chứng mật mã độc lập về thời gian; không khẳng định sự cố merge cụ thể nếu chưa có đối chiếu lịch sử chứng minh. Không mô tả bộ pair B3 mới là sẵn sàng chỉ dựa trên bản dự thảo này.
