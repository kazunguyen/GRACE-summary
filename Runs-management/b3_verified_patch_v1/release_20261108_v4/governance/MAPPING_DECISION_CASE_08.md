# Governance Mapping Decision: Case 08 (Devign 8614 & 26054)

- **Case ID:** `case_08_ffmpeg_can_safely_read_8614_26054`
- **Repository:** `FFmpeg/FFmpeg` (`libavcodec/escape124.c`)
- **Parent Commit:** `4b529edff8934c258af95e5acc51f84deea66262`
- **Fix Commit:** `3d7817048cb387de87600f2152075f78b37b60a6`
- **Status:** **RATIFIED (EMPTY LINES ONLY)**

---

## 1. Mapping Verification & Transformation Rule

Devign clean train donors `devign:train:8614` (vulnerable=1) and `devign:train:26054` (patched=0) represent the function `can_safely_read`.
When compared against raw upstream extractions from `libavcodec/escape124.c` at commits `4b529edff8` and `3d7817048c`, exact byte SHA-256 hashes differ due to the Devign export serialization inserting interleaved blank lines (`\n\n`).

- **Transformation Rule:** Completely blank lines (`line == ""`) are filtered out.
- **Verification Result:**
  - Vulnerable function: **100% line-by-line identical** under empty line filtering.
  - Patched function: **100% line-by-line identical** under empty line filtering.
  - Token counts, character values, and keyword sequences match perfectly.
  - Exact-bytes match is honestly reported as **FALSE**.

```
Upstream Raw Before (SHA-256: 9e037e8ecb093f421a6d610b9c7de7ec5f2a7b8e03bc37ef813638c020857454):
static int can_safely_read(GetBitContext* gb, int bits) {
    return get_bits_left(gb) >= bits;
}

Donor Bank Before (SHA-256: 4606a83675db1907349a2ac64be8ed091bd0ec903a1ba397b70d893390429c0a):
static int can_safely_read(GetBitContext* gb, int bits) {

    return get_bits_left(gb) >= bits;

}
```

## 2. Governance Policy & Scope Boundaries

1. **Frozen Bank Preservation:** Per AGENTS.md Section 2.5, clean donor banks remain strictly frozen. Donor text is preserved in prompt demonstrations while raw upstream evidence is cryptographically bound in the candidate payload.
2. **No General Whitespace Token Split Equivalence:** This mapping decision is certified exclusively for Case 08 based on proved empty-line preservation. It does NOT claim general C/C++ `.split()` equivalence.
3. **Demonstration Scope Limitation:** The upstream commit `3d7817048cb387de87600f2152075f78b37b60a6` contains two changes in `escape124.c`:
   - Change 1 (Hunk 1): In `can_safely_read(gb, bits)`, widening parameter `bits` from `int` to `uint64_t`.
   - Change 2 (Hunk 2): In caller `unpack_codebook(gb, ...)`, widening `size * 34` to `size * 34L`.
   The demonstration pair extracts only `can_safely_read`. Human reviewers must evaluate the demonstration knowing that caller expression `size * 34L` resides in `unpack_codebook` outside this demonstration pair.
