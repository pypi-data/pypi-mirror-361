"""TigerGraph graph adapter for dgraphrag (minimal)."""

from __future__ import annotations

from typing import List

from pyTigerGraph import TigerGraphConnection

from ..core.base import BaseGraphAdapter, Triple
from ..core.exceptions import GraphAdapterError


class TigerGraphAdapter(BaseGraphAdapter):
    """Adapter using pyTigerGraph REST interface."""

    def __init__(
        self,
        host: str,
        graphname: str,
        username: str,
        password: str,
        secret: str | None = None,
    ) -> None:
        try:
            self.conn = TigerGraphConnection(host=host, graphname=graphname, username=username, password=password)
            if secret:
                self.conn.getToken(secret)
        except Exception as exc:  # pragma: no cover
            raise GraphAdapterError(str(exc)) from exc

    # TigerGraph schema assumed: vertex type Entity(primary_id name STRING), edge type REL(FROM Entity, TO Entity, predicate STRING)

    def add_triples(self, triples: List[Triple]) -> None:  # noqa: D401
        data = [
            {
                "vertices": {
                    "Entity": {
                        t.subject: {"name": t.subject},
                        t.object: {"name": t.object},
                    }
                },
                "edges": {
                    "Entity": {
                        t.subject: {
                            "REL": {
                                "Entity": {
                                    t.object: {"predicate": t.predicate}
                                }
                            }
                        }
                    }
                },
            }
            for t in triples
        ]
        for payload in data:
            self.conn.upsertGraphData(payload)

    def query_neighbors(self, node: str, depth: int = 1) -> List[Triple]:  # noqa: D401
        query = f"INTERPRET QUERY () FOR GRAPH {self.conn.graphname} {{ Start = {{Entity.{node}}}; Result = SELECT v FROM Start:(s)- (REL:e)- :Entity:v LIMIT 100; PRINT Result; }}"
        res = self.conn.interpretQuery(query)
        triples: List[Triple] = []
        for item in res[0].get("Result", []):
            subj = item["s"]["attributes"]["name"]
            obj = item["v"]["attributes"]["name"]
            pred = item["e"]["attributes"].get("predicate", "REL")
            triples.append(Triple(subj, pred, obj))
        return triples

    def shortest_path(self, source: str, target: str) -> List[str]:  # noqa: D401
        query = (
            f"INTERPRET QUERY () FOR GRAPH {self.conn.graphname} {{ "
            "Result = SELECT shortest_path({source}, {target}); PRINT Result; }}"
        )
        try:
            res = self.conn.interpretQuery(query)
            path = res[0]["Result"][0]["ShortestPath"]  # list of vertex IDs
            return path
        except Exception:  # pragma: no cover
            return []
