"""ArangoDB graph adapter for dgraphrag (minimal implementation)."""

from __future__ import annotations

from typing import List

from arango import ArangoClient, Database

from ..core.base import BaseGraphAdapter, Triple
from ..core.exceptions import GraphAdapterError


class ArangoDBAdapter(BaseGraphAdapter):
    """Adapter using python-arango (HTTP) driver."""

    def __init__(self, host: str, username: str, password: str, db_name: str = "_system") -> None:
        try:
            client = ArangoClient(hosts=host)
            self.db: Database = client.db(db_name, username=username, password=password)
            if not self.db.exists_graph("dgraphrag_g"):
                self.db.create_graph("dgraphrag_g")
            self.graph = self.db.graph("dgraphrag_g")
            if "entities" not in self.graph.vertex_collections():
                self.graph.create_vertex_collection("entities")
            if "relations" not in self.graph.edge_definitions():
                self.graph.create_edge_definition(
                    edge_collection="relations",
                    from_vertex_collections=["entities"],
                    to_vertex_collections=["entities"],
                )
        except Exception as exc:  # pragma: no cover
            raise GraphAdapterError(str(exc)) from exc

    def add_triples(self, triples: List[Triple]) -> None:  # noqa: D401
        entities = self.graph.vertex_collection("entities")
        edges = self.graph.edge_collection("relations")
        for t in triples:
            entities.insert({"_key": t.subject, "name": t.subject}, overwrite=True)
            entities.insert({"_key": t.object, "name": t.object}, overwrite=True)
            edges.insert(
                {
                    "_from": f"entities/{t.subject}",
                    "_to": f"entities/{t.object}",
                    "predicate": t.predicate,
                },
                overwrite=True,
            )

    def query_neighbors(self, node: str, depth: int = 1) -> List[Triple]:  # noqa: D401
        aql = (
            "FOR v, e IN 1..%d ANY @start GRAPH 'dgraphrag_g' "
            "RETURN {s: @startKey, p: e.predicate, o: v.name}" % depth
        )
        cursor = self.db.aql.execute(aql, bind_vars={"start": f"entities/{node}", "startKey": node})
        return [Triple(doc["s"], doc["p"], doc["o"]) for doc in cursor]

    def shortest_path(self, source: str, target: str) -> List[str]:  # noqa: D401
        aql = (
            "FOR v IN nodes("  # pragma: no cover
            "    ANY SHORTEST_PATH @src TO @dst GRAPH 'dgraphrag_g'"
            ") RETURN v.name"
        )
        cursor = self.db.aql.execute(
            aql,
            bind_vars={
                "src": f"entities/{source}",
                "dst": f"entities/{target}",
            },
        )
        return list(cursor)
