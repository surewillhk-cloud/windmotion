"""Neo4j graph database client with typed nodes and relationships."""
import os
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# Node types per design doc §15
NODE_TYPES = {
    "factor": "Factor",       # name / category / score(0-5) / confidence / description
    "variable": "Variable",   # name / category / current_value / trend
    "event": "Event",         # name / event_type / timestamp / description
    "decision": "Decision",   # name / timestamp / inferred_logic / factor_scores
    "result": "Result",       # name / profit / roi / holding_days
}

# Relationship types per design doc §15
REL_TYPES = {
    "influences": "INFLUENCES",             # Factor/Variable → Decision: strength / confidence / direction / verified
    "triggered_by": "TRIGGERED_BY",         # Event → Decision: directness
    "leads_to": "LEADS_TO",                 # Decision → Result: impact
    "correlates": "CORRELATES",             # Variable ↔ Variable: correlation_type / strength
    "temporal_sequence": "TEMPORAL_SEQUENCE", # Event→Event / Decision→Decision: time_delta
}


class Neo4jClient:
    """Neo4j client for causal graph operations with typed nodes and relationships."""

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

    def _get_node_label(self, node_type: str) -> str:
        """Get Neo4j label for node type. Falls back to generic 'Node'."""
        return NODE_TYPES.get(node_type, "Node")

    def _get_rel_type(self, rel_kind: str) -> str:
        """Get Neo4j relationship type. Falls back to 'RELATES'."""
        return REL_TYPES.get(rel_kind, "RELATES")

    async def create_graph(self, analysis_id: str, graph_data: Dict) -> str:
        """Create a new causal graph in Neo4j with typed nodes and relationships."""
        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])

        async with self.driver.session() as session:
            # Create nodes with specific labels (Factor/Variable/Event/Decision/Result)
            for node in nodes:
                node_type = node.get("type", "factor")
                label = self._get_node_label(node_type)
                # Use dynamic label via APOC or parameterized Cypher
                # Since dynamic labels aren't natively supported in Cypher params,
                # we store type as property AND use specific labels via string formatting
                query = f"""
                    MERGE (n:{label} {{id: $id, analysis_id: $aid}})
                    SET n.name = $name, n.type = $type, n += $props
                """
                props = node.get("properties", {})
                # Add type-specific properties
                if node_type == "factor":
                    props.setdefault("score", node.get("score", 0))
                    props.setdefault("confidence", node.get("confidence", "medium"))
                    props.setdefault("category", node.get("category", ""))
                elif node_type == "variable":
                    props.setdefault("current_value", node.get("current_value", ""))
                    props.setdefault("trend", node.get("trend", ""))
                elif node_type == "event":
                    props.setdefault("event_type", node.get("event_type", ""))
                    props.setdefault("timestamp", node.get("timestamp", ""))
                elif node_type == "decision":
                    props.setdefault("inferred_logic", node.get("inferred_logic", ""))
                    props.setdefault("factor_scores", node.get("factor_scores", {}))
                elif node_type == "result":
                    props.setdefault("profit", node.get("profit", 0))
                    props.setdefault("roi", node.get("roi", 0))
                    props.setdefault("holding_days", node.get("holding_days", 0))

                await session.run(query,
                    id=node.get("id"), aid=analysis_id,
                    name=node.get("name"), type=node_type, props=props
                )

            # Create typed relationships
            for edge in edges:
                rel_kind = edge.get("rel_type", "influences")
                rel_label = self._get_rel_type(rel_kind)
                from_type = edge.get("from_type", "Factor")
                to_type = edge.get("to_type", "Decision")

                query = f"""
                    MATCH (a {{id: $from_id, analysis_id: $aid}})
                    MATCH (b {{id: $to_id, analysis_id: $aid}})
                    MERGE (a)-[r:{rel_label} {{analysis_id: $aid}}]->(b)
                    SET r.strength = $strength, r.confidence = $confidence,
                        r.direction = $direction, r.verified = $verified,
                        r += $extra_props
                """
                extra_props = {}
                if rel_kind == "triggered_by":
                    extra_props["directness"] = edge.get("directness", "direct")
                elif rel_kind == "leads_to":
                    extra_props["impact"] = edge.get("impact", "medium")
                elif rel_kind == "correlates":
                    extra_props["correlation_type"] = edge.get("correlation_type", "positive")
                elif rel_kind == "temporal_sequence":
                    extra_props["time_delta"] = edge.get("time_delta", "")

                await session.run(query,
                    from_id=edge.get("from"), to_id=edge.get("to"),
                    aid=analysis_id, strength=edge.get("strength", "medium"),
                    confidence=edge.get("confidence", "medium"),
                    direction=edge.get("direction", "forward"),
                    verified=edge.get("verified", False),
                    extra_props=extra_props
                )

        return analysis_id

    async def get_graph(self, analysis_id: str) -> Dict:
        """Retrieve a causal graph from Neo4j with typed nodes and relationships."""
        async with self.driver.session() as session:
            # Get all nodes (across all type labels)
            nodes = []
            for label in NODE_TYPES.values():
                result = await session.run(
                    f"MATCH (n:{label} {{analysis_id: $aid}}) RETURN n, '{label}' as label",
                    aid=analysis_id
                )
                async for record in result:
                    n = record["n"]
                    nodes.append({
                        "id": n.get("id"), "name": n.get("name"),
                        "type": n.get("type"), "properties": dict(n),
                        "label": record["label"]
                    })

            # Get all typed relationships
            edges = []
            for rel_type in REL_TYPES.values():
                result = await session.run(
                    f"MATCH (a)-[r:{rel_type} {{analysis_id: $aid}}]->(b) "
                    f"RETURN a.id as from_id, b.id as to_id, r, '{rel_type}' as rel_label",
                    aid=analysis_id
                )
                async for record in result:
                    r = record["r"]
                    edges.append({
                        "from": record["from_id"], "to": record["to_id"],
                        "strength": r.get("strength"), "confidence": r.get("confidence"),
                        "direction": r.get("direction"), "verified": r.get("verified"),
                        "rel_type": record["rel_label"],
                        "properties": dict(r)
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
        node_type = node.get("type", "factor")
        label = self._get_node_label(node_type)
        async with self.driver.session() as session:
            await session.run(
                f"MERGE (n:{label} {{id: $id, analysis_id: $aid}}) SET n += $props",
                id=node.get("id"), aid=analysis_id, props=node
            )

    async def _create_edge(self, analysis_id: str, edge: Dict):
        rel_kind = edge.get("rel_type", "influences")
        rel_label = self._get_rel_type(rel_kind)
        async with self.driver.session() as session:
            await session.run(
                f"""
                MATCH (a {{id: $from_id, analysis_id: $aid}})
                MATCH (b {{id: $to_id, analysis_id: $aid}})
                MERGE (a)-[r:{rel_label} {{analysis_id: $aid}}]->(b) SET r += $props
                """,
                from_id=edge.get("from"), to_id=edge.get("to"),
                aid=analysis_id, props=edge
            )

    async def _update_edge(self, analysis_id: str, update: Dict):
        rel_kind = update.get("rel_type", "influences")
        rel_label = self._get_rel_type(rel_kind)
        async with self.driver.session() as session:
            await session.run(
                f"""
                MATCH (a {{id: $from_id, analysis_id: $aid}})
                -[r:{rel_label}]->(b {{id: $to_id, analysis_id: $aid}})
                SET r += $props
                """,
                from_id=update.get("from"), to_id=update.get("to"),
                aid=analysis_id, props=update.get("properties", {})
            )

    async def delete_graph(self, analysis_id: str):
        """Delete all nodes and relationships for an analysis."""
        async with self.driver.session() as session:
            for label in NODE_TYPES.values():
                await session.run(
                    f"MATCH (n:{label} {{analysis_id: $aid}}) DETACH DELETE n",
                    aid=analysis_id
                )

    async def get_subgraph(self, analysis_id: str, node_type: str) -> Dict:
        """Get subgraph filtered by node type."""
        label = self._get_node_label(node_type)
        async with self.driver.session() as session:
            result = await session.run(
                f"MATCH (n:{label} {{analysis_id: $aid}}) RETURN n",
                aid=analysis_id
            )
            nodes = []
            async for record in result:
                n = record["n"]
                nodes.append({"id": n.get("id"), "name": n.get("name"), "type": n.get("type")})
        return {"nodes": nodes, "edges": []}

    async def find_paths(self, analysis_id: str, from_id: str, to_id: str, max_depth: int = 5) -> List[List[str]]:
        """Find all paths between two nodes."""
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH path = (a {id: $from_id, analysis_id: $aid})
                -[*1..""" + str(max_depth) + """]->(b {id: $to_id, analysis_id: $aid})
                RETURN [n IN nodes(path) | n.id] as node_ids
                LIMIT 20
                """,
                from_id=from_id, to_id=to_id, aid=analysis_id
            )
            paths = []
            async for record in result:
                paths.append(record["node_ids"])
            return paths
