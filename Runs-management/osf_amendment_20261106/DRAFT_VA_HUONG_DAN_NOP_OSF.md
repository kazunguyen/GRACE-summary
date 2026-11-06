# Dự thảo cập nhật đăng ký OSF và hướng dẫn nộp

Ngày soạn: 06/11/2026 (Asia/Bangkok). Trạng thái: DRAFT, chưa nộp OSF.

Đăng ký gốc: https://osf.io/fqgh2/overview

Tài liệu gốc: `Runs-management/osf_registration_draft_20261102/output/pdf/GRACE_OSF_PREREGISTRATION_20261102.pdf`.
SHA-256 PDF gốc: `22648ead896baf5c1032de700c12fb97bd6dc44f0a8049292532ae6c0468b14c`.

Đây là tài liệu mới, không thay PDF/ZIP gốc. Nội dung dưới đây là đề xuất phương pháp để nhóm rà soát và nộp; không xác nhận B3 mới đã được triển khai hoặc nghiệm thu. Phương án B3 do người dùng chọn: thay B3 trong ma trận bằng cặp cùng hàm trước/sau vá, cùng các probe tương ứng.

## 1. Quy trình trên OSF

1. Đăng nhập bằng tài khoản có quyền Admin của đăng ký. Mở đăng ký gốc, chọn `Updates` rồi `Update`. Cũng có thể vào `My Registrations` > `Submitted` > `Update`.
2. Dán phần A bên dưới vào ô `Justification`.
3. Sửa các câu trả lời liên quan trong form bằng phần B. Nếu form ban đầu chỉ chứa một mục mô tả và PDF đính kèm, bổ sung nội dung thay thế vào mục văn bản cập nhật được, ghi rõ các mục/trang của PDF được đính chính. Chỉ ghi lý do trong Justification chưa đủ: OSF yêu cầu thay ít nhất một trường câu trả lời.
4. OSF không cho thêm/xóa/thay tệp trong Update. Nếu cần chia sẻ bản đính chính dưới dạng tệp, lưu riêng trên OSF Project liên kết hoặc kho Git công khai; dẫn URL tới phiên bản/commit cố định và SHA-256 trong câu trả lời cập nhật. File trên Project là tài liệu hỗ trợ; phần phương pháp cốt lõi vẫn phải nằm trong nội dung update. Chỉ thêm URL công khai đã tồn tại, không dán đường dẫn máy tính hoặc URL dự kiến.
5. Chọn Review, đọc lại nội dung thay đổi rồi Submit. Các Admin nhận email phê duyệt; OSF mô tả thời gian tự phê duyệt 48 giờ nếu không có phản đối, với ngoại lệ registry có kiểm duyệt. Ghi trạng thái thực tế, không ghi đã duyệt khi còn `Update in progress`.
6. Sau khi update được công khai, lưu URL/version/thời điểm hiển thị và bản sao nội dung update vào thư mục mới. Ghi nhận trong `CHANGES_AFTER_PREREG.md`. Tạo commit/tag mới nếu cần, sau khi kiểm tra tên chưa dùng; không sửa tag hoặc nhánh niêm phong cũ. Không sửa khóa ngưỡng hiện hành trong bước soạn/nộp tài liệu này.

