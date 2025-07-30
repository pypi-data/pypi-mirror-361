"""In-memory graph adapter using NetworkX or fallback."""

from __future__ import annotations

from typing import List

try:
    import networkx as nx
except ImportError:  # pragma: no cover
    nx = None  # type: ignore

from ..core.base import BaseGraphAdapter, Triple
from ..core.exceptions import GraphAdapterError


class InMemoryGraphAdapter(BaseGraphAdapter):
    """Graph adapter backed by a NetworkX directed multigraph."""

    def __init__(self) -> None:
        if nx is None:
            raise GraphAdapterError(
                "networkx is required for InMemoryGraphAdapter. Install via 'pip install networkx'."
            )
        self.graph = nx.MultiDiGraph()

    def add_triples(self, triples: List[Triple]) -> None:  # noqa: D401
        for triple in triples:
            self.graph.add_node(triple.subject)
            self.graph.add_node(triple.object)
            self.graph.add_edge(triple.subject, triple.object, predicate=triple.predicate)

    def query_neighbors(self, node: str, depth: int = 1) -> List[Triple]:  # noqa: D401
        if node not in self.graph:
            return []
        neighbors = set()
        for dst in self.graph.successors(node):
            neighbors.add((node, dst))
        for src in self.graph.predecessors(node):
            neighbors.add((src, node))
        triples: List[Triple] = []
        for subj, obj in neighbors:
            edge_dict = self.graph.get_edge_data(subj, obj, default={})
            for key, data in edge_dict.items():
                triples.append(Triple(subj, data.get("predicate", ""), obj))
        return triples

    def shortest_path(self, source: str, target: str) -> List[str]:  # noqa: D401
        try:
            path = nx.shortest_path(self.graph.to_undirected(), source, target)
            return path
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []
