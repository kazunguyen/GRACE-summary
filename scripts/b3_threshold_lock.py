"""Load a separately sealed B3-new threshold with a caller-pinned file hash."""
import hashlib
import json
from pathlib import Path


def canonical_hash(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=False, allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_threshold(path, expected_sha256, dataset, expected_identity):
    """Fail closed on bytes, seal, scope, or any supplied method identity mismatch.

    The expected hash must come from the reviewed delivery, not the lock itself.
    Validation prompt hashes are evidence; test prompts have their own manifest.
    """
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ValueError("Threshold lock file checksum mismatch")
    lock = json.loads(raw)
    unsigned = {k: v for k, v in lock.items() if k != "seal_sha256"}
    if canonical_hash(unsigned) != lock.get("seal_sha256"):
        raise ValueError("Threshold lock canonical seal mismatch")
    if (lock.get("status"), lock.get("arm"), lock.get("method_id"),
            lock.get("seed"), lock.get("dataset")) != (
            "LOCKED", "B3", "b3-verified-patch-v1", 42, dataset):
        raise ValueError("Threshold lock scope mismatch")
    required = {"method_id", "pool_sha256", "model_sha256", "tokenizer_revision",
                "runtime_contract_sha256", "scoring", "worker_sha256"}
    if not required.issubset(expected_identity):
        raise ValueError("Incomplete expected threshold application identity")
    if any(lock["application_identity"].get(k) != v
           for k, v in expected_identity.items()):
        raise ValueError("Threshold method/pool/model/tokenizer/runtime/worker mismatch")
    tau = lock["tau_star"]
    if type(tau) not in (float, int) or not 0.01 <= tau <= 0.99:
        raise ValueError("Invalid locked threshold")
    return tau
