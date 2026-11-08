import hashlib
from pathlib import Path

p = Path("01_Author_Baseline_Unified/output/research_freeze_20261101/reveal/donors.tmp")
h = hashlib.sha256()
with open(p, "rb") as f:
    for chunk in iter(lambda: f.read(4 * 1024 * 1024), b""):
        h.update(chunk)
digest = h.hexdigest()
expected = "6bf44ab86c8524d239e610fdccff5916cfc402fef7945d7cbe7f695e287abbce"
print("Digest:", digest)
print("Expected:", expected)
print("Matches:", digest == expected)
