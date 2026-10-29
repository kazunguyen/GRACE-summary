"""
GRACE Demonstration Retrieval Engine
Implements the author's Hybrid Reranking algorithm:
  Score = 0.7 * Jaccard_Code + 0.3 * Sim_AST
Adheres to the contract's 50-candidate pool and selects the single top-1 demonstration.
"""

from __future__ import annotations

import difflib
import hashlib
from typing import List, Dict, Any, Tuple, Optional
import numpy as np

from embedding_engine import CodeT5Embedder, compute_whitening_kernel, apply_whitening
from graph_extractor import serialize_ast_representation


def jaccard_similarity(code1: str, code2: str) -> float:
    """Whitespace-token Jaccard similarity (matching author's .split() logic)."""
    s1, s2 = set(code1.split()), set(code2.split())
    if not s1 or not s2:
        return 0.0
    return float(len(s1.intersection(s2))) / float(len(s1.union(s2)))


def ast_similarity(ast_str1: str, ast_str2: str) -> float:
    """
    Syntactic similarity between serialized AST representations.
    Uses SequenceMatcher ratio (equivalent to normalized Levenshtein sequence ratio).
    """
    if not ast_str1 or not ast_str2:
        return 0.0
    return difflib.SequenceMatcher(None, ast_str1.split(), ast_str2.split()).ratio()


def compute_hybrid_score(
    query_code: str,
    query_ast: str,
    cand_code: str,
    cand_ast: str,
    lexical_weight: float = 0.7,
    syntactic_weight: float = 0.3,
) -> Tuple[float, float, float]:
    """
    Author's formula: Score = 0.7 * Jaccard + 0.3 * Sim_AST
    Returns: (hybrid_score, jaccard_score, ast_score)
    """
    j_score = jaccard_similarity(query_code, cand_code)
    a_score = ast_similarity(query_ast, cand_ast)
    hybrid_score = (lexical_weight * j_score) + (syntactic_weight * a_score)
    return hybrid_score, j_score, a_score


