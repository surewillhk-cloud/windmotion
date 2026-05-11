"""Neo4j graph database client."""
import os
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class Neo4jClient:
    """Neo4j client for causal graph operations."""

    def __init__(self, uri: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "windmotion_dev")
        self.driver = None

    async def connect(self):
        try:
            from neo4j import AsyncGraphDatabase
            self.driver = AsyncGraphDatabase.driver(self.uri, auth=(self.user, self.password))
            logger.info("Neo4j connected")
        except ImportError:
            logger.warning("neo4j driver not installed, using mock mode")
        except Exception as e:
            logger.error(f"Neo4j connection failed: {e}")

    async def disconnect(self):
        if self.driver:
            await self.driver.close()

    async def create_graph(self, analysis_id: str, graph_data: Dict) -> str:
        """Create a new causal graph in Neo4j."""
        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])

        async with self.driver.session() as session:
            # Create nodes
            for node in nodes:
                await session.run(
                    """
                    MERGE (n:Node {id: $id, analysis_id: $aid})
                    SET n.name = $name, n.type = $type, n.properties = $props
                    """,
                    id=node.get("id"), aid=analysis_id,
                    name=node.get("name"), type=node.get("type", "factor"),
                    props=node.get("properties", {})
                )

            # Create edges
            for edge in edges:
                await session.run(
                    """
                    MATCH (a:Node {id: $from_id, analysis_id: $aid})
                    MATCH (b:Node {id: $to_id, analysis_id: $aid})
                    MERGE (a)-[r:RELATES {analysis_id: $aid}]->(b)
                    SET r.strength = $strength, r.confidence = $confidence,
                        r.direction = $direction, r.verified = $verified
                    """,
                    from_id=edge.get("from"), to_id=edge.get("to"),
                    aid=analysis_id, strength=edge.get("strength", "medium"),
                    confidence=edge.get("confidence", "medium"),
                    direction=edge.get("direction", "forward"),
                    verified=edge.get("verified", False)
                )

        return analysis_id

    async def get_graph(self, analysis_id: str) -> Dict:
        """Retrieve a causal graph from Neo4j."""
        async with self.driver.session() as session:
            nodes_result = await session.run(
                "MATCH (n:Node {analysis_id: $aid}) RETURN n",
                aid=analysis_id
            )
            nodes = []
            async for record in nodes_result:
                n = record["n"]
                nodes.append({
                    "id": n.get("id"), "name": n.get("name"),
                    "type": n.get("type"), "properties": n.get("properties", {})
                })

            edges_result = await session.run(
                "MATCH (a:Node)-[r:RELATES {analysis_id: $aid}]->(b:Node) RETURN a, r, b",
                aid=analysis_id
            )
            edges = []
            async for record in edges_result:
                r = record["r"]
                edges.append({
                    "from": record["a"].get("id"), "to": record["b"].get("id"),
                    "strength": r.get("strength"), "confidence": r.get("confidence"),
                    "direction": r.get("direction"), "verified": r.get("verified")
                })

        return {"nodes": nodes, "edges": edges}

    async def update_graph(self, analysis_id: str, diff: Dict):
        """Apply diff updates to graph."""
        for node in diff.get("added_nodes", []):
            await self._create_node(analysis_id, node)
        for edge in diff.get("added_edges", []):
            await self._create_edge(analysis_id, edge)
        for update in diff.get("updated_edges", []):
            await self._update_edge(analysis_id, update)

    async def _create_node(self, analysis_id: str, node: Dict):
        async with self.driver.session() as session:
            await session.run(
                "MERGE (n:Node {id: $id, analysis_id: $aid}) SET n += $props",
                id=node.get("id"), aid=analysis_id, props=node
            )

    async def _create_edge(self, analysis_id: str, edge: Dict):
        async with self.driver.session() as session:
            await session.run(
                """
                MATCH (a:Node {id: $from_id, analysis_id: $aid})
                MATCH (b:Node {id: $to_id, analysis_id: $aid})
                MERGE (a)-[r:RELATES]->(b) SET r += $props
                """,
                from_id=edge.get("from"), to_id=edge.get("to"),
                aid=analysis_id, props=edge
            )

    async def _update_edge(self, analysis_id: str, update: Dict):
        async with self.driver.session() as session:
            await session.run(
                """
                MATCH (a:Node {id: $from_id, analysis_id: $aid})
                -[r:RELATES]->(b:Node {id: $to_id, analysis_id: $aid})
                SET r += $props
                """,
                from_id=update.get("from"), to_id=update.get("to"),
                aid=analysis_id, props=update.get("properties", {})
            )

    async def delete_graph(self, analysis_id: str):
        async with self.driver.session() as session:
            await session.run(
                "MATCH (n:Node {analysis_id: $aid}) DETACH DELETE n",
                aid=analysis_id
            )
