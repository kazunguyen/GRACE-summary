# B3: verified patch-pair selector, 6 November 2026

Status: implementation and software smoke tests; **not an approved pair pool or an inference bundle**. Proposed amendment code is separate from the historical `contrastive_pair_builder.py`. No inference, threshold fitting or OSF submission is performed here.

## Implemented method

`grace_diag.amended_b3.make_pair_candidate` creates an unreviewed record using two donor functions and archived source evidence. It generates a function diff, line ranges and `Key difference` by quoting the actual changed code and the supplied security rationale. It does not infer safety from words such as `sizeof`, `NULL` or `memcpy`. A commit message can supply context, but cannot replace the actual fix diff.

`VerifiedPairSelector` admits only same-dataset clean-train donors with labels 1/0, exact source-code hashes, the same source function, full fix and parent revision IDs, repository/path/source URL, archived source functions, actual fix diff and security rationale. Displayed changes must occur in that actual diff. Two distinct reviewers must approve source revisions, same-function identity, security-fix relevance and explanation support, with each approval bound to the complete evidence payload hash. Review disagreement or later evidence edits require renewed review. These checks verify local consistency; **humans still have to authenticate the source and establish security meaning**. The code cannot turn declarations into independent proof.

Selection exhaustively ranks the approved pool by the mean token-set Jaccard similarity of the target to the two functions, reusing the historical token normalization. Jaccard ranks already verified pairs; it never creates a counterfactual relationship. Exact rational arithmetic and lexicographic pair IDs resolve ties deterministically. Neither target labels nor B2 anchors enter selection. No top-200 approximation or arbitrary fallback is used.

Rendering uses the existing Figure 6 renderer, graph prefix and registered budgets. Complete donor functions, supporting changed lines and the difference must remain visible; an oversized selected pair stops generation. It is not silently replaced by another pair. B3-nodiff removes only the explanation, B3-swap reverses the examples, and B3-flip follows the existing label-flip convention (including label words in the difference). B3-nodiff has its own validation threshold; swap and flip inherit B3, as required by proposal sections 6.6 and 8.5. Existing arms, thresholds, frozen specs and original OSF artifacts are unchanged.

## Reproduce the real-data check

From the repository root:

```powershell
python Runs-management/b3_amended_20261106/check_b3.py --samples 3 --out Runs-management/b3_amended_20261106/my_check
```

The output directory must be new. The script verifies the pinned freeze manifest, clean-train membership/counts, input hashes and validation target code against the original archive. It reads train and validation only. It attempts three actual validation targets per dataset. Without an approved pair manifest, each attempt explicitly pauses.

With a genuinely reviewed manifest and the local pinned tokenizer snapshot:

```powershell
python Runs-management/b3_amended_20261106/check_b3.py --pairs reviewed_pairs.jsonl --tokenizer PATH/TO/b2cff646eb4bb1d68355c01b18ae02e7cf42d120 --samples 3 --out Runs-management/b3_amended_20261106/reviewed_check
```

The manifest is JSONL, one record per pair. Its fields are defined by `make_pair_candidate`; archive `source.fix_diff` from the actual repository change, not a diff invented from two unrelated donor functions. Each review includes `reviewer`, `reviewed_at`, `decision="approve"`, `payload_sha256=payload_hash(pair)` and the four affirmative checks used by `validate_pair`. Do not fabricate human reviews. The CLI rejects synthetic fixture records. It uses only target ID/code/graph from frozen validation specs, discarding their labels and old demonstrations. Successful rendering still requires the registered content audit and a complete prompt freeze before inference.

## Evidence and limits

- `real_data_check_final/report.json`: attempts on six real validation targets and full clean-bank discovery counts. No reviewed pool was supplied; all six pause. This does **not** prove no true pairs exist.
- `real_data_check_final/*_candidate_discovery.json`: twelve short name-match candidates per dataset for source investigation. These are **not eligible pairs**. Function-name extraction is deliberately only a discovery heuristic, with known macro/name ambiguity.
- `synthetic_smoke_preview.txt`: three readable base B3 prompts generated with the pinned tokenizer from synthetic functions. These use invented test-only revision IDs and programmatic review fixtures, explicitly labelled throughout; they are **not real security-fix evidence or inference inputs**.
- `synthetic_smoke_prompts.json`: all twelve synthetic B3-family prompts, hashes, token counts, selection scores and probe metadata. No model responses or prediction accuracy are claimed.
- `tests/test_amended_b3.py`: ranking/ties, empty-pool refusal, source/donor/review corruption, label leakage, budget failure, determinism and exact probe transformations.

Devign contains 21,691 eligible donors and no opposite-label candidate sharing both recorded commit and extracted function hint. REVEAL contains 17,636 eligible donors, all missing commit IDs in the current frozen raw export. Name matches across commits/projects do not resolve before/after provenance. The next research step is authenticating source revision pairs and completing two-person review within the existing donor bank. Expanding the donor dataset would require a separate disclosed decision. GPU validation/test remains paused until that evidence and the required prompt audit exist.
