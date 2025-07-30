"""Graph builders for dgraphrag MVP."""

from __future__ import annotations

from typing import List

from ..core.base import Triple, BaseGraphAdapter


class SimpleGraphBuilder:
    """Inserts triples into a graph adapter."""

    def __init__(self, adapter: BaseGraphAdapter) -> None:
        self.adapter = adapter

    def build(self, triples: List[Triple]) -> None:  # noqa: D401
        if not triples:
            return
        self.adapter.add_triples(triples)
