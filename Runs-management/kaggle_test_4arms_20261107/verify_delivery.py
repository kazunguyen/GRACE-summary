#!/usr/bin/env python3
"""
Kiểm thử độc lập tính toàn vẹn của gói test 4 arm Nhóm 2 trước khi đẩy lên Kaggle.
"""
import json, hashlib, zipfile, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "delivery_manifest.json"

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""): h.update(chunk)
    return h.hexdigest()

def main():
    print("="*70)
    print("VERIFYING TEST DELIVERY FOR 4 ARMS (GROUP 2)")
    print("="*70)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    
    for arm, arm_data in manifest["arms"].items():
        print(f"Checking {arm}...")
        bundle_path = HERE / "bundles" / arm_data["bundle"]
        assert bundle_path.is_file(), f"Missing bundle: {bundle_path}"
        actual_b_sha = sha256_file(bundle_path)
        assert actual_b_sha == arm_data["bundle_sha256"], f"Bundle SHA mismatch for {arm}"
        
        nb_path = HERE / "notebooks" / arm_data["notebook"]
        assert nb_path.is_file(), f"Missing notebook: {nb_path}"
        actual_nb_sha = sha256_file(nb_path)
        assert actual_nb_sha == arm_data["notebook_sha256"], f"Notebook SHA mismatch for {arm}"
        
        # Verify notebook code cells compile cleanly
        nb_obj = json.loads(nb_path.read_text(encoding="utf-8"))
        for c_idx, cell in enumerate(nb_obj["cells"]):
            if cell["cell_type"] == "code":
                src = "".join(cell["source"])
                if src.startswith("%%writefile"):
                    src = src.split("\n", 1)[1]
                compile(src, f"{arm}_cell_{c_idx}", "exec")
        
        # Verify bundle contents
        with zipfile.ZipFile(bundle_path) as z:
            namelist = z.namelist()
            for s in arm_data["sets"]:
                assert s["name"] in namelist, f"Missing inner set {s['name']} in {arm_data['bundle']}"
                inner_bytes = z.read(s["name"])
                actual_inner_sha = hashlib.sha256(inner_bytes).hexdigest()
                assert actual_inner_sha == s["sha256"], f"Inner zip SHA mismatch: {s['name']}"
                
                with zipfile.ZipFile(z.open(s["name"])) as inner:
                    assert "prompts.jsonl" in inner.namelist()
                    assert "bundle_manifest.json" in inner.namelist()
                    assert "threshold_lock.json" in inner.namelist()
                    
                    b_man = json.loads(inner.read("bundle_manifest.json"))
                    assert b_man["count"] == s["count"]
                    assert b_man["tau_star"] == s["tau_star"]
                    assert b_man["prompts_sha256"] == s["prompts_sha256"]
                    
                    p_lines = [json.loads(l) for l in inner.read("prompts.jsonl").decode("utf-8").splitlines() if l.strip()]
                    assert len(p_lines) == s["count"]
                    for row in p_lines:
                        assert row["arm"] == arm
                        assert row["split"] == "test"
                        if arm == "B2-rep":
                            assert row.get("repeat") is True
                            assert row.get("tag") == "repeat"
                            
        print(f"  -> {arm}: All checks PASSED (Devign {arm_data['thresholds']['devign']}, ReVeal {arm_data['thresholds']['reveal']})")
    
    print("="*70)
    print("ALL 4 ARMS TEST DELIVERY VERIFICATION SUCCEEDED 100%!")
    print("="*70)

if __name__ == "__main__":
    main()
