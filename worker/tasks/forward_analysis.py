"""Forward Analysis Task - Full 6-phase inference pipeline.

Phases:
    0. Data Preparation (fetch + factor calculation)
    1. Causal Graph Build (referee + 3 reviewers)
    2. Event Chain Analysis (multi-agent reasoning)
    3. Probability Pricing (ensemble aggregation)
    4. Deliberation (if triggered)
    5. Report Generation
"""
import logging
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def execute(payload: Dict, context: Dict) -> Dict[str, Any]:
    """Execute the forward analysis pipeline."""
    address = payload["address"]
    chain = payload.get("chain", "bsc")
    publish = context["publish_progress"]

    pg = context["pg"]
    neo4j = context["neo4j"]
    agent_pool = context["agent_pool"]
    model_router = context["model_router"]
    redis = context["redis"]

    analysis_id = context["task_id"]
    results = {}

    # ── Phase 0: Data Preparation ────────────────────────────
    publish(5, "Phase 0: Fetching on-chain data...")
    from backend.skills.data_fetch import DataFetch
    from backend.skills.factor_reverse import FactorReverse

    data_fetch = DataFetch()
    factor_reverse = FactorReverse()

    fetch_result = await data_fetch.execute({
        "address": address,
        "chain": chain,
        "data_types": ["transactions", "token_transfers", "dex_swaps"]
    })

    if not fetch_result.success:
        raise Exception(f"Data fetch failed: {fetch_result.error}")

    publish(12, "Phase 0: Calculating factor scores...")
    factor_result = await factor_reverse.execute({
        "whale_address": address,
        "trade_history": fetch_result.data.get("transactions", []),
        "token_price_history": {}
    })

    results["phase_0"] = {
        "raw_data": fetch_result.data,
        "rounds": factor_result.data.get("rounds", []),
        "factor_scores": factor_result.data.get("factor_scores", {}),
        "strategy_pattern": factor_result.data.get("strategy_pattern")
    }

    # ── Phase 1: Causal Graph Build ──────────────────────────
    publish(20, "Phase 1: Building causal graph...")
    from backend.skills.causal_graph_build import CausalGraphBuild

    graph_skill = CausalGraphBuild()
    graph_result = await graph_skill.execute({
        "seed_data": {
            "rounds": results["phase_0"]["rounds"],
            "factors": results["phase_0"]["factor_scores"],
            "pattern": results["phase_0"]["strategy_pattern"]
        },
        "target": payload.get("target", "profitability"),
        "constraints": {}
    }, context={"agent_pool": agent_pool, "model_router": model_router})

    if not graph_result.success:
        raise Exception(f"Graph build failed: {graph_result.error}")

    graph = graph_result.data.get("graph", {})
    activation_map = graph_result.data.get("activation_map", {})
    results["phase_1"] = {"graph": graph, "activation_map": activation_map}

    # Sync graph to Neo4j
    publish(30, "Phase 1: Syncing graph to Neo4j...")
    await _sync_graph_to_neo4j(neo4j, analysis_id, graph)

    # ── Phase 2: Event Chain Analysis ────────────────────────
    publish(35, "Phase 2: Analyzing event chain...")
    from backend.skills.event_analyze import EventAnalyze
    from backend.skills.probability_price import ProbabilityPrice

    event_skill = EventAnalyze()
    prob_skill = ProbabilityPrice()

    events = fetch_result.data.get("events", [])
    all_event_results = []
    probability_timeline = []
    context_str = ""

    event_groups = _group_events(events)

    for gi, group in enumerate(event_groups):
        group_results = []
        for event in group:
            event_type = event.get("type", "default")
            activated = activation_map.get(event_type, ["chain_analyst", "token_analyst", "macro_analyst"])

            result = await event_skill.execute({
                "event": event,
                "graph_snapshot": graph,
                "context": context_str,
                "activated_agents": activated
            }, context={"agent_pool": agent_pool})

            if result.success:
                group_results.append(result.data)
                context_str += f"\n{result.data.get('event_summary', '')}"

        # Probability pricing after each group
        prob_result = await prob_skill.execute({
            "reasoning_results": group_results,
            "graph_snapshot": graph,
            "agent_profiles": agent_pool.get_profiles()
        })

        if prob_result.success:
            probability_timeline.append({
                "aggregate": prob_result.data.get("weighted_aggregate"),
                "std_dev": prob_result.data.get("std_dev"),
                "spread": prob_result.data.get("max_spread")
            })

        all_event_results.extend(group_results)

        pct = 35 + int((gi + 1) / len(event_groups) * 25)
        publish(pct, f"Phase 2: Processed {gi + 1}/{len(event_groups)} event groups")

    results["phase_2"] = {
        "event_results": all_event_results,
        "probability_timeline": probability_timeline,
        "context": context_str
    }

    # ── Phase 3: Deliberation ────────────────────────────────
    publish(62, "Phase 3: Checking deliberation trigger...")
    from backend.skills.deliberate import Deliberate

    last_prob = probability_timeline[-1] if probability_timeline else {}
    should_deliberate = (
        last_prob.get("spread", 0) > 30 or
        abs(last_prob.get("change", 0)) > 15
    )

    if should_deliberate:
        publish(65, "Phase 3: Running deliberation (spread > 30%)...")
        deliberation = Deliberate()
        delib_result = await deliberation.execute({
            "trigger_reason": f"Spread {last_prob.get('spread', 0):.0f}% exceeded threshold",
            "probability_dist": last_prob,
            "graph_snapshot": graph,
            "participants": ["chain_analyst", "token_analyst", "retail_a", "institutional"],
            "context": context_str
        }, context={"agent_pool": agent_pool, "model_router": model_router})

        results["phase_3"] = {
            "triggered": True,
            "records": delib_result.data if delib_result.success else {}
        }
    else:
        results["phase_3"] = {"triggered": False, "records": {}}

    # ── Phase 4: Final Review ────────────────────────────────
    publish(78, "Phase 4: Final review...")
    consensus = [e for e in graph.get("edges", []) if e.get("verified")]
    divergence = [e for e in graph.get("edges", []) if not e.get("verified")]

    results["phase_4"] = {
        "consensus_paths": len(consensus),
        "divergence_paths": len(divergence),
        "total_nodes": len(graph.get("nodes", [])),
        "total_edges": len(graph.get("edges", []))
    }

    # ── Phase 5: Report Generation ───────────────────────────
    publish(88, "Phase 5: Generating report...")
    from backend.skills.report_generate import ReportGenerate

    report_skill = ReportGenerate()
    report_result = await report_skill.execute({
        "final_graph": graph,
        "probability_timeline": probability_timeline,
        "deliberation_records": results["phase_3"].get("records", {}),
        "review_output": results["phase_4"],
        "format": payload.get("format", "full")
    }, context={"agent_pool": agent_pool})

    results["phase_5"] = report_result.data if report_result.success else {}

    # ── Persist to PostgreSQL ────────────────────────────────
    publish(95, "Saving results...")
    await _save_analysis(pg, analysis_id, address, chain, results)

    # ── Cache result ─────────────────────────────────────────
    await redis.set_json(f"analysis:{analysis_id}:result", results, ttl=86400)

    return {
        "analysis_id": analysis_id,
        "address": address,
        "chain": chain,
        "graph": graph,
        "probability_timeline": probability_timeline,
        "deliberation": results["phase_3"],
        "report": results["phase_5"],
        "phase_summary": {
            "phase_0": "Data fetched, factors calculated",
            "phase_1": f"Graph: {len(graph.get('nodes', []))} nodes, {len(graph.get('edges', []))} edges",
            "phase_2": f"{len(all_event_results)} events analyzed",
            "phase_3": f"Deliberation {'triggered' if results['phase_3']['triggered'] else 'not needed'}",
            "phase_4": f"Consensus: {len(consensus)}, Divergence: {len(divergence)}",
            "phase_5": "Report generated"
        }
    }


