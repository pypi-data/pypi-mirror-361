"""Basic graph retriever for dgraphrag MVP."""

from __future__ import annotations

import re
from typing import List

from ..core.base import BaseGraphAdapter


class BasicGraphRetriever:
    """Naive retriever using shortest path and neighbor expansion."""

    def __init__(self, adapter: BaseGraphAdapter) -> None:
        self.adapter = adapter

    @staticmethod
    def _extract_entities(query: str) -> List[str]:
        # very naive capitalized words extraction
        return re.findall(r"[A-Z][a-zA-Z0-9_]+", query)

    def answer(self, query: str) -> str:  # noqa: D401
        entities = self._extract_entities(query)
        if len(entities) < 1:
            return "No entities detected in query."

        focus = None
        for ent in entities:
            if ent in self.adapter.graph:  # type: ignore[attr-defined]
                focus = ent
                break
        if focus is None:
            focus = entities[0]
        neighbors = self.adapter.query_neighbors(focus)
        if not neighbors:
            return f"No knowledge about '{focus}'."

        lines: List[str] = []
        for triple in neighbors:
            lines.append(f"{triple.subject} {triple.predicate} {triple.object}.")

        if len(entities) >= 2:
            target = entities[1]
            path = self.adapter.shortest_path(focus, target)
            if path:
                lines.append(f"Shortest path between {focus} and {target}: {' -> '.join(path)}")

        return "\n".join(lines)
