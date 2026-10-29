"""
GRACE Embedding & Dimension Reduction Engine
Implements CodeT5 feature extraction with BERT-Whitening (Author Code-based)
and t-SNE projection (Author Paper-based).
Includes offline/CPU fallback for fast testing.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)


def compute_whitening_kernel(vecs: np.ndarray, target_dim: int = 256) -> Tuple[np.ndarray, np.ndarray]:
    """
    Fit BERT-Whitening on training set embeddings.
    Reference: Su et al. (Whitening BERT / Author's bert_whitening.py).
    """
    mu = np.mean(vecs, axis=0, keepdims=True)
    cov = np.cov(vecs - mu, rowvar=False)
    u, s, _ = np.linalg.svd(cov)
    # Numerical stability epsilon
    s_inv_sqrt = 1.0 / np.sqrt(s + 1e-12)
    w = np.dot(u, np.diag(s_inv_sqrt))[:, :target_dim]
    return mu, w


def apply_whitening(vecs: np.ndarray, mu: np.ndarray, w: np.ndarray) -> np.ndarray:
    """Project and L2-normalize vectors."""
    projected = np.dot(vecs - mu, w)
    norms = np.linalg.norm(projected, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1e-12, norms)
    return projected / norms


class CodeT5Embedder:
    """
    Extracts semantic code embeddings using CodeT5-base (768d).
    Falls back to TF-IDF + SVD if transformers or GPU weights are unavailable.
    """
    def __init__(self, model_name: str = "Salesforce/codet5-base", force_fallback: bool = False):
        self.model_name = model_name
        self.force_fallback = force_fallback
        self.is_fallback = force_fallback
        self.tokenizer = None
        self.model = None
        self.device = "cpu"
        self._fallback_vectorizer = None

        if not force_fallback:
            import torch
            from transformers import RobertaTokenizer, T5EncoderModel

            revision = "02cd2d31bb7c6d0e4d91156167b2de044989c733"
            if model_name != "Salesforce/codet5-base":
                raise ValueError("Baseline requires the pinned CodeT5 model")
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.tokenizer = RobertaTokenizer.from_pretrained(model_name, revision=revision)
            self.model = T5EncoderModel.from_pretrained(model_name, revision=revision).to(self.device)
            self.model.eval()

    def encode(self, code_snippets: List[str], batch_size: int = 32) -> np.ndarray:
        """Encode list of code snippets into 768d vectors."""
        if not code_snippets:
            return np.empty((0, 768), dtype=np.float32)

        if self.is_fallback:
            return self._encode_fallback(code_snippets)

        import torch
        all_vecs = []
        for i in range(0, len(code_snippets), batch_size):
            batch = code_snippets[i : i + batch_size]
            inputs = self.tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs)
                # Masked mean pooling across non-padding tokens
                attention_mask = inputs["attention_mask"].unsqueeze(-1)
                hidden_states = outputs.last_hidden_state * attention_mask
                sum_hidden = torch.sum(hidden_states, dim=1)
                sum_mask = torch.clamp(attention_mask.sum(dim=1), min=1e-9)
                mean_pooled = sum_hidden / sum_mask
                all_vecs.append(mean_pooled.cpu().numpy().astype(np.float32))

        return np.concatenate(all_vecs, axis=0)

    def _encode_fallback(self, code_snippets: List[str]) -> np.ndarray:
        """TF-IDF + SVD fallback for offline / lightweight dry-runs."""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.decomposition import TruncatedSVD

        if self._fallback_vectorizer is None:
            self._fallback_vectorizer = TfidfVectorizer(max_features=2048, token_pattern=r"\S+")
            tfidf_mat = self._fallback_vectorizer.fit_transform(code_snippets)
            n_components = min(768, tfidf_mat.shape[1], max(2, len(code_snippets) - 1))
            self._svd = TruncatedSVD(n_components=n_components, random_state=42)
            reduced = self._svd.fit_transform(tfidf_mat)
        else:
            tfidf_mat = self._fallback_vectorizer.transform(code_snippets)
            reduced = self._svd.transform(tfidf_mat)

        if reduced.shape[1] < 768:
            padded = np.zeros((reduced.shape[0], 768), dtype=np.float32)
            padded[:, : reduced.shape[1]] = reduced
            return padded
        return reduced.astype(np.float32)
