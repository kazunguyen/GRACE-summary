"""
GRACE Baseline Configuration Module
Unified configuration for author's baseline adhering to evaluation_contract_v2 (context 8192 bytes).
"""

from __future__ import annotations

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import yaml

HERE = Path(__file__).resolve().parent


def is_kaggle_environment() -> bool:
    return os.path.exists("/kaggle/working") or "KAGGLE_URL_BASE" in os.environ


def load_env_variables() -> Dict[str, str]:
    """Load settings from .env files and os.environ."""
    env_paths = [
        Path("D:/JUNIOR/LabThayTho/.env"),
        Path("/mnt/d/JUNIOR/LabThayTho/.env"),
        Path("C:/MY-FILES/LAB-THAY-THO/Graduation-Project/.env"),
        Path("/mnt/c/MY-FILES/LAB-THAY-THO/Graduation-Project/.env"),
        HERE / ".env",
        HERE.parent / ".env",
    ]
    values: Dict[str, str] = {}
    # Iterate in reverse order so earlier paths take higher priority
    for p in reversed(env_paths):
        if p.is_file():
            try:
                for line in p.read_text(encoding="utf-8-sig").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    key, sep, val = line.partition("=")
                    if not sep:
                        continue
                    key = key.strip().removeprefix("export ")
                    val = val.strip()
                    if val.startswith(('"', "'")) and len(val) >= 2 and val[0] == val[-1]:
                        val = val[1:-1]
                    else:
                        val = val.split(" #", 1)[0].strip()
                    values[key] = val
            except Exception:
                continue

    # Also overlay os.environ
    for k, v in os.environ.items():
        if k in {"FPT_API", "FPT_MODEL", "FPT_BASE_URL", "VERTEX_PROJECT", "VERTEX_LOCATION"}:
            values[k] = v

    return values


@dataclass
class BaselineConfig:
    # Directories
    base_dir: Path = field(default_factory=lambda: HERE)
    contract_path: Path = field(default_factory=lambda: HERE / "evaluation_contract.yaml")
    template_path: Path = field(default_factory=lambda: HERE / "prompt_template.txt")
    output_dir: Path = field(default_factory=lambda: HERE / "output")
    checkpoint_dir: Path = field(default_factory=lambda: HERE / "checkpoints")

    # Dataset default settings
    dataset_name: str = "devign"
    split: str = "test"
    sample_ratio: float = 1.0
    max_targets: Optional[int] = None
    seed: int = 42

    # Retrieval & Reranker settings (GRACE Author baseline)
    candidate_pool_size: int = 50
    semantic_top_k: int = 5
    lexical_weight: float = 0.7  # Author formula: 0.7 * Jaccard_code + 0.3 * Sim_AST
    syntactic_weight: float = 0.3
    whitening_dim: int = 256
    profile: str = "code"  # "code" (CodeT5 + Whitening) or "paper" (CodeT5 + t-SNE)

    # Prompt budget settings (Contract 8192 bytes)
    context_limit_bytes: int = 8192
    graph_nodes_max: int = 40
    graph_edges_max: int = 80
    target_code_max_chars: int = 3000
    standard_demo_max_chars: int = 1500
    contrastive_demo_max_chars: int = 1200
    preserve_prefix: bool = True

    # LLM Backbone settings
    provider: str = "transformers"
    model_name: str = "Qwen/Qwen3-Coder-30B-A3B-Instruct"
    model_revision: str = "b2cff646eb4bb1d68355c01b18ae02e7cf42d120"
    temperature: float = 0.0
    random_seed: int = 42
    max_tokens: int = 256
    thinking_enabled: bool = False  # CRITICAL: Disable thinking to avoid exhausting 256 tokens
    retry_max_attempts: int = 5
    retry_delay_base: float = 5.0
    retry_delay_max: float = 120.0
    use_mock: bool = False

    # Loaded contract data
    contract_data: Dict[str, Any] = field(default_factory=dict)
    env_vars: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Load environment variables
        self.env_vars = load_env_variables()

        # Load contract if exists
        if self.contract_path.is_file():
            try:
                self.contract_data = yaml.safe_load(self.contract_path.read_text(encoding="utf-8"))
                policy = self.contract_data.get("prompt_context_policy", {})
                self.context_limit_bytes = int(policy.get("context_limit", self.context_limit_bytes))
                trunc = policy.get("truncation_policy", {})
                self.graph_nodes_max = int(trunc.get("graph_nodes_max", self.graph_nodes_max))
                self.graph_edges_max = int(trunc.get("graph_edges_max", self.graph_edges_max))
                self.target_code_max_chars = int(trunc.get("target_code_max_chars", self.target_code_max_chars))
                self.standard_demo_max_chars = int(trunc.get("standard_demo_max_chars", self.standard_demo_max_chars))

                inf = self.contract_data.get("inference_config", {})
                self.temperature = float(inf.get("temperature", self.temperature))
                self.random_seed = int(inf.get("seed", self.random_seed))
                self.max_tokens = int(inf.get("max_tokens", self.max_tokens))

                backbone = self.contract_data.get("backbone_llm", {})
                if backbone.get("model"):
                    self.model_name = backbone["model"]
                self.model_revision = backbone.get("revision", self.model_revision)
                self.provider = backbone.get("provider", self.provider)
            except Exception as e:
                print(f"[Config] Warning: Failed to parse evaluation_contract.yaml: {e}")



config = BaselineConfig()
