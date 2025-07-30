"""Command-line interface for dgraphrag.

Usage::

    dgrag ingest <path>
    dgrag ask "<question>"
    dgrag graph-info

This CLI intentionally keeps zero external deps beyond click- or argparse-like stdlib.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

from . import (
    LocalTextLoader,
    SimpleParagraphSplitter,
    RegexExtractor,
    InMemoryGraphAdapter,
    SimpleGraphBuilder,
    BasicGraphRetriever,
)

_STATE_FILE = Path.home() / ".dgraphrag" / "state.json"


class StateStore:  # very lightweight local cache
    def __init__(self, path: Path = _STATE_FILE) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            self._data = json.loads(self.path.read_text())
        else:
            self._data = {"files": {}}

    def is_unchanged(self, filepath: Path) -> bool:
        cached = self._data["files"].get(str(filepath))
        return cached == self._hash(filepath)

    def update(self, filepath: Path) -> None:
        self._data["files"][str(filepath)] = self._hash(filepath)
        self.flush()

    def flush(self) -> None:
        self.path.write_text(json.dumps(self._data, indent=2))

    @staticmethod
    def _hash(filepath: Path) -> str:
        import hashlib

        h = hashlib.sha256()
        h.update(filepath.read_bytes())
        return h.hexdigest()


def _ingest(path: str) -> None:
    target = Path(path)
    if not target.exists():
        print(f"[Error] Path not found: {target}")
        sys.exit(1)

    loader = LocalTextLoader()
    splitter = SimpleParagraphSplitter()
    extractor = RegexExtractor()
    adapter = InMemoryGraphAdapter()
    builder = SimpleGraphBuilder(adapter)
    state = StateStore()

    files: List[Path]
    if target.is_dir():
        files = list(target.rglob("*.txt")) + list(target.rglob("*.md")) + list(target.rglob("*.html"))
    else:
        files = [target]

    for file in files:
        if state.is_unchanged(file):
            print(f"[Skip] {file}")
            continue
        print(f"[Load] {file}")
        text = loader.load(file)
        paragraphs = splitter.split(text)
        triples = extractor.extract(paragraphs)
        builder.build(triples)
        state.update(file)
        print(f"[Graph] Added {len(triples)} triples from {file}")

    print("[Done] Ingestion completed.")


def _ask(question: str) -> None:
    adapter = InMemoryGraphAdapter()
    retriever = BasicGraphRetriever(adapter)
    print(retriever.answer(question))


def _graph_info() -> None:
    adapter = InMemoryGraphAdapter()
    g = adapter.graph
    print(f"Nodes: {g.number_of_nodes()}, Edges: {g.number_of_edges()}")
    out = Path("graph.graphml")
    import networkx as nx

    nx.write_graphml(g, out)
    print(f"GraphML exported to {out.resolve()}")


def main() -> None:  # noqa: D401
    parser = argparse.ArgumentParser(description="dgraphrag CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    ingest_p = sub.add_parser("ingest", help="Ingest files or directory")
    ingest_p.add_argument("path")

    ask_p = sub.add_parser("ask", help="Ask a question")
    ask_p.add_argument("question")

    sub.add_parser("graph-info", help="Show graph statistics")

    args = parser.parse_args()

    if args.command == "ingest":
        _ingest(args.path)
    elif args.command == "ask":
        _ask(args.question)
    elif args.command == "graph-info":
        _graph_info()
    else:
        parser.print_help()


if __name__ == "__main__":  # pragma: no cover
    main()
