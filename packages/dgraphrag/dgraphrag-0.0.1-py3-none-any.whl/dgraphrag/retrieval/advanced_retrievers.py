"""Additional retrievers: PathRetriever, VectorSimilarityRetriever."""

from __future__ import annotations

from typing import List

from ..core.base import BaseGraphAdapter, Triple
from ..graph.indexers import FaissIndexer


class PathRetriever:
    """Retrieve all simple paths up to max_hops between head and tail entities."""

    def __init__(self, adapter: BaseGraphAdapter, max_hops: int = 3) -> None:
        self.adapter = adapter
        self.max_hops = max_hops

    def paths(self, source: str, target: str) -> List[List[str]]:  # noqa: D401
        # Only works for InMemoryGraphAdapter where graph attr exists
        if not hasattr(self.adapter, "graph"):
            return []
        import networkx as nx

        g = self.adapter.graph.to_undirected()
        try:
            return list(nx.all_simple_paths(g, source=source, target=target, cutoff=self.max_hops))
        except (nx.NodeNotFound, nx.NetworkXNoPath):
            return []


class VectorSimilarityRetriever:
    """Retrieve top-k similar nodes via FaissIndexer and return neighbor triples."""

    def __init__(self, adapter: BaseGraphAdapter, indexer: FaissIndexer, embed_fn) -> None:
        self.adapter = adapter
        self.indexer = indexer
        self.embed_fn = embed_fn  # function str -> List[float]

    def query(self, text: str, k: int = 5) -> List[Triple]:  # noqa: D401
        vec = self.embed_fn(text)
        nodes = self.indexer.query(vec, k)
        triples: List[Triple] = []
        for node, _ in nodes:
            triples.extend(self.adapter.query_neighbors(node))
        return triples