class DemonstrationRetriever:
    """
    Hybrid Demonstration Retrieval for GRACE:
    Phase 1: Semantic search via Whitened CodeT5 (or t-SNE) -> top 50 candidates from train pool
             (excluding exact duplicate target code to avoid data leakage)
             -> top K (default 5) semantic candidates
    Phase 2: Hybrid Reranking (0.7 code Jaccard + 0.3 AST) -> top 1 demonstration
    """
    def __init__(
        self,
        embedder: Optional[CodeT5Embedder] = None,
        profile: str = "code",
        candidate_pool_size: int = 50,
        semantic_top_k: int = 5,
        whitening_dim: int = 256,
        lexical_weight: float = 0.7,
        syntactic_weight: float = 0.3,
    ):
        self.embedder = embedder or CodeT5Embedder(force_fallback=False)
        self.profile = profile
        self.candidate_pool_size = candidate_pool_size
        self.semantic_top_k = semantic_top_k
        self.whitening_dim = whitening_dim
        self.lexical_weight = lexical_weight
        self.syntactic_weight = syntactic_weight

        self.train_samples: List[Dict[str, Any]] = []
        self.train_code_hashes: List[str] = []
        self.train_vecs: Optional[np.ndarray] = None
        self.mu: Optional[np.ndarray] = None
        self.w: Optional[np.ndarray] = None
        self.tsne_projector: Any = None

    def fit(self, train_samples: List[Dict[str, Any]]) -> None:
        """Fit embeddings and dimension reduction on train set."""
        self.train_samples = train_samples
        train_codes = [s["func"] for s in train_samples]
        self.train_code_hashes = [
            hashlib.sha256(c.encode("utf-8")).hexdigest()
            for c in train_codes
        ]

        raw_vecs = self.embedder.encode(train_codes)
        if self.profile == "code":
            dim = min(self.whitening_dim, raw_vecs.shape[1], max(2, len(train_samples) - 1))
            self.mu, self.w = compute_whitening_kernel(raw_vecs, target_dim=dim)
            self.train_vecs = apply_whitening(raw_vecs, self.mu, self.w)
        else:
            # Paper profile: t-SNE 2D with KNN out-of-sample regressor
            from sklearn.manifold import TSNE
            from sklearn.neighbors import KNeighborsRegressor
            n_samples = len(train_samples)
            perplexity = min(30, max(2, n_samples // 3))
            tsne = TSNE(n_components=2, perplexity=perplexity, random_state=42)
            self.train_vecs = tsne.fit_transform(raw_vecs)

            # Fit out-of-sample projector for unseen queries
            self.tsne_projector = KNeighborsRegressor(n_neighbors=min(5, max(1, n_samples)))
            self.tsne_projector.fit(raw_vecs, self.train_vecs)

    def retrieve_single(
        self,
        target_sample: Dict[str, Any],
        candidate_indices: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve the single best demonstration for a given query sample.
        - Excludes exact duplicate code from the candidate pool to prevent leakage.
        - If candidate_indices is None, selects top 50 semantic candidates from the full train set.
        - Slices top 5 semantic candidates, then applies hybrid reranking (0.7 Jaccard + 0.3 AST).
        """
        if not self.train_samples:
            raise RuntimeError("Retriever must be fitted on train set first.")

        query_code = target_sample["func"]
        query_hash = hashlib.sha256(query_code.encode("utf-8")).hexdigest()
        query_ast = serialize_ast_representation(target_sample.get("nodes", []), target_sample.get("edges", []))

        # 1. Determine valid candidate indices (excluding identical code duplicate)
        if candidate_indices is not None:
            valid_pool_idx = [i for i in candidate_indices if self.train_code_hashes[i] != query_hash]
            if not valid_pool_idx:
                # If all candidates in custom pool matched query, fall back to any other train index
                valid_pool_idx = [i for i in range(len(self.train_samples)) if self.train_code_hashes[i] != query_hash]
        else:
            valid_pool_idx = [i for i in range(len(self.train_samples)) if self.train_code_hashes[i] != query_hash]

        if not valid_pool_idx:
            # If train contains only copies of this code, use candidate 0 as absolute fallback
            valid_pool_idx = [0]

        # 2. Semantic search to get Top 50 initial pool (and then Top 5 for hybrid reranking)
        pool_vecs = self.train_vecs[valid_pool_idx]
        query_raw = self.embedder.encode([query_code])

        if self.profile == "code":
            query_vec = apply_whitening(query_raw, self.mu, self.w)
            sims = np.dot(pool_vecs, query_vec.T).reshape(-1)
        else:
            query_2d = self.tsne_projector.predict(query_raw)
            diffs = pool_vecs - query_2d
            sims = -np.linalg.norm(diffs, axis=1)

        # Sort candidate indices by semantic score descending
        sorted_rel_order = np.argsort(-sims)
        # Top 50 candidates (candidate_pool_size)
        pool_size = min(self.candidate_pool_size, len(sorted_rel_order))
        top_50_cand_idx = [valid_pool_idx[sorted_rel_order[i]] for i in range(pool_size)]

        # Top K semantic candidates (default 5) within the 50 candidate pool
        top_k = min(self.semantic_top_k, len(top_50_cand_idx))
        top_k_cand_idx = top_50_cand_idx[:top_k]

        # 3. Hybrid Reranking on the top K semantic candidates
        best_demo = None
        best_hybrid_score = -1.0
        best_meta = {}

        for train_idx in top_k_cand_idx:
            cand = self.train_samples[train_idx]
            cand_code = cand["func"]
            cand_ast = serialize_ast_representation(cand.get("nodes", []), cand.get("edges", []))

            hybrid, jacc, ast_s = compute_hybrid_score(
                query_code, query_ast, cand_code, cand_ast,
                lexical_weight=self.lexical_weight,
                syntactic_weight=self.syntactic_weight,
            )

            if hybrid > best_hybrid_score:
                best_hybrid_score = hybrid
                best_demo = cand
                best_meta = {
                    "hybrid_score": float(hybrid),
                    "jaccard_code": float(jacc),
                    "ast_similarity": float(ast_s),
                    "demo_id": cand.get("id"),
                    "demo_label": int(cand.get("target", 0)),
                    "candidate_pool_size_used": len(top_50_cand_idx),
                }

        return {
            "demo": best_demo,
            "metadata": best_meta,
            "initial_candidate_ids": [self.train_samples[i].get("id") for i in top_50_cand_idx],
        }