Nguồn quy trình: [OSF Support - Update a Registration](https://help.osf.io/article/330-welcome-to-registrations#Update-a-Registration). Tên câu hỏi cụ thể tùy template đã dùng; đây không phải xác nhận trực tiếp form trong tài khoản của nhóm.

## 2. Đối chiếu nội dung cần cập nhật

| Vị trí trong PDF gốc | Nội dung cần đính chính hoặc bổ sung |
|---|---|
| Trang 1-2, mục 1 và exposure ledger | Khai báo thời điểm thực tế đã chạy/xem dữ liệu, bao gồm phân tích lại ngày 06/11 và Colab L4 đã thực hiện; không khẳng định toàn bộ quyết định hoặc khóa ngưỡng có trước mọi test run. |
| Trang 4, mục 3.2 | Sửa bốn ngưỡng B0/B1 theo toàn bộ validation; giữ quy tắc tối ưu và ngưỡng kế thừa cho probe. |
| Trang 5-6, mục 4 | Thay định nghĩa B3 và họ B3 bằng phương pháp cặp trước/sau vá mới; phân biệt phiên bản cũ và mới. |
| Trang 6-7, mục 5 | Giữ quy tắc scoring/validity; áp dụng cùng quy tắc cho Kaggle và Colab. |
| Trang 9, mục 7.2 | Bổ sung Colab, một NVIDIA L4 và quy tắc chọn runtime khả dụng gần môi trường tham chiếu nhất. |
| Trang 9-10, mục 8 | Các ô tick không chứng minh mọi công việc đã hoàn tất; cập nhật từng trạng thái bằng artifact thực có. |

Không sửa giả thuyết, biên hiệu ứng thực tiễn, cỡ mẫu, seed, định nghĩa metric, số bootstrap, cluster unit, họ Holm, nguồn graph, thứ tự prompt hoặc ngân sách token ngoài các thay đổi B3 được nêu rõ dưới đây.

## A. Justification - văn bản tiếng Anh để dán vào OSF

We request a transparent amendment to the existing GRACE registration for three reasons: (1) correction of B0/B1 decision thresholds that were carried into the submitted threshold table as fixed values rather than recomputed from the complete validation splits; (2) replacement of the B3 demonstration-pair construction and difference-generation procedure with a verified same-function, vulnerable/patched design; and (3) addition of Google Colab with a single NVIDIA L4 and a documented compatible runtime as an alternative to Kaggle with two Tesla T4 GPUs, due to the compute configurations and runtime images available to our team.

This is an amendment to an ongoing study. B0/B1/B2/B2-flip inference outputs and metrics, and a post-hoc reanalysis including validation-selected thresholds and paired bootstrap contrasts, existed before this amendment. B1-H2 validation inference has also already been performed on Colab L4. These activities are disclosed retrospectively; this update does not establish that they were preregistered before execution or analysis. The original registration and its PDF/ZIP attachments remain preserved. The revised methods below apply from the actual amendment date to the work to which they relate. Hypotheses, sample sizes, data partitions, model weights, quantization, tokenizer, scoring, decoding, seeds and statistical decision rules remain as registered except for the specific threshold, B3 and execution-environment changes stated below.

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

### B2. Replacement of the B3 method

This section supersedes the B3-family construction in Section 4 of the submitted PDF. It is a substantive post-registration change to demonstration selection and difference generation. The B3 hypotheses and outcome definitions remain unchanged, but results using the replacement prompts will be identified as obtained under the amended method rather than the original prompt specification. Any outputs from the original B3 implementation will be kept under a separate version identity and will not be mixed with amended B3 outputs.

The original implementation uses a retrieved example and an opposite-label donor selected by token overlap with the target, with heuristic difference descriptions. It does not require the examples to be a verified vulnerable/patched pair. Fallback descriptions and unrelated examples are implementation limitations; they do not by themselves establish a measured B3 AUROC or prove that the research hypothesis is false.

The proposed replacement specification is:

1. An eligible pair contains the vulnerable and patched versions of the same source function across an identified security-fix commit. Record repository, path, function identity, fixing commit and parent revision, both donor IDs, both code hashes, labels and supporting patch evidence. A shared commit alone is insufficient. A patch must have a verified security rationale; it is not assumed that every function after any edit is non-vulnerable.
2. Both examples must remain eligible members of the corresponding frozen clean training donor bank. Targets and validation/test functions must never enter the donor pool. No new external donor dataset is authorized by this amendment. If no adequate verified pair pool can be constructed under this restriction, B3 pauses; broadening the donor data requires a separately disclosed decision before inference.
3. Validate each pair against its source diff and security rationale before use. Record two reviewer judgments and resolve disagreement before admitting a pair. Archive the eligible-pair manifest and the deterministic selection code before B3 validation inference.
4. Proposed deterministic target-to-pair selection: use the existing code-token normalization and rank eligible pairs by the mean of token-set Jaccard similarity between the target and each of the two functions. Select the highest-scoring pair; exact ties use lexicographic stable pair ID. Do not use the target label or any validation/test performance to choose donors or adjust this rule. The B2 retrieved example is no longer required to be an anchor; this is part of the declared B3 method replacement.
5. Generate Key difference from verified changes visible in the two displayed snippets and supported by the fix diff. Store the relevant changed lines and evidence. Commit messages may provide context but are not sufficient by themselves. Do not infer a security property from a generic keyword match. If truncation removes the evidence necessary to support the explanation, do not silently substitute a generic security claim; correct the pair/snippet construction and complete the registered input audit before inference.
6. Retain the registered section order, tokenizer, token budget, graph input, output schema and scoring. Freeze and hash all amended B3-family prompts before the corresponding inference. Verify that the selected pairs and their supporting changed lines fit the existing demonstration budget without removing the causal distinction.
7. B3-nodiff uses exactly the same examples and omits only Key difference; B3-swap changes only example order; B3-flip changes only both demonstration labels, under the existing probe convention. Apart from each stated intervention, prompt contents remain matched to the amended B3 base.
8. Select the amended B3 threshold on complete validation only. B3-swap and B3-flip inherit that threshold. B3-nodiff retains its registered independent validation-threshold policy: the frozen arms configuration does not specify inheritance for this arm. Complete required prompt audits before inference; lock validation thresholds before the corresponding new test inference.

The pair manifest, labels/source evidence, source code and rendered-prompt hashes must be archived as new versioned artifacts. This draft does not assert that these artifacts already exist, that the pair pool has sufficient coverage, or that a content audit has already passed. The original frozen specs and donor banks remain preserved; amended prompts are separate outputs.

### B3. Additional compute platform, GPU and runtime

This section supplements Section 7.2 of the submitted PDF. Kaggle with two NVIDIA Tesla T4 GPUs remains permitted. Google Colab with one NVIDIA L4 is additionally permitted because the dual-T4 configuration and exact Kaggle runtime image are not available through the Colab environments accessible to our team. This is a limitation of the team's available execution environments, not a claim that Google guarantees or universally prohibits a particular GPU allocation.

When the exact Kaggle runtime cannot be reproduced, use the available Colab runtime that most closely supports the reference environment, chosen before examining model outputs. First prefer a compatible Python major/minor version and the exact registered inference-package versions; among equally compatible offered runtime versions, select the most recent. If no offered image matches all base-environment components, explicitly record the unavoidable Python, operating-system, CUDA, driver and runtime-image differences. Do not choose a runtime based on favourable validation or test results. Pin the selected image/version where the service permits and keep it for the run; record any forced service-side migration as a new execution identity.

All experimental settings other than the explicitly amended methods and platform/GPU/base-runtime components remain unchanged:

- Model: Qwen/Qwen3-Coder-30B-A3B-Instruct; GGUF Q4_K_M; SHA-256 `f6050b4da22869aa3fb9d94bb3314e9fc5a027d4741c1f97761c387d6b2b2335`.
- Tokenizer revision: `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`.
- Inference backend: `llama-cpp-python==0.3.16`, direct Llama invocation; preserve the reference inference dependency versions and build settings as far as the explicitly disclosed base-runtime differences permit. Do not silently upgrade the inference library to make a runtime work.
- `n_ctx=8192`, `n_batch=256`, `n_gpu_layers=-1`, `logits_all=True`; greedy decoding, temperature 0, and the registered seeds.
- First-token logprobs for both binary labels and the same normalized score; separate score validity from raw greedy-response validity.
- Frozen data partitions, sample census, graph inputs, non-B3 prompts, prompt section order, token budgets, cache isolation, threshold-selection rules and statistical analysis rules, except the explicit B0/B1 values and B3 method replacement described above.

Log the actual platform, GPU model/count/VRAM, OS, Python, CUDA toolkit, driver, runtime image, package versions, backend build flags, model/tokenizer hashes, prompt hashes and code commit per run. Record model-load/offload evidence and actual GPU utilization: requesting `n_gpu_layers=-1` alone does not establish full GPU offload. Keep execution identities distinct across environments and do not reuse cached responses across them. Cross-hardware greedy inference is not assumed to yield bitwise-identical logits or predictions. Report platform-specific provenance and any observed discrepancies without selecting the more favourable environment's results.

For B2-rep, the intended within-environment repeat comparison requires the same environment as its reference B2 run. A Colab-L4 repeat compared only with a Kaggle-T4 reference is a cross-environment comparison and cannot isolate natural repeat variability. If Colab is used for the main repeat comparison, generate and identify the corresponding B2 reference under that same environment; otherwise retain the within-Kaggle route or label the cross-environment result separately. This requirement preserves the interpretation of the original repetition probe.

### B4. Retrospective disclosure of work already completed

At preparation of this draft on 2026-11-06:

- B0, B1, B2 and B2-flip have full validation/test inference outputs on both datasets. Historical raw scores and provenance remain preserved.
- B2-rand has 7,789 of 15,015 planned three-seed validation records in the imported I-11 checkpoint; its test outputs have not been produced in that checkpoint. B2-rep remains unexecuted in the local run ledger.
- B1-H2 original validation prompts were executed on Colab L4 on 2026-11-06: I-12 has 100 rows and I-13 has 4,905, together covering 5,005 unique validation IDs. These are the original prompt variant, not the later v5/v6 candidates. Observed runtime was Colab 2026.10, Python 3.13.16, CUDA toolkit 13.0.88 and driver 580.82.07; the audited Kaggle runtime recorded Python 3.13.15. Full GPU-layer placement was not verified in the retained L4 logs. This update records those runs retrospectively and does not erase their earlier exploratory/deviation designation.
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
- [OSF - quy trình cập nhật](https://help.osf.io/article/330-welcome-to-registrations): quyền Admin, Justification, câu trả lời sửa, hạn chế tệp và phê duyệt.
- [Colab - tài nguyên/GPU khả dụng](https://research.google.com/colaboratory/faq.html): GPU và tài nguyên thay đổi theo khả dụng.
- [Colab - runtime versions](https://research.google.com/colaboratory/runtime-version-faq.html): chọn runtime và cài phiên bản thư viện cụ thể.

Không dùng riêng commit timestamp làm bằng chứng mật mã độc lập về thời gian; không khẳng định sự cố merge cụ thể nếu chưa có đối chiếu lịch sử chứng minh. Không mô tả bộ pair B3 mới là sẵn sàng chỉ dựa trên bản dự thảo này.
