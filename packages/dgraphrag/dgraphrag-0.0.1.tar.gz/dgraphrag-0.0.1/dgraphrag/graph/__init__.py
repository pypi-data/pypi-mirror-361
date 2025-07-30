"""Graph subpackage for dgraphrag MVP."""

from .adapters import InMemoryGraphAdapter
from .adapters_neo4j import Neo4jAdapter
try:
    from .adapters_arangodb import ArangoDBAdapter  # optional
except ImportError:  # pragma: no cover
    ArangoDBAdapter = None  # type: ignore
try:
    from .adapters_tigergraph import TigerGraphAdapter  # optional
except ImportError:  # pragma: no cover
    TigerGraphAdapter = None  # type: ignore
from .builders import SimpleGraphBuilder

__all__ = [
    "InMemoryGraphAdapter",
    "Neo4jAdapter",
    "ArangoDBAdapter",
    "TigerGraphAdapter",
    "SimpleGraphBuilder",
]
