# Checks before committing the amendment evidence

Date: 6 November 2026. Base checkout: `b24ca027bf1b3b217fbbb2c77899c2f2b9ae6af4` on `fix/kaggle-repeat-main`.

- Isolated reproduction: completed successfully with the original optimizer, new verifier and four archived validation inputs only; all four corrected thresholds match. See the isolated stdout and JSON audit.
- Historical optimizer identity: current bytes match commit `282033d3ed30b9f91392fec063bd2b2ce10266f4`, SHA-256 `9d83acbe5a1767d0e91c6e5950ab73e92c6b4d05980422486a1876564e4db711`.
- Required governance checks: `python -m pytest tests/test_preregistration_integrity.py 01_Author_Baseline_Unified/diagnostic_kit/tests/test_probes.py 01_Author_Baseline_Unified/diagnostic_kit/tests/test_stats_and_complementarity.py -q` returned **37 passed in 10.06s**.
- Submitted PDF SHA-256 previously verified in this preparation: `22648ead896baf5c1032de700c12fb97bd6dc44f0a8049292532ae6c0468b14c`.

No GPU inference, active threshold changes, active arm changes or modification of the submitted PDF/ZIP was performed. B3 pair construction is a proposed amended method; these checks do not certify an implementation or pair bank that has not yet been built.

## B1-H2 documentation follow-up on 6 November

- Base checkout for this follow-up: `846279676b60ca1185210642e75699b914e36a4d`, which separately implemented the B1-H2 supplemental lock.
- Verified both B1-H2 values, validation MCCs, per-dataset timestamps and the embedded checksum against the committed artifact/config. Confirmed exactly two keys were added and all 14 preceding values were preserved; mirrors match byte-for-byte.
- Verified the English Justification matches the standalone paste-ready file and every fixed-commit evidence target E1-E18 exists in local Git objects. New B1-H2 references must be published before OSF submission.
- The old integrity test failed because it required exactly 14 values and the previous disclosure-only reseal text. Updated it to check the 16-value supplement, preserve the original 14 values against the immutable submitted ZIP, and validate B1-H2 artifact identities/counts and the immediate predecessor seal. The archived ZIP's older seal differs from the later disclosure reseal, so these identities are explicitly distinguished.
- Reran the same three required test files: **37 passed in 8.74s**. A subsequent edit only updated the test module's descriptive header.
- This follow-up only updates documentation and its integrity check; it does not fit thresholds or alter the active threshold configuration.
