# B1-H2 Kaggle validation bundle

Completed Kaggle 2xT4 validation inference: Devign 2,732/2,732; ReVeal 2,273/2,273 (5,005 total). Independent verification checked exact IDs, prompt hashes, frozen validation labels, score formula and registered 99-point MCC grid. Final thresholds: Devign tau=0.09, validation MCC=0.0667928192; ReVeal tau=0.21, validation MCC=0.0836323479. Devign coincides with the exploratory Colab value by independent recomputation; ReVeal differs from Colab's 0.67. No test data was used. Kaggle lock payload SHA-256: b5dc7e0da070f75cfabc10c366a08675d1c3f471f1e11fb86ee826a22ce674f8; audit and evidence archive are in the Runs-management artifacts.

Bundle SHA-256: b35b44f430c28ec44052867499ae7537950fb1dc2eee63083c3bdbb9c784c2b4
Notebook: ../notebooks/02_kaggle_qwen_q4_b1_h2_validation_20261106.ipynb
After completion, download `kaggle_threshold_lock.json` with the checkpoint from Kaggle Output.
