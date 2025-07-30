"""Tests for advanced retrievers."""

import pytest

from dgraphrag.core.base import Triple
from dgraphrag.graph import InMemoryGraphAdapter
from dgraphrag.retrieval import PathRetriever, VectorSimilarityRetriever


def _setup_simple_graph():
    adapter = InMemoryGraphAdapter()
    adapter.add_triples([
        Triple("A", "rel", "B"),
        Triple("B", "rel", "C"),
    ])
    return adapter


def test_path_retriever():
    pytest.importorskip("networkx")
    adapter = _setup_simple_graph()
    pr = PathRetriever(adapter, max_hops=2)
    paths = pr.paths("A", "C")
    assert ["A", "B", "C"] in paths


import os

@pytest.mark.skip(reason="Faiss may crash in some environments")
def test_vector_similarity_retriever():
    faiss = pytest.importorskip("faiss")
    from dgraphrag.graph.indexers import FaissIndexer

    adapter = _setup_simple_graph()
    indexer = FaissIndexer(2)
    indexer.add("A", [1.0, 0.0])
    indexer.add("B", [0.5, 0.5])
    indexer.add("C", [0.0, 1.0])

    def embed(text: str):  # very dummy embed
        mapping = {"foo": [1.0, 0.1], "bar": [0.0, 0.9]}
        return mapping.get(text, [0.0, 0.0])

    vr = VectorSimilarityRetriever(adapter, indexer, embed)
    triples = vr.query("foo", k=2)
    assert any(t.subject == "A" for t in triples)
