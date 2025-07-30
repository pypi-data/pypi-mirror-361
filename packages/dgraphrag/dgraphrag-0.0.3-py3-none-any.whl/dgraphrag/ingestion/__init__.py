"""Ingestion subpackage exposes loaders, splitters, and extractors."""

from .loaders import LocalTextLoader
from .splitters import SimpleParagraphSplitter
from .extractors import RegexExtractor

__all__ = [
    "LocalTextLoader",
    "SimpleParagraphSplitter",
    "RegexExtractor",
]
