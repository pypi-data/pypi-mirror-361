# dgraphrag

Minimal Viable Product (MVP) implementation of a GraphRAG toolkit for Python.

## Installation
```bash
pip install dgraphrag[arangodb,tigergraph,vector]
# 或者开发模式
pip install -e .[arangodb,tigergraph,vector]
```

## Quick Start
```python
from pathlib import Path

from dgraphrag import (
    LocalTextLoader,
    SimpleParagraphSplitter,
    RegexExtractor,
    InMemoryGraphAdapter,
    SimpleGraphBuilder,
    BasicGraphRetriever,
)

# create a small demo file
Path("demo.txt").write_text("GraphRAG is RetrievalAugmentedGeneration.\n\nRetrievalAugmentedGeneration is Powerful.")

loader = LocalTextLoader()
text = loader.load("demo.txt")

paragraphs = SimpleParagraphSplitter().split(text)
triples = RegexExtractor().extract(paragraphs)

adapter = InMemoryGraphAdapter()
SimpleGraphBuilder(adapter).build(triples)

retriever = BasicGraphRetriever(adapter)
print(retriever.answer("What is GraphRAG?"))
```