def _group_events(events: list) -> list:
    """Group events for sequential/parallel processing."""
    if not events:
        return []
    return [events[i:i+2] for i in range(0, len(events), 2)]


async def _sync_graph_to_neo4j(neo4j, analysis_id: str, graph: Dict):
    """Write causal graph to Neo4j."""
    try:
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])

        for node in nodes:
            await neo4j.execute(
                "MERGE (n:Node {id: $id, analysis_id: $aid}) "
                "SET n.label = $label, n.type = $type",
                {"id": node.get("id"), "aid": analysis_id,
                 "label": node.get("label"), "type": node.get("type")}
            )

        for edge in edges:
            await neo4j.execute(
                "MATCH (a:Node {id: $src, analysis_id: $aid}) "
                "MATCH (b:Node {id: $tgt, analysis_id: $aid}) "
                "MERGE (a)-[r:CAUSES {analysis_id: $aid}]->(b) "
                "SET r.strength = $strength, r.verified = $verified",
                {"src": edge.get("source"), "tgt": edge.get("target"),
                 "aid": analysis_id, "strength": edge.get("strength"),
                 "verified": edge.get("verified")}
            )

        logger.info(f"Graph synced to Neo4j: {len(nodes)} nodes, {len(edges)} edges")
    except Exception as e:
        logger.warning(f"Neo4j sync failed (non-fatal): {e}")


async def _save_analysis(pg, analysis_id: str, address: str, chain: str, results: Dict):
    """Persist analysis record to PostgreSQL."""
    try:
        await pg.execute(
            "INSERT INTO analyses (id, address, chain, type, status, result, created_at) "
            "VALUES ($1, $2, $3, 'forward', 'completed', $4, NOW()) "
            "ON CONFLICT (id) DO UPDATE SET status = 'completed', result = $4",
            analysis_id, address, chain,
            json.dumps(results, ensure_ascii=False, default=str)
        )
    except Exception as e:
        logger.warning(f"PostgreSQL save failed (non-fatal): {e}")
