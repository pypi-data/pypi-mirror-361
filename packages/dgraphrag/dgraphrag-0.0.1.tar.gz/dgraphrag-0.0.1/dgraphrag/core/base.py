"""Base classes and core dataclasses for dgraphrag MVP."""

from __future__ import annotations

import abc
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class Triple:
    """Simple representation of a (subject, predicate, object) triple."""

    subject: str
    predicate: str
    object: str

    def as_tuple(self) -> tuple[str, str, str]:
        """Return triple as tuple."""
        return self.subject, self.predicate, self.object


class BaseLoader(abc.ABC):
    """Abstract base class for document loaders."""

    @abc.abstractmethod
    def load(self, path: str | Path) -> str:  # noqa: D401
        """Load file content and return as string."""


class BaseSplitter(abc.ABC):
    """Abstract base class for text splitters."""

    @abc.abstractmethod
    def split(self, text: str) -> List[str]:
        """Split text into smaller chunks."""


class BaseExtractor(abc.ABC):
    """Abstract base class for entity/relationship extractors."""

    @abc.abstractmethod
    def extract(self, chunks: List[str]) -> List[Triple]:
        """Extract triples from text chunks."""


class BaseGraphAdapter(abc.ABC):
    """Abstract base class for graph database adapters."""

    @abc.abstractmethod
    def add_triples(self, triples: List[Triple]) -> None:
        """Insert triples into the graph storage."""

    @abc.abstractmethod
    def query_neighbors(self, node: str, depth: int = 1) -> List[Triple]:
        """Return triples within *depth* hops of *node*."""

    @abc.abstractmethod
    def shortest_path(self, source: str, target: str) -> List[str]:
        """Return list of node names from *source* to *target*."""
