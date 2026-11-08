# Review Evidence Packet: case_08_ffmpeg_can_safely_read_8614_26054

- **Dataset:** Devign
- **Project:** FFmpeg (`libavcodec/escape124.c`)
- **Function:** `can_safely_read`
- **Vulnerable Donor:** `devign:train:8614` (Target=1, Commit `3d7817048cb387de87600f2152075f78b37b60a6`)
- **Patched Candidate Donor:** `devign:train:26054` (Target=0, Commit `e494f44c051d7dccc038a603ab22532b87dd1705`)
- **Canonical Payload SHA-256:** `0ced77fefccbcef797c3c01abfa0d139d5611e2d562e8f5ec01089ff05168ee1`
- **Evidence Inputs Manifest SHA-256:** `bd1a8c56480ad4e0e375715ca1d60b144a26fc1e787a2b6fe17913d3eaf9a921`

---

## 1. Upstream Commit & Context

- **Fix Commit:** `3d7817048cb387de87600f2152075f78b37b60a6`
- **Parent Commit:** `4b529edff8934c258af95e5acc51f84deea66262` (Verified Direct Parent in Git Tree)
- **Commit Message:**
```
escape124: fix integer overflow leading to excessive memory allocation

Fixes Ticket1629

Signed-off-by: Michael Niedermayer <michaelni@gmx.at>
```

## 2. Demonstration Scope & Context Notice (Crucial for Reviewers)

> **IMPORTANT EVALUATION CRITERION**:
> The actual upstream fix contains **two distinct hunks** in `escape124.c`:
> 1. In `can_safely_read`: Parameter widening from `int` to `uint64_t`.
> 2. In caller `unpack_codebook`: Integer multiplication promotion from `size * 34` to `size * 34L`.
>
> **The contrastive demonstration pair captures ONLY Hunk 1 (`can_safely_read`).**
> Caller expression `size * 34L` resides in `unpack_codebook` outside this function pair.
> Reviewers must independently determine whether demonstrating parameter widening in `can_safely_read`
> provides a valid, contrastive demonstration of the vulnerability patch mechanism.

## 3. Raw Upstream vs. Donor Bank Mapping

- **Mapping Verdict:** `MAPPING_DECISION_RATIFIED_EMPTY_LINES_ONLY`
- Non-empty line comparison: **100% Match** (`before_empty_line_match: True`, `after_empty_line_match: True`).
- Exact byte match: **False** (Devign JSON serialization added blank lines `\n\n` between lines).
- Donor bank remains completely frozen.

## 4. Source Functions & Actual Fix Diff

### Vulnerable Source Function (Before)
```c
static int can_safely_read(GetBitContext* gb, int bits) {

    return get_bits_left(gb) >= bits;

}
```

### Patched Source Function (After)
```c
static int can_safely_read(GetBitContext* gb, uint64_t bits) {

    return get_bits_left(gb) >= bits;

}
```

### Actual Upstream Fix Diff (Both Hunks)
```diff
--- a/libavcodec/escape124.c
+++ b/libavcodec/escape124.c
@@ -48,7 +48,7 @@ typedef struct Escape124Context {
     CodeBook codebooks[3];
 } Escape124Context;
 
-static int can_safely_read(GetBitContext* gb, int bits) {
+static int can_safely_read(GetBitContext* gb, uint64_t bits) {
     return get_bits_left(gb) >= bits;
 }
 
@@ -90,7 +90,7 @@ static CodeBook unpack_codebook(GetBitContext* gb, unsigned depth,
     unsigned i, j;
     CodeBook cb = { 0 };
 
-    if (!can_safely_read(gb, size * 34))
+    if (!can_safely_read(gb, size * 34L))
         return cb;
 
     if (size >= INT_MAX / sizeof(MacroBlock))

```

## 5. Security Rationale
In FFmpeg libavcodec/escape124.c (commit 3d7817048cb387de87600f2152075f78b37b60a6, Ticket 1629), the upstream security fix addresses an integer overflow leading to excessive memory allocation. In the vulnerable code, can_safely_read(gb, bits) declared parameter 'bits' as int (32-bit signed), while caller unpack_codebook computed 'size * 34' where 'size' was unsigned. The complete upstream fix consists of two changes: (1) in can_safely_read, widening the parameter type from 'int' to 'uint64_t' so that large bit counts do not evaluate improperly against get_bits_left(gb); and (2) in unpack_codebook, promoting the multiplication to 'size * 34L'. This contrastive demonstration pair captures exclusively change (1) — widening parameter 'bits' from 'int' to 'uint64_t' in can_safely_read — while change (2) ('size * 34L') resides in caller unpack_codebook outside this function pair. Reviewers must evaluate this demonstration in the context of the full upstream commit diff, acknowledging that the demonstrated snippet reflects the parameter type widening component of the integer overflow defense.

## 6. Review Instructions for Human Reviewers
Please fill out a separate review form verifying:
1. `same_function_verified`: Are the two functions genuinely the same function in upstream source?
2. `security_fix_verified`: Does the change represent an authentic security vulnerability fix?
3. `source_revisions_verified`: Do the commit revisions connect via git parentage and actual patch diff?
4. `explanation_supported`: Is the difference rationale supported by reviewed code changes and diff context?
Include `payload_sha256: "0ced77fefccbcef797c3c01abfa0d139d5611e2d562e8f5ec01089ff05168ee1"` matching above to certify authenticity.
