# Devign CodeT5 validation/test — Kaggle source bundle

Upload this ZIP as a Kaggle Dataset. Import the separate .ipynb notebook, Add Input this Dataset, enable GPU + Internet, and Run All.

Only validation/test raw inputs (2732 each) are included. No train data or CPG graphs. Raw JSONL bytes are checked against GRACE-native provenance. Code normalization is `.strip()` exactly as current GRACE-summary. Frozen CodeT5-base revision 02cd2d31bb7c6d0e4d91156167b2de044989c733; T5EncoderModel, RobertaTokenizer, max_length=512, dynamic padding, masked-mean pooling, float32, no AMP/quantization/whitening. TF32 is disabled. CUDA mandatory; does not silently fall back to CPU. One GPU, default batch 64.

Stage output: validation/vectors.npy + manifest.json and test/vectors.npy + manifest.json. Same ID/code-hash order as local raw files. Resumable per batch in the same working directory. Remote GPU vector values can differ from CPU by floating point rounding; bitwise equality is not promised.

Download devign_codet5_validation_test_cache.zip. After local train job stops/finishes, place its validation/ and test/ beside the local Devign train/ cache, preserving filenames. Verify export_manifest.json SHA256 before copying. The result cannot be used alone by CachedEmbedder, which requires train + validation + test. Do not replace the completed counter to fake missing rows.

Dependencies: Kaggle CUDA-enabled PyTorch >=2.6 is retained, transformers==4.57.1 installed. Internet downloads only the pinned model and pip packages; no dataset download or API keys required. This bundle was checked locally for syntax, data hashes, packaging and simulated CUDA control flow; no real Kaggle GPU execution was performed before delivery.
