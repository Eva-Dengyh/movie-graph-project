import os
from typing import Any

try:
    from neo4j import GraphDatabase
except ImportError:  # JSON mode remains available for local previews.
    GraphDatabase = None

class Neo4jStore:
    def __init__(self) -> None:
        self.uri = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
        self.user = os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "moviegraphdev")
        self.driver = None
        if GraphDatabase:
            try:
                driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
                driver.verify_connectivity()
                self.driver = driver
            except Exception:
                self.driver = None

    @property
    def available(self) -> bool:
        return self.driver is not None

    def run(self, cypher: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        if not self.driver:
            return []
        with self.driver.session() as session:
            return [record.data() for record in session.run(cypher, **params)]
