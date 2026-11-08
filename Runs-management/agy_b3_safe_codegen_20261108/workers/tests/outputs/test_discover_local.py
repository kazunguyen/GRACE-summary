import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from typing import Any, Dict, List, Optional

DISCOVER_SCRIPT = os.path.abspath(os.environ.get("DISCOVER_LOCAL_SCRIPT", "discover_local.py"))


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def make_jsonl(rows: List[Dict[str, Any]]) -> bytes:
    lines = [json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows]
    content = "\n".join(lines)
    if content:
        content += "\n"
    return content.encode("utf-8")


def build_freeze_tree(
    base_dir: str,
    dataset: str,
    raw_rows: List[Dict[str, Any]],
    manifest_rows: List[Dict[str, Any]],
    donor_count: Optional[int] = None,
    corrupt_raw_hash: bool = False,
    corrupt_manifest_hash: bool = False,
) -> str:
    freeze_dir = os.path.join(base_dir, "freeze")
    ds_dir = os.path.join(freeze_dir, dataset)
    os.makedirs(ds_dir, exist_ok=True)

    raw_bytes = make_jsonl(raw_rows)
    manifest_bytes = make_jsonl(manifest_rows)

    raw_path = os.path.join(ds_dir, "train_raw.jsonl")
    manifest_path = os.path.join(ds_dir, "train_manifest.jsonl")

    with open(raw_path, "wb") as f:
        f.write(raw_bytes)
    with open(manifest_path, "wb") as f:
        f.write(manifest_bytes)

    raw_sha = sha256_bytes(raw_bytes)
    manifest_sha = sha256_bytes(manifest_bytes)

    if corrupt_raw_hash:
        raw_sha = "0" * 64
    if corrupt_manifest_hash:
        manifest_sha = "0" * 64

    if donor_count is None:
        donor_count = sum(1 for m in manifest_rows if m.get("keep_in_bank") is True)

    freeze_manifest = {
        "datasets": {
            dataset: {
                "donor_count": donor_count,
                "files_sha256": {
                    "train_raw.jsonl": raw_sha,
                    "train_manifest.jsonl": manifest_sha,
                },
            }
        }
    }

    with open(os.path.join(freeze_dir, "freeze_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(freeze_manifest, f, indent=2, sort_keys=True)

    return freeze_dir


class TestDiscoverLocal(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_discover_local_")

    def tearDown(self):
        # Coordinator safety review: check the resolved deletion target before
        # recursive cleanup; TMP/TEMP are set to a task-local workspace folder.
        cleanup_root = os.path.realpath(tempfile.gettempdir())
        cleanup_target = os.path.realpath(self.test_dir)
        if os.path.commonpath([cleanup_root, cleanup_target]) != cleanup_root or cleanup_target == cleanup_root:
            raise RuntimeError('Refusing unsafe test cleanup target')
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def run_discover(
        self,
        freeze_path: str,
        dataset: str,
        out_path: str,
        expect_success: bool = True,
    ) -> subprocess.CompletedProcess:
        cmd = [
            sys.executable,
            DISCOVER_SCRIPT,
            "--freeze",
            freeze_path,
            "--dataset",
            dataset,
            "--out",
            out_path,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if expect_success:
            self.assertEqual(
                proc.returncode,
                0,
                f"discover_local failed unexpectedly.\nSTDOUT: {proc.stdout}\nSTDERR: {proc.stderr}",
            )
        else:
            self.assertNotEqual(
                proc.returncode,
                0,
                f"discover_local succeeded unexpectedly.\nSTDOUT: {proc.stdout}\nSTDERR: {proc.stderr}",
            )
        return proc

    def test_heuristic_match_opposite_labels(self):
        func_vulnerable = "void authenticate_user(char *token) { if (!token) return; }"
        func_patched = "void authenticate_user(char *token) { if (validate(token)) return; }"

        raw_rows = [
            {
                "id": "dev_001",
                "dataset": "devign",
                "split": "train",
                "func": func_vulnerable,
                "target": 1,
                "project": "auth_project",
                "commit_id": "commit_vuln_1",
                "source_id": 101,
            },
            {
                "id": "dev_002",
                "dataset": "devign",
                "split": "train",
                "func": func_patched,
                "target": 0,
                "project": "auth_project",
                "commit_id": "commit_patch_1",
                "source_id": 102,
            },
        ]
        manifest_rows = [
            {
                "id": "dev_001",
                "keep_in_bank": True,
                "label": 1,
                "code_sha256": sha256_bytes(func_vulnerable.encode("utf-8")),
            },
            {
                "id": "dev_002",
                "keep_in_bank": True,
                "label": 0,
                "code_sha256": sha256_bytes(func_patched.encode("utf-8")),
            },
        ]

        freeze_dir = build_freeze_tree(self.test_dir, "devign", raw_rows, manifest_rows)
        out_dir = os.path.join(self.test_dir, "out_heuristic")

        self.run_discover(freeze_dir, "devign", out_dir, expect_success=True)

        candidate_path = os.path.join(out_dir, "candidate_pairs.jsonl")
        donor_index_path = os.path.join(out_dir, "donor_index.jsonl")
        prioritized_path = os.path.join(out_dir, "prioritized_candidates.json")
        summary_path = os.path.join(out_dir, "summary.json")

        for p in [candidate_path, donor_index_path, prioritized_path, summary_path]:
            self.assertTrue(os.path.isfile(p), f"Missing expected output artifact: {p}")

        with open(candidate_path, "r", encoding="utf-8") as f:
            pairs = [json.loads(line) for line in f if line.strip()]

        self.assertEqual(len(pairs), 1)
        p = pairs[0]
        self.assertEqual(p["project"], "auth_project")
        self.assertEqual(p["function_hint"], "authenticate_user")
        self.assertEqual(p["vulnerable_id"], "dev_001")
        self.assertEqual(p["patched_candidate_id"], "dev_002")
        self.assertEqual(p["vulnerable_commit"], "commit_vuln_1")
        self.assertEqual(p["patched_candidate_commit"], "commit_patch_1")
        self.assertEqual(p["before_sha256"], sha256_bytes(func_vulnerable.encode("utf-8")))
        self.assertEqual(p["after_sha256"], sha256_bytes(func_patched.encode("utf-8")))
        self.assertEqual(p["characters"], len(func_vulnerable) + len(func_patched))
        self.assertFalse(p["same_commit"])
        self.assertEqual(p["status"], "UNVERIFIED_NAME_MATCH_NOT_AN_ELIGIBLE_PAIR")

        with open(donor_index_path, "r", encoding="utf-8") as f:
            donors = [json.loads(line) for line in f if line.strip()]
        self.assertEqual(len(donors), 2)
        for d in donors:
            self.assertNotIn("func", d)
            self.assertIn("id", d)
            self.assertIn("code_sha256", d)
            self.assertIn("function_hint", d)
            self.assertEqual(d["function_hint"], "authenticate_user")

        with open(prioritized_path, "r", encoding="utf-8") as f:
            prioritized = json.load(f)
        self.assertEqual(len(prioritized), 1)
        self.assertEqual(prioritized[0]["vulnerable_id"], "dev_001")

        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)
        self.assertEqual(summary["dataset"], "devign")
        self.assertEqual(summary["raw_count"], 2)
        self.assertEqual(summary["bank_count"], 2)
        self.assertEqual(summary["candidate_count"], 1)
        self.assertEqual(summary["same_commit_candidate_count"], 0)
        self.assertEqual(summary["donors_missing_commit_id"], 0)
        self.assertEqual(summary["verified_pairs"], 0)
        self.assertEqual(summary["reviewed_pairs"], 0)
        self.assertIsInstance(summary["limitations"], list)
        self.assertIn("candidate_pairs.jsonl", summary["output_sha256"])
        self.assertIn("donor_index.jsonl", summary["output_sha256"])
        self.assertIn("prioritized_candidates.json", summary["output_sha256"])
        self.assertNotIn("summary.json", summary["output_sha256"])

    def test_excluded_donor(self):
        func1 = "int calculate_checksum(int *buf) { return 0; }"
        func2 = "int calculate_checksum(int *buf) { return 1; }"
        raw_rows = [
            {
                "id": "r1",
                "dataset": "reveal",
                "split": "train",
                "func": func1,
                "target": 1,
                "project": "p1",
                "commit_id": "c1",
                "source_id": 1,
            },
            {
                "id": "r2",
                "dataset": "reveal",
                "split": "train",
                "func": func2,
                "target": 0,
                "project": "p1",
                "commit_id": "c2",
                "source_id": 2,
            },
        ]
        manifest_rows = [
            {
                "id": "r1",
                "keep_in_bank": False,
                "label": 1,
                "code_sha256": sha256_bytes(func1.encode("utf-8")),
            },
            {
                "id": "r2",
                "keep_in_bank": True,
                "label": 0,
                "code_sha256": sha256_bytes(func2.encode("utf-8")),
            },
        ]
        freeze_dir = build_freeze_tree(
            self.test_dir, "reveal", raw_rows, manifest_rows, donor_count=1
        )
        out_dir = os.path.join(self.test_dir, "out_excluded")

        self.run_discover(freeze_dir, "reveal", out_dir, expect_success=True)

        with open(os.path.join(out_dir, "summary.json"), "r", encoding="utf-8") as f:
            summary = json.load(f)
        self.assertEqual(summary["raw_count"], 2)
        self.assertEqual(summary["bank_count"], 1)
        self.assertEqual(summary["candidate_count"], 0)
        self.assertEqual(summary["verified_pairs"], 0)

        with open(os.path.join(out_dir, "donor_index.jsonl"), "r", encoding="utf-8") as f:
            donors = [json.loads(line) for line in f if line.strip()]
        self.assertEqual(len(donors), 1)
        self.assertEqual(donors[0]["id"], "r2")

    def test_no_match(self):
        func1 = "int func_alpha(void) { return 0; }"
        func2 = "int func_beta(void) { return 0; }"
        raw_rows = [
            {
                "id": "r1",
                "dataset": "devign",
                "split": "train",
                "func": func1,
                "target": 1,
                "project": "p",
                "commit_id": "c1",
                "source_id": 1,
            },
            {
                "id": "r2",
                "dataset": "devign",
                "split": "train",
                "func": func2,
                "target": 0,
                "project": "p",
                "commit_id": "c2",
                "source_id": 2,
            },
        ]
        manifest_rows = [
            {
                "id": "r1",
                "keep_in_bank": True,
                "label": 1,
                "code_sha256": sha256_bytes(func1.encode("utf-8")),
            },
            {
                "id": "r2",
                "keep_in_bank": True,
                "label": 0,
                "code_sha256": sha256_bytes(func2.encode("utf-8")),
            },
        ]
        freeze_dir = build_freeze_tree(self.test_dir, "devign", raw_rows, manifest_rows)
        out_dir = os.path.join(self.test_dir, "out_no_match")
        self.run_discover(freeze_dir, "devign", out_dir, expect_success=True)

        with open(os.path.join(out_dir, "candidate_pairs.jsonl"), "r", encoding="utf-8") as f:
            pairs = [line for line in f if line.strip()]
        self.assertEqual(len(pairs), 0)

        with open(os.path.join(out_dir, "summary.json"), "r", encoding="utf-8") as f:
            summary = json.load(f)
        self.assertEqual(summary["candidate_count"], 0)
        self.assertEqual(summary["verified_pairs"], 0)

    def test_missing_commits_and_same_commit_flag(self):
        func1 = "void handler(int x) { x = 1; }"
        func2 = "void handler(int x) { x = 2; }"
        func3 = "void handler(int x) { x = 3; }"
        raw_rows = [
            {
                "id": "r1",
                "dataset": "devign",
                "split": "train",
                "func": func1,
                "target": 1,
                "project": "p",
                "commit_id": None,
                "source_id": 1,
            },
            {
                "id": "r2",
                "dataset": "devign",
                "split": "train",
                "func": func2,
                "target": 0,
                "project": "p",
                "commit_id": "comm_shared",
                "source_id": 2,
            },
            {
                "id": "r3",
                "dataset": "devign",
                "split": "train",
                "func": func3,
                "target": 1,
                "project": "p",
                "commit_id": "comm_shared",
                "source_id": 3,
            },
        ]
        manifest_rows = [
            {
                "id": "r1",
                "keep_in_bank": True,
                "label": 1,
                "code_sha256": sha256_bytes(func1.encode("utf-8")),
            },
            {
                "id": "r2",
                "keep_in_bank": True,
                "label": 0,
                "code_sha256": sha256_bytes(func2.encode("utf-8")),
            },
            {
                "id": "r3",
                "keep_in_bank": True,
                "label": 1,
                "code_sha256": sha256_bytes(func3.encode("utf-8")),
            },
        ]
        freeze_dir = build_freeze_tree(self.test_dir, "devign", raw_rows, manifest_rows)
        out_dir = os.path.join(self.test_dir, "out_commits")
        self.run_discover(freeze_dir, "devign", out_dir, expect_success=True)

        with open(os.path.join(out_dir, "summary.json"), "r", encoding="utf-8") as f:
            summary = json.load(f)
        self.assertEqual(summary["donors_missing_commit_id"], 1)
        self.assertEqual(summary["same_commit_candidate_count"], 1)
        self.assertEqual(summary["candidate_count"], 2)
        self.assertEqual(summary["verified_pairs"], 0)

        with open(os.path.join(out_dir, "candidate_pairs.jsonl"), "r", encoding="utf-8") as f:
            pairs = [json.loads(line) for line in f if line.strip()]

        pair_map = {(p["vulnerable_id"], p["patched_candidate_id"]): p for p in pairs}
        self.assertIn(("r1", "r2"), pair_map)
        self.assertFalse(pair_map[("r1", "r2")]["same_commit"])
        self.assertIsNone(pair_map[("r1", "r2")]["vulnerable_commit"])

        self.assertIn(("r3", "r2"), pair_map)
        self.assertTrue(pair_map[("r3", "r2")]["same_commit"])
        self.assertEqual(pair_map[("r3", "r2")]["vulnerable_commit"], "comm_shared")

    def test_missing_project_handled_without_type_error(self):
        func1 = "void run_job(void) { check(); }"
        func2 = "void run_job(void) { verify(); }"
        raw_rows = [
            {
                "id": "r1",
                "dataset": "devign",
                "split": "train",
                "func": func1,
                "target": 1,
                "project": None,
                "commit_id": "c1",
                "source_id": 1,
            },
            {
                "id": "r2",
                "dataset": "devign",
                "split": "train",
                "func": func2,
                "target": 0,
                "project": "project_x",
                "commit_id": "c2",
                "source_id": 2,
            },
            {
                "id": "r3",
                "dataset": "devign",
                "split": "train",
                "func": func2,
                "target": 0,
                "project": None,
                "commit_id": "c3",
                "source_id": 3,
            },
        ]
        manifest_rows = [
            {
                "id": "r1",
                "keep_in_bank": True,
                "label": 1,
                "code_sha256": sha256_bytes(func1.encode("utf-8")),
            },
            {
                "id": "r2",
                "keep_in_bank": True,
                "label": 0,
                "code_sha256": sha256_bytes(func2.encode("utf-8")),
            },
            {
                "id": "r3",
                "keep_in_bank": True,
                "label": 0,
                "code_sha256": sha256_bytes(func2.encode("utf-8")),
            },
        ]
        freeze_dir = build_freeze_tree(self.test_dir, "devign", raw_rows, manifest_rows)
        out_dir = os.path.join(self.test_dir, "out_null_project")
        self.run_discover(freeze_dir, "devign", out_dir, expect_success=True)

        with open(os.path.join(out_dir, "candidate_pairs.jsonl"), "r", encoding="utf-8") as f:
            pairs = [json.loads(line) for line in f if line.strip()]
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0]["vulnerable_id"], "r1")
        self.assertEqual(pairs[0]["patched_candidate_id"], "r3")
        self.assertIsNone(pairs[0]["project"])

    def test_deterministic_artifact_bytes_across_two_out_dirs(self):
        raw_rows = []
        manifest_rows = []
        for i in range(1, 6):
            fn_name = f"worker_routine_{i % 2}"
            target = i % 2
            func_body = f"void {fn_name}(int step) {{ process({i}); }}"
            rid = f"id_{i:03d}"
            raw_rows.append({
                "id": rid,
                "dataset": "devign",
                "split": "train",
                "func": func_body,
                "target": target,
                "project": "proj_det",
                "commit_id": f"commit_{i}",
                "source_id": i,
            })
            manifest_rows.append({
                "id": rid,
                "keep_in_bank": True,
                "label": target,
                "code_sha256": sha256_bytes(func_body.encode("utf-8")),
            })

        freeze_dir = build_freeze_tree(self.test_dir, "devign", raw_rows, manifest_rows)
        out_dir1 = os.path.join(self.test_dir, "out_run_1")
        out_dir2 = os.path.join(self.test_dir, "out_run_2")

        self.run_discover(freeze_dir, "devign", out_dir1, expect_success=True)
        self.run_discover(freeze_dir, "devign", out_dir2, expect_success=True)

        for filename in ["candidate_pairs.jsonl", "donor_index.jsonl", "prioritized_candidates.json", "summary.json"]:
            p1 = os.path.join(out_dir1, filename)
            p2 = os.path.join(out_dir2, filename)
            with open(p1, "rb") as f1, open(p2, "rb") as f2:
                b1 = f1.read()
                b2 = f2.read()
            self.assertEqual(b1, b2, f"File content mismatch between runs for {filename}")

    def test_corrupt_raw_hash_rejection_before_output_creation(self):
        func = "int test(void) { return 0; }"
        raw_rows = [{
            "id": "r1",
            "dataset": "devign",
            "split": "train",
            "func": func,
            "target": 1,
            "project": "p",
            "commit_id": "c",
            "source_id": 1,
        }]
        manifest_rows = [{
            "id": "r1",
            "keep_in_bank": True,
            "label": 1,
            "code_sha256": sha256_bytes(func.encode("utf-8")),
        }]
        freeze_dir = build_freeze_tree(
            self.test_dir, "devign", raw_rows, manifest_rows, corrupt_raw_hash=True
        )
        out_dir = os.path.join(self.test_dir, "out_corrupt_raw")

        self.run_discover(freeze_dir, "devign", out_dir, expect_success=False)
        self.assertFalse(os.path.exists(out_dir), "Output directory was created despite manifest hash failure!")

    def test_duplicate_id_rejected(self):
        func1 = "void funcA(void) { return; }"
        func2 = "void funcB(void) { return; }"
        raw_rows = [
            {
                "id": "duplicate_id",
                "dataset": "devign",
                "split": "train",
                "func": func1,
                "target": 1,
                "project": "p",
                "commit_id": "c1",
                "source_id": 1,
            },
            {
                "id": "duplicate_id",
                "dataset": "devign",
                "split": "train",
                "func": func2,
                "target": 0,
                "project": "p",
                "commit_id": "c2",
                "source_id": 2,
            },
        ]
        manifest_rows = [
            {
                "id": "duplicate_id",
                "keep_in_bank": True,
                "label": 1,
                "code_sha256": sha256_bytes(func1.encode("utf-8")),
            },
            {
                "id": "duplicate_id",
                "keep_in_bank": True,
                "label": 0,
                "code_sha256": sha256_bytes(func2.encode("utf-8")),
            },
        ]
        freeze_dir = build_freeze_tree(self.test_dir, "devign", raw_rows, manifest_rows)
        out_dir = os.path.join(self.test_dir, "out_duplicate_id")

        self.run_discover(freeze_dir, "devign", out_dir, expect_success=False)
        self.assertFalse(os.path.exists(out_dir))

    def test_label_and_code_mismatch_rejected(self):
        func_valid = "void compute(void) { do_math(); }"
        func_altered = "void compute(void) { corrupted(); }"
        raw_rows = [{
            "id": "r1",
            "dataset": "devign",
            "split": "train",
            "func": func_valid,
            "target": 1,
            "project": "p",
            "commit_id": "c1",
            "source_id": 1,
        }]
        manifest_rows = [{
            "id": "r1",
            "keep_in_bank": True,
            "label": 0,
            "code_sha256": sha256_bytes(func_valid.encode("utf-8")),
        }]
        freeze_dir = build_freeze_tree(self.test_dir, "devign", raw_rows, manifest_rows)
        out_dir = os.path.join(self.test_dir, "out_label_mismatch")
        self.run_discover(freeze_dir, "devign", out_dir, expect_success=False)
        self.assertFalse(os.path.exists(out_dir))

        manifest_rows_code_mismatch = [{
            "id": "r1",
            "keep_in_bank": True,
            "label": 1,
            "code_sha256": sha256_bytes(func_altered.encode("utf-8")),
        }]
        freeze_dir2 = build_freeze_tree(
            self.test_dir, "devign", raw_rows, manifest_rows_code_mismatch
        )
        out_dir2 = os.path.join(self.test_dir, "out_code_mismatch")
        self.run_discover(freeze_dir2, "devign", out_dir2, expect_success=False)
        self.assertFalse(os.path.exists(out_dir2))

    def test_donor_count_mismatch_rejected(self):
        func = "int status_check(void) { return 1; }"
        raw_rows = [{
            "id": "r1",
            "dataset": "devign",
            "split": "train",
            "func": func,
            "target": 1,
            "project": "p",
            "commit_id": "c",
            "source_id": 1,
        }]
        manifest_rows = [{
            "id": "r1",
            "keep_in_bank": True,
            "label": 1,
            "code_sha256": sha256_bytes(func.encode("utf-8")),
        }]
        freeze_dir = build_freeze_tree(
            self.test_dir, "devign", raw_rows, manifest_rows, donor_count=999
        )
        out_dir = os.path.join(self.test_dir, "out_count_mismatch")
        self.run_discover(freeze_dir, "devign", out_dir, expect_success=False)
        self.assertFalse(os.path.exists(out_dir))

    def test_refuse_overwrite_existing_out_with_sentinel(self):
        func = "int test(void) { return 0; }"
        raw_rows = [{
            "id": "r1",
            "dataset": "devign",
            "split": "train",
            "func": func,
            "target": 1,
            "project": "p",
            "commit_id": "c",
            "source_id": 1,
        }]
        manifest_rows = [{
            "id": "r1",
            "keep_in_bank": True,
            "label": 1,
            "code_sha256": sha256_bytes(func.encode("utf-8")),
        }]
        freeze_dir = build_freeze_tree(self.test_dir, "devign", raw_rows, manifest_rows)

        existing_out_dir = os.path.join(self.test_dir, "existing_dir")
        os.makedirs(existing_out_dir, exist_ok=True)
        sentinel_path = os.path.join(existing_out_dir, "sentinel.txt")
        sentinel_content = b"SENTINEL_DATA_DO_NOT_OVERWRITE"
        with open(sentinel_path, "wb") as f:
            f.write(sentinel_content)

        self.run_discover(freeze_dir, "devign", existing_out_dir, expect_success=False)

        self.assertTrue(os.path.isfile(sentinel_path))
        with open(sentinel_path, "rb") as f:
            self.assertEqual(f.read(), sentinel_content)

        items = os.listdir(existing_out_dir)
        self.assertEqual(items, ["sentinel.txt"])

    def test_prioritized_candidates_shortlist_cap_at_12(self):
        raw_rows = []
        manifest_rows = []

        for i in range(1, 5):
            func_vuln = f"int multi_pair_fn(int a) {{ return a + {i}; }}"
            rid_v = f"vuln_{i:02d}"
            raw_rows.append({
                "id": rid_v,
                "dataset": "devign",
                "split": "train",
                "func": func_vuln,
                "target": 1,
                "project": "p_large",
                "commit_id": f"cv_{i}",
                "source_id": 100 + i,
            })
            manifest_rows.append({
                "id": rid_v,
                "keep_in_bank": True,
                "label": 1,
                "code_sha256": sha256_bytes(func_vuln.encode("utf-8")),
            })

        for j in range(1, 6):
            padding = "x" * (j * 10)
            func_clean = f"int multi_pair_fn(int a) {{ /* {padding} */ return a; }}"
            rid_c = f"clean_{j:02d}"
            raw_rows.append({
                "id": rid_c,
                "dataset": "devign",
                "split": "train",
                "func": func_clean,
                "target": 0,
                "project": "p_large",
                "commit_id": f"cc_{j}",
                "source_id": 200 + j,
            })
            manifest_rows.append({
                "id": rid_c,
                "keep_in_bank": True,
                "label": 0,
                "code_sha256": sha256_bytes(func_clean.encode("utf-8")),
            })

        freeze_dir = build_freeze_tree(self.test_dir, "devign", raw_rows, manifest_rows)
        out_dir = os.path.join(self.test_dir, "out_prioritized")
        self.run_discover(freeze_dir, "devign", out_dir, expect_success=True)

        with open(os.path.join(out_dir, "summary.json"), "r", encoding="utf-8") as f:
            summary = json.load(f)
        self.assertEqual(summary["candidate_count"], 4 * 5)
        self.assertEqual(summary["verified_pairs"], 0)

        with open(os.path.join(out_dir, "prioritized_candidates.json"), "r", encoding="utf-8") as f:
            prioritized = json.load(f)
        self.assertLessEqual(len(prioritized), 12)
        self.assertEqual(len(prioritized), 12)

        characters_seq = [item["characters"] for item in prioritized]
        self.assertEqual(characters_seq, sorted(characters_seq))


if __name__ == "__main__":
    if "--script" in sys.argv:
        idx = sys.argv.index("--script")
        if idx + 1 < len(sys.argv):
            DISCOVER_SCRIPT = os.path.abspath(sys.argv[idx + 1])
            del sys.argv[idx : idx + 2]
        else:
            del sys.argv[idx]
    unittest.main()
