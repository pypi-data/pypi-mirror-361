"""Top-level package for dgraphrag MVP."""

from .ingestion.loaders import LocalTextLoader
from .ingestion.splitters import SimpleParagraphSplitter
from .ingestion.extractors import RegexExtractor
from .graph.adapters import InMemoryGraphAdapter
from .graph.builders import SimpleGraphBuilder
from .retrieval.graph_retrievers import BasicGraphRetriever

__all__ = [
    "LocalTextLoader",
    "SimpleParagraphSplitter",
    "RegexExtractor",
    "InMemoryGraphAdapter",
    "SimpleGraphBuilder",
    "BasicGraphRetriever",
]
