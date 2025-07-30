"""Vector indexers (Faiss) for dgraphrag."""

from __future__ import annotations

from typing import List, Tuple

try:
    import faiss  # type: ignore
except ImportError:  # pragma: no cover
    faiss = None  # type: ignore

from ..core.exceptions import GraphAdapterError


class FaissIndexer:
    """Simple in-memory Faiss L2 index over node embeddings."""

    def __init__(self, dim: int) -> None:
        if faiss is None:
            raise GraphAdapterError("Faiss is not installed. Run pip install dgraphrag[vector]")
        self.index = faiss.IndexFlatL2(dim)
        self.vectors: List[str] = []  # keep node names in same order
        self.dim = dim

    def add(self, node: str, vec: List[float]) -> None:
        if len(vec) != self.dim:
            raise ValueError("Embedding dimension mismatch")
        import numpy as np

        self.index.add(np.array([vec], dtype="float32"))
        self.vectors.append(node)

    def query(self, vec: List[float], k: int = 5) -> List[Tuple[str, float]]:
        import numpy as np

        distances, indices = self.index.search(np.array([vec], dtype="float32"), k)
        res: List[Tuple[str, float]] = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.vectors):
                res.append((self.vectors[idx], float(dist)))
        return res
