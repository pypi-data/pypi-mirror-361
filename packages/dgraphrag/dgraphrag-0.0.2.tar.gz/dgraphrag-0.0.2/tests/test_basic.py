"""Basic unit tests for dgraphrag MVP."""

from pathlib import Path

from dgraphrag import (
    LocalTextLoader,
    SimpleParagraphSplitter,
    RegexExtractor,
    InMemoryGraphAdapter,
    SimpleGraphBuilder,
    BasicGraphRetriever,
)


def _prepare_demo(tmp_path: Path) -> Path:
    demo_file = tmp_path / "demo.txt"
    demo_file.write_text(
        "GraphRAG is RetrievalAugmentedGeneration.\n\nRetrievalAugmentedGeneration is Powerful."
    )
    return demo_file


def test_full_pipeline(tmp_path):
    demo = _prepare_demo(tmp_path)

    loader = LocalTextLoader()
    text = loader.load(demo)
    paragraphs = SimpleParagraphSplitter().split(text)
    triples = RegexExtractor().extract(paragraphs)
    assert len(triples) == 2

    adapter = InMemoryGraphAdapter()
    SimpleGraphBuilder(adapter).build(triples)
    assert adapter.graph.number_of_nodes() == 3

    retriever = BasicGraphRetriever(adapter)
    answer = retriever.answer("What is GraphRAG?")
    assert "GraphRAG is RetrievalAugmentedGeneration." in answer
