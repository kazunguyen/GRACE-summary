# Changes and exposure record for OSF submission

The historical `prereg-v1` Git tag predates the current OSF package. It is not evidence that the current protocol or threshold seal preceded the historical test runs. No OSF registration URL or approval timestamp has been recorded yet.

## 2026-11-03 — pre-submission disclosure correction

- Corrected `configs/protocol.yaml`, its diagnostic-kit copy, and `configs/protocol_en.yaml` to disclose Tier 1 test metrics, B2-flip Devign test raw-label exposure (230 samples), and partial B2-rand validation inference.
- Documented the executed `llama-cpp-python 0.3.16` full-vocabulary-logit scoring path. API top-k handling remains a separate conditional rule. No inference output was changed or rerun by this documentation correction.
- Resealed `configs/thresholds.json` and its diagnostic-kit copy because the corrected protocol has a new SHA-256. All 14 threshold **values remain identical**. The preceding seal and protocol hashes are retained in metadata and Git history; `locked_utc` now records this reseal, not the original validation fitting time. This reseal does not turn earlier test results into prospective results.
- Updated both OSF submission guides and the package README to remove zero-test-exposure claims. A registration URL and timestamp must be added only after actual OSF approval, without changing the submitted PDF/ZIP bytes.

Future changes after OSF registration must be appended here with the date, reason, affected analyses and whether they are exploratory.
