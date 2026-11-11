# PA1 11/11 — reproducibility inputs and rerun

Date: 2026-11-11

## B0/B1 test records

Published the four test `records.jsonl` files referenced by `Runs-management/current_status.json`. Their SHA-256 values are:

- B0 Devign: `e5eed103294d0ce4f74a5d2f719f128104a79e5f6f3a92bd00da23a947c7fdb6`
- B0 ReVeal: `d64fe85a7f8124ec189d1d110c9c22a3926fcc2391d76f0a5d7e9218f231c3a8`
- B1 Devign: `15673b8f6788b1d6b55e66438cba292435178303d820b8c3d249cd850254ace4`
- B1 ReVeal: `26057b7af6fe20dd40a829598555709b963f7615c6a04d8f228f63e6bea2c166`

The files were present locally under ignored `output/` paths and their digests matched the analysis provenance. The 11/11 analysis also consumes other test records and Step 6 score/join/feature artifacts. The current provenance lists 53 inputs; 23 existing inputs (37,341,181 bytes) were not tracked before this change. Those listed artifacts are included so a clean checkout has the analysis inputs, rather than only the four B0/B1 files.

## Independent recomputation

Command:

```powershell
python Runs-management/analysis_pa1_20261111/recompute.py --out Runs-management/analysis_pa1_20261111/full_tables
```

The script completed for both datasets: Devign (2,732 IDs; 2,068 full-test clusters) and ReVeal (2,274 IDs; 646 full-test clusters), producing 66 contrasts per dataset. `contrasts.csv`, `sensitivity.csv`, and `provenance.json` matched the generated files byte-for-byte. SHA-256:

- `contrasts.csv`: `83522253e5190006c5ab6487dd2da1d0b3876ea5e6c4c8af74f7545124c75595`
- `sensitivity.csv`: `f28565187f6ad8909e0787f91199a6ab66a00f52b147bf2ac1449fe54a3c9baa`
- `provenance.json`: `500d56d07124716919fb90949fc3bdb7cdef1146701c715fb9304f29d54ef647`

This is a retrospective recomputation on existing test outputs. It does not rerun inference or refit the locked thresholds. The report links the artifacts in `analysis_pa1_20261111/full_tables/`.

## Remaining status checks

- B3-flip completion and its full-test run are recorded in `Runs-management/RUNS.md` (I-31) and `worklogs/2026-11-11_b3_flip_test_completed.md`. Its inference seed is `4294967295`; the prompt-generation seed is 42. The runtime lock/provenance record the inference seed.
- H5.3's existing Step 6 notebook output was generated with source SHA-256 `d19d28d4efb771442a7d57f3233b68e82320dcb817a8a5580a29226d037d0170`. The current Step 6 source SHA-256 is `882a5c8bc364ee90d73255afc6e4e62decd834d3d6d43f38cc42894864975fdc`. The source was updated after that run, and the Step 6 worklog says the notebook has not been rerun. Therefore the previous H5.3 output is not evidence that the current source revision has run; report it as the prior run until the notebook is rerun.
