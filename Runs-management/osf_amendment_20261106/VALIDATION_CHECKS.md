# Checks before committing the amendment evidence

Date: 6 November 2026. Base checkout: `b24ca027bf1b3b217fbbb2c77899c2f2b9ae6af4` on `fix/kaggle-repeat-main`.

- Isolated reproduction: completed successfully with the original optimizer, new verifier and four archived validation inputs only; all four corrected thresholds match. See the isolated stdout and JSON audit.
- Historical optimizer identity: current bytes match commit `282033d3ed30b9f91392fec063bd2b2ce10266f4`, SHA-256 `9d83acbe5a1767d0e91c6e5950ab73e92c6b4d05980422486a1876564e4db711`.
- Required governance checks: `python -m pytest tests/test_preregistration_integrity.py 01_Author_Baseline_Unified/diagnostic_kit/tests/test_probes.py 01_Author_Baseline_Unified/diagnostic_kit/tests/test_stats_and_complementarity.py -q` returned **37 passed in 10.06s**.
- Submitted PDF SHA-256 previously verified in this preparation: `22648ead896baf5c1032de700c12fb97bd6dc44f0a8049292532ae6c0468b14c`.

No GPU inference, active threshold changes, active arm changes or modification of the submitted PDF/ZIP was performed. B3 pair construction is a proposed amended method; these checks do not certify an implementation or pair bank that has not yet been built.
