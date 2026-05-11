"""Graph Sync Task - Sync causal graph data to Neo4j.

Handles incremental updates and full rebuilds of the graph database.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def execute(payload: Dict, context: Dict) -> Dict[str, Any]:
    """Sync graph to Neo4j."""
    publish = context["publish_progress"]
    neo4j = context["neo4j"]

    analysis_id = payload.get("analysis_id")
    graph_data = payload.get("graph")
    mode = payload.get("mode", "upsert")  # upsert | replace

    if not graph_data:
        raise ValueError("No graph data provided")

    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    # ── Clear existing if replace mode ───────────────────────
    if mode == "replace":
        publish(5, "Clearing existing graph...")
        await neo4j.execute(
            "MATCH (n:Node {analysis_id: $aid}) DETACH DELETE n",
            {"aid": analysis_id}
        )

    # ── Upsert nodes ─────────────────────────────────────────
    publish(20, f"Syncing {len(nodes)} nodes...")
    for i, node in enumerate(nodes):
        await neo4j.execute(
            "MERGE (n:Node {id: $id, analysis_id: $aid}) "
            "SET n.label = $label, n.type = $type, n.updated_at = datetime()",
            {
                "id": node.get("id"),
                "aid": analysis_id,
                "label": node.get("label", ""),
                "type": node.get("type", "unknown")
            }
        )
        if (i + 1) % 10 == 0:
            pct = 20 + int((i + 1) / len(nodes) * 30)
            publish(pct, f"Synced {i + 1}/{len(nodes)} nodes")

    # ── Upsert edges ─────────────────────────────────────────
    publish(55, f"Syncing {len(edges)} edges...")
    for i, edge in enumerate(edges):
        src = edge.get("source")
        tgt = edge.get("target")
        if isinstance(src, dict):
            src = src.get("id")
        if isinstance(tgt, dict):
            tgt = tgt.get("id")

        await neo4j.execute(
            "MATCH (a:Node {id: $src, analysis_id: $aid}) "
            "MATCH (b:Node {id: $tgt, analysis_id: $aid}) "
            "MERGE (a)-[r:CAUSES {analysis_id: $aid}]->(b) "
            "SET r.strength = $strength, r.verified = $verified, r.updated_at = datetime()",
            {
                "src": src, "tgt": tgt, "aid": analysis_id,
                "strength": edge.get("strength", "medium"),
                "verified": edge.get("verified", False)
            }
        )
        if (i + 1) % 10 == 0:
            pct = 55 + int((i + 1) / len(edges) * 30)
            publish(pct, f"Synced {i + 1}/{len(edges)} edges")

    # ── Create indexes ───────────────────────────────────────
    publish(90, "Creating indexes...")
    try:
        await neo4j.execute("CREATE INDEX node_id IF NOT EXISTS FOR (n:Node) ON (n.id)")
        await neo4j.execute("CREATE INDEX node_analysis IF NOT EXISTS FOR (n:Node) ON (n.analysis_id)")
    except Exception as e:
        logger.warning(f"Index creation skipped: {e}")

    publish(100, "Graph sync complete")

    return {
        "analysis_id": analysis_id,
        "nodes_synced": len(nodes),
        "edges_synced": len(edges),
        "mode": mode
    }
