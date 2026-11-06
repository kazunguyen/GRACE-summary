# OSF amendment preparation and validation-only evidence

Prepared 6 November 2026. OSF status: not submitted by this preparation.

`OSF_UPDATE_EN.md` contains the English submission text once prepared; `DRAFT_VA_HUONG_DAN_NOP_OSF.md` contains the Vietnamese workflow and detailed working draft. The update concerns B0/B1 threshold correction, replacement of the B3 pairing method, and the addition of Colab L4/compatible runtime. The frozen OSF PDF/ZIP and active protocol/threshold/arm configurations are not changed by these artifacts.

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
