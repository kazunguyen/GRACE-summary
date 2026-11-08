# Review Evidence Packet: case_08_ffmpeg_can_safely_read_8614_26054

- **Dataset:** Devign
- **Project:** ffmpeg
- **Function Hint:** `can_safely_read`
- **Vulnerable Donor:** `devign:train:8614` (Commit `3d7817048cb387de87600f2152075f78b37b60a6`)
- **Patched Candidate:** `devign:train:26054` (Commit `e494f44c051d7dccc038a603ab22532b87dd1705`)
- **Payload SHA-256 (Canonical Candidate Hash):** `0ced77fefccbcef797c3c01abfa0d139d5611e2d562e8f5ec01089ff05168ee1`
- **Admissible Candidate Available:** **True**

## Source Revisions
- Direct Parent Edge in Git: **True**
- Vulnerable Parents: `['4b529edff8934c258af95e5acc51f84deea66262']`
- Patched Parents: `['ca10d66719f5bb3242c77d178bdd9068f52ee668']`

## Changed Files
- Vulnerable Commit Modified: `['libavcodec/escape124.c']`
- Patched Commit Modified: `['libavcodec/escape124.c']`
- Shared Files: `['libavcodec/escape124.c']`

## Commit Messages
- **Vulnerable:** escape124: fix integer overflow leading to excessive memory allocation

Fixes Ticket1629

Signed-off-by: Michael Niedermayer <michaelni@gmx.at>
- **Patched:** avcodec/escape124: fix infinite loop

Remove can_safely_read() as its not really needed with
checked bitstream reader.

Fixes #2984.
Reported-by: Piotr Bandurski <ami_stuff@o2.pl>
Signed-off-by: Paul 

## Archived Source Evidence
- **Repository:** `FFmpeg/FFmpeg`
- **Source File Path:** `libavcodec/escape124.c`
- **Security Rationale:** In FFmpeg libavcodec/escape124.c (commit 3d7817048cb387de87600f2152075f78b37b60a6, Ticket 1629), the upstream security fix addresses an integer overflow leading to excessive memory allocation. In the vulnerable code, can_safely_read(gb, bits) declared parameter 'bits' as int (32-bit signed), while caller unpack_codebook computed 'size * 34' where 'size' was unsigned. The complete upstream fix consists of two changes: (1) in can_safely_read, widening the parameter type from 'int' to 'uint64_t' so that large bit counts do not evaluate improperly against get_bits_left(gb); and (2) in unpack_codebook, promoting the multiplication to 'size * 34L'. This contrastive demonstration pair captures exclusively change (1) — widening parameter 'bits' from 'int' to 'uint64_t' in can_safely_read — while change (2) ('size * 34L') resides in caller unpack_codebook outside this function pair. Reviewers must evaluate this demonstration in the context of the full upstream commit diff, acknowledging that the demonstrated snippet reflects the parameter type widening component of the integer overflow defense.
- **Key Difference:** Before patch: `static int can_safely_read(GetBitContext* gb, int bits) {`. After patch: `static int can_safely_read(GetBitContext* gb, uint64_t bits) {`. Security rationale: In FFmpeg libavcodec/escape124.c (commit 3d7817048cb387de87600f2152075f78b37b60a6, Ticket 1629), the upstream security fix addresses an integer overflow leading to excessive memory allocation. In the vulnerable code, can_safely_read(gb, bits) declared parameter 'bits' as int (32-bit signed), while caller unpack_codebook computed 'size * 34' where 'size' was unsigned. The complete upstream fix consists of two changes: (1) in can_safely_read, widening the parameter type from 'int' to 'uint64_t' so that large bit counts do not evaluate improperly against get_bits_left(gb); and (2) in unpack_codebook, promoting the multiplication to 'size * 34L'. This contrastive demonstration pair captures exclusively change (1) — widening parameter 'bits' from 'int' to 'uint64_t' in can_safely_read — while change (2) ('size * 34L') resides in caller unpack_codebook outside this function pair. Reviewers must evaluate this demonstration in the context of the full upstream commit diff, acknowledging that the demonstrated snippet reflects the parameter type widening component of the integer overflow defense.

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

### Actual Fix Diff
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

## Review Instructions for Human Reviewers
Please fill out a separate review form verifying:
1. `same_function_verified`: Are the two functions genuinely the same function in upstream source?
2. `security_fix_verified`: Does the change represent an authentic security vulnerability fix?
3. `source_revisions_verified`: Do the commit revisions connect via git parentage and actual patch diff?
4. `explanation_supported`: Is the difference rationale supported by reviewed code changes?
Include `payload_sha256` matching above to certify authenticity.
