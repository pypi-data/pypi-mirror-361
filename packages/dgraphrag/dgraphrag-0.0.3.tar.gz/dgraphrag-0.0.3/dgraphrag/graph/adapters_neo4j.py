"""Neo4j graph adapter (minimal) for dgraphrag."""

from __future__ import annotations

from typing import List

from neo4j import GraphDatabase, Driver

from ..core.base import BaseGraphAdapter, Triple
from ..core.exceptions import GraphAdapterError


class Neo4jAdapter(BaseGraphAdapter):
    """Adapter using Neo4j Bolt driver (read/write nodes and relationships)."""

    def __init__(self, uri: str, user: str, password: str) -> None:
        try:
            self.driver: Driver = GraphDatabase.driver(uri, auth=(user, password))
        except Exception as exc:
            raise GraphAdapterError(str(exc)) from exc

    def close(self) -> None:
        self.driver.close()

    def add_triples(self, triples: List[Triple]) -> None:  # noqa: D401
        cypher = (
            "UNWIND $rows AS row "
            "MERGE (s:Entity {name: row.subject}) "
            "MERGE (o:Entity {name: row.object}) "
            "MERGE (s)-[:REL {predicate: row.predicate}]->(o)"
        )
        rows = [triple.__dict__ for triple in triples]
        with self.driver.session() as session:
            session.run(cypher, rows=rows)

    def query_neighbors(self, node: str, depth: int = 1) -> List[Triple]:  # noqa: D401
        query = (
            "MATCH (s:Entity {name: $name})-[r*1..%d]-(o:Entity) "
            "UNWIND r AS rel RETURN DISTINCT s.name AS s, rel.predicate AS p, o.name AS o" % depth
        )
        with self.driver.session() as session:
            result = session.run(query, name=node)
            return [Triple(r["s"], r["p"], r["o"]) for r in result]

    def shortest_path(self, source: str, target: str) -> List[str]:  # noqa: D401
        query = (
            "MATCH (a:Entity {name: $src}), (b:Entity {name: $dst}), "
            "p = shortestPath((a)-[*]-(b)) RETURN nodes(p) AS ns"
        )
        with self.driver.session() as session:
            rec = session.run(query, src=source, dst=target).single()
            if not rec:
                return []
            nodes = rec["ns"]
            return [n["name"] for n in nodes]
