# OSF amendment preparation and validation-only evidence

Prepared 6 November 2026. OSF status: not submitted by this preparation.

`OSF_UPDATE_EN.md` contains the English submission text; `OSF_JUSTIFICATION_EN.txt` contains the justification to paste into OSF; `HUONG_DAN_NOP_OSF.md` gives the submission steps in Vietnamese. `DRAFT_VA_HUONG_DAN_NOP_OSF.md` is the detailed working draft. The update concerns B0/B1 threshold correction, B1-H2 validation-only thresholds (Devign tau=0.09, MCC=0.0667928192, n=2,732; ReVeal tau=0.21, MCC=0.0836323479, n=2,273), and replacement of the B3 pairing method. The 5,005 Kaggle validation records were independently checked against frozen labels and prompts; threshold selection did not read test data. The registered Kaggle 2xT4 environment remains required; this update does not request Colab. Colab B1-H2 validation/test and its 0.09/0.67 lock are disclosed as historical exploratory work and superseded. The frozen OSF PDF/ZIP and historical Colab evidence are preserved.

The lock at commit 846279676b60ca1185210642e75699b914e36a4d and checksum eedb783ebba986cec772bde2bdcca1cb95a2cd9db4bebd8141a44f49342178e5 are retained as historical Colab evidence only. The Kaggle lock payload SHA-256 is b5dc7e0da070f75cfabc10c366a08675d1c3f471f1e11fb86ee826a22ce674f8; the active 16-threshold config seal is cecd6c604481da846e37d1899324f1177566bdf0a422d0a632467b2c235a6a47. The new thresholds are Devign 0.09 and ReVeal 0.21.

## Evidence files

- `verify_validation_thresholds.py`: verifier added on 6 November, which calls the existing optimizer without modifying its algorithm.
- `validation_threshold_verification.json`: verification against original local validation files, including all 99 MCC grid points per arm/dataset.
- `validation_records.zip`: four byte-preserved validation JSONL files, with original repository-relative paths. No test records or prompts are included.
- `validation_input_inventory.json`: SHA-256, record counts and byte sizes for the archive and its four members.
- `isolated_validation_verification.json` and `isolated_verification_stdout.txt`: successful run in a temporary repository-shaped directory containing only the verifier, original optimizer and four validation files. Temporary absolute paths in this captured output identify that completed run and do not need to exist for reproduction.
- `BANG_CHUNG_NGUONG_VALIDATION.md`: evidence explanation in Vietnamese and proposed English wording.

The archive SHA-256 is `4737fc0ac8685dc0c70cdc5493e10dbc468ad5097753d19a4532a0237af17596`.

## Reproduce from a checkout of the evidence commit

Only Python's standard library is required. From the repository root:

```powershell
python -m zipfile -e Runs-management/osf_amendment_20261106/validation_records.zip .
python -B Runs-management/osf_amendment_20261106/verify_validation_thresholds.py
```

Extract in a fresh checkout. The archive restores the original, otherwise ignored validation files at their original paths. Each archive member is listed in the inventory; all four are validation records. The verifier writes its new report in this evidence folder. Timing and absolute-path fields will differ by machine; source/input hashes, grid results and thresholds should match.

Expected computed thresholds: B0 Devign 0.98, B0 ReVeal 0.30, B1 Devign 0.98, B1 ReVeal 0.63. The expected values are compared only after all fits and are not passed into the optimizer.

The optimizer is `Runs-management/validation_lock.py`, function `pick_threshold`. Its SHA-256 is `9d83acbe5a1767d0e91c6e5950ab73e92c6b4d05980422486a1876564e4db711`, identical to its bytes at historical commit `282033d3ed30b9f91392fec063bd2b2ce10266f4`.

The verifier enforces an exact file-read allowlist through Python's `open` audit events after standard-library imports. During the successful run, only four validation files and two Python source files were opened for reading. This is evidence about the computation, not a claim that researchers had never previously seen test results. The separate full reanalysis script reads test for metrics/bootstrap and must not be described as entirely test-free.
