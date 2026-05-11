"""Forward Analysis Task - Full 6-phase inference pipeline.

Phases:
    0. Data Preparation (DataFetch + FactorReverse)
    1. Causal Graph Build (CausalGraphBuild skill)
    2. Event Chain Analysis (EventAnalyze skill)
    3. Probability Pricing (ProbabilityPrice skill)
    4. Deliberation (Deliberate skill, if triggered)
    5. Report Generation (ReportGenerate skill)
"""
import json
import logging
import time
from typing import Dict, Any, List

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
    llm_caller = context.get("llm_caller")

    analysis_id = context["task_id"]
    results: Dict[str, Any] = {}

    # ── Phase 0: Data Preparation ────────────────────────────
    publish(5, "Phase 0: Fetching on-chain data...")
    from backend.skills.data_fetch import DataFetch
    from backend.skills.factor_reverse import FactorReverse

    data_fetch = DataFetch()
    factor_reverse = FactorReverse()

    # Fetch transactions
    tx_result = await data_fetch.execute({
        "data_type": "transactions",
        "params": {"address": address, "chain": chain, "limit": 200},
    })
    transactions = tx_result.data.get("data", {}).get("transactions", []) if tx_result.success else []

    # Fetch token transfers
    transfer_result = await data_fetch.execute({
        "data_type": "token_transfers",
        "params": {"address": address, "chain": chain, "limit": 200},
    })
    token_transfers = transfer_result.data.get("data", {}).get("transfers", []) if transfer_result.success else []

    # Fetch price data for relevant tokens
    price_data: Dict[str, Any] = {}
    token_addresses = _extract_unique_tokens(transactions, token_transfers)
    for token_addr in token_addresses[:5]:
        price_result = await data_fetch.execute({
            "data_type": "price_history",
            "params": {"token": token_addr, "chain": chain, "days": 90},
        })
        if price_result.success:
            price_data[token_addr] = price_result.data.get("data", {}).get("prices", [])

    publish(12, "Phase 0: Calculating factor scores...")

    # Merge and classify
    combined_txs = _merge_transactions(transactions, token_transfers)
    factor_result = await factor_reverse.execute({
        "address": address,
        "transactions": combined_txs,
        "price_data": price_data,
    })

    rounds = factor_result.data.get("decision_nodes", []) if factor_result.success else []
    factor_scores = factor_result.data.get("factors", {}) if factor_result.success else {}
    strategy_pattern = factor_result.data.get("matched_strategies", []) if factor_result.success else []

    # Generate events from rounds for causal graph
    events = _generate_events_from_rounds(rounds, combined_txs)

    results["phase_0"] = {
        "raw_data": {"transactions": transactions, "transfers": token_transfers},
        "rounds": rounds,
        "factor_scores": factor_scores,
        "strategy_pattern": strategy_pattern[0] if strategy_pattern else None,
        "events": events,
    }

    # ── Phase 1: Causal Graph Build ──────────────────────────
    publish(20, "Phase 1: Building causal graph...")
    from backend.skills.causal_graph_build import CausalGraphBuild

    graph_skill = CausalGraphBuild()
    graph_result = await graph_skill.execute(
        {
            "events": events,
            "context": f"分析地址 {address} 在 {chain} 上的交易行为因果关系",
        },
        context={
            "agent_pool": agent_pool,
            "model_router": model_router,
            "llm_caller": llm_caller,
        },
    )

    if not graph_result.success:
        logger.warning(f"Graph build failed: {graph_result.error}, using empty graph")
        graph = {"nodes": [], "edges": []}
    else:
        graph = graph_result.data.get("graph", graph_result.data.get("final_graph", {"nodes": [], "edges": []}))

    activation_map = graph_result.data.get("activation_map", {}) if graph_result.success else {}
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

    all_event_results: List[Dict] = []
    probability_timeline: List[Dict] = []
    context_str = ""

    event_groups = _group_events(events)

    for gi, group in enumerate(event_groups):
        group_results = []
        for event in group:
            event_type = event.get("type", "default")
            activated = activation_map.get(event_type, ["chain_analyst", "token_analyst", "macro_analyst"])

            result = await event_skill.execute(
                {
                    "event": event,
                    "graph_snapshot": graph,
                    "context": context_str,
                    "activated_agents": activated,
                },
                context={"agent_pool": agent_pool, "llm_caller": llm_caller},
            )

            if result.success:
                group_results.append(result.data)
                context_str += f"\n{result.data.get('event_summary', event.get('label', ''))}"

        # Probability pricing after each group
        prob_result = await prob_skill.execute({
            "agent_results": group_results,
        })

        if prob_result.success:
            probability_timeline.append({
                "aggregate": prob_result.data.get("weighted_probability"),
                "std_dev": prob_result.data.get("std_dev"),
                "spread": prob_result.data.get("spread"),
            })

        all_event_results.extend(group_results)

        pct = 35 + int((gi + 1) / max(len(event_groups), 1) * 25)
        publish(pct, f"Phase 2: Processed {gi + 1}/{len(event_groups)} event groups")

    results["phase_2"] = {
        "event_results": all_event_results,
        "probability_timeline": probability_timeline,
        "context": context_str,
    }

    # ── Phase 3: Probability Pricing ─────────────────────────
    publish(62, "Phase 3: Aggregating probabilities...")
    last_prob = probability_timeline[-1] if probability_timeline else {}
    weighted_probability = last_prob.get("aggregate", 50)
    spread = last_prob.get("spread", 0)

    results["phase_3_prob"] = {
        "weighted_probability": weighted_probability,
        "spread": spread,
        "timeline": probability_timeline,
    }

    # ── Phase 4: Deliberation (if triggered) ─────────────────
    publish(65, "Phase 4: Checking deliberation trigger...")
    from backend.skills.deliberate import Deliberate

    should_deliberate = spread > 30 or abs(last_prob.get("std_dev", 0)) > 15

    if should_deliberate and all_event_results:
        publish(68, f"Phase 4: Deliberation triggered (spread={spread:.0f}%)...")

        # Find most divergent pair
        sorted_results = sorted(all_event_results, key=lambda r: r.get("probability_estimate", 50))
        most_divergent_pair = {
            "low": {"agent_id": sorted_results[0].get("agent_id", ""), "probability": sorted_results[0].get("probability_estimate", 50)},
            "high": {"agent_id": sorted_results[-1].get("agent_id", ""), "probability": sorted_results[-1].get("probability_estimate", 50)},
        }

        deliberation = Deliberate()
        delib_result = await deliberation.execute(
            {
                "agent_results": all_event_results,
                "most_divergent_pair": most_divergent_pair,
                "graph_snapshot": graph,
                "spread": spread,
                "weighted_probability": weighted_probability,
            },
            context={
                "agent_pool": agent_pool,
                "model_router": model_router,
                "llm_caller": llm_caller,
            },
        )

        results["phase_4"] = {
            "triggered": True,
            "records": delib_result.data if delib_result.success else {},
        }

        # Update weighted probability with deliberation result
        if delib_result.success:
            final_prob = delib_result.data.get("final_probability", weighted_probability)
            results["phase_3_prob"]["weighted_probability_after_deliberation"] = final_prob
    else:
        results["phase_4"] = {"triggered": False, "records": {}}

    # ── Phase 5: Report Generation ───────────────────────────
    publish(80, "Phase 5: Generating report...")
    from backend.skills.report_generate import ReportGenerate

    report_skill = ReportGenerate()
    analysis_data = {
        "type": "forward",
        "address": address,
        "chain": chain,
        "factor_scores": factor_scores,
        "graph": graph,
        "probability_timeline": probability_timeline,
        "weighted_probability": results["phase_3_prob"]["weighted_probability"],
        "deliberation": results["phase_4"],
        "event_results": all_event_results,
        "strategy_pattern": results["phase_0"]["strategy_pattern"],
    }

    report_result = await report_skill.execute(
        {"analysis_data": analysis_data},
        context={"agent_pool": agent_pool, "llm_caller": llm_caller},
    )
    report = report_result.data if report_result.success else {}

    results["phase_5"] = report

    # ── Consensus / Divergence summary ───────────────────────
    consensus = [e for e in graph.get("edges", []) if e.get("verified")]
    divergence = [e for e in graph.get("edges", []) if not e.get("verified")]

    results["summary"] = {
        "consensus_paths": len(consensus),
        "divergence_paths": len(divergence),
        "total_nodes": len(graph.get("nodes", [])),
        "total_edges": len(graph.get("edges", [])),
    }

    # ── Persist ──────────────────────────────────────────────
    publish(95, "Saving results...")
    await _save_analysis(pg, analysis_id, address, chain, results)
    await redis.set_json(f"analysis:{analysis_id}:result", results, ttl=86400)

    publish(100, "Forward analysis complete")

    return {
        "analysis_id": analysis_id,
        "address": address,
        "chain": chain,
        "graph": graph,
        "probability_timeline": probability_timeline,
        "weighted_probability": results["phase_3_prob"]["weighted_probability"],
        "deliberation": results["phase_4"],
        "report": report,
        "phase_summary": {
            "phase_0": f"Data fetched: {len(transactions)} txs, {len(token_transfers)} transfers",
            "phase_1": f"Graph: {len(graph.get('nodes', []))} nodes, {len(graph.get('edges', []))} edges",
            "phase_2": f"{len(all_event_results)} events analyzed",
            "phase_3": f"Probability: {results['phase_3_prob']['weighted_probability']:.0f}%, spread: {spread:.0f}%",
            "phase_4": f"Deliberation {'triggered' if results['phase_4']['triggered'] else 'not needed'}",
            "phase_5": "Report generated",
        },
    }


def _extract_unique_tokens(transactions: List[Dict], transfers: List[Dict]) -> List[str]:
    """Extract unique token addresses."""
    tokens = set()
    for tx in transactions:
        if tx.get("value", "0") != "0" and not tx.get("contractAddress"):
            tokens.add("0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c")  # WBNB
        if tx.get("contractAddress"):
            tokens.add(tx["contractAddress"].lower())
    for tf in transfers:
        ca = tf.get("contractAddress", "")
        if ca:
            tokens.add(ca.lower())
    return list(tokens)


def _merge_transactions(transactions: List[Dict], transfers: List[Dict]) -> List[Dict]:
    """Merge external transactions and token transfers."""
    merged = []
    for tx in transactions:
        fn = tx.get("functionName", "").lower()
        tx_type = "other"
        if "swap" in fn:
            tx_type = "swap"
        elif "addliquidity" in fn:
            tx_type = "lp_add"
        elif "removeliquidity" in fn:
            tx_type = "lp_remove"
        elif fn == "":
            tx_type = "bnb_transfer"

        merged.append({
            "hash": tx.get("hash", ""),
            "from": tx.get("from", "").lower(),
            "to": tx.get("to", "").lower(),
            "value_wei": int(tx.get("value", "0")),
            "value_bnb": int(tx.get("value", "0")) / 1e18,
            "timestamp": int(tx.get("timeStamp", 0)),
            "block": int(tx.get("blockNumber", 0)),
            "method": tx.get("functionName", ""),
            "type": tx_type,
            "source": "external",
        })
    for tf in transfers:
        merged.append({
            "hash": tf.get("hash", ""),
            "from": tf.get("from", "").lower(),
            "to": tf.get("to", "").lower(),
            "value_wei": int(tf.get("value", "0")),
            "token": tf.get("tokenSymbol", ""),
            "token_address": tf.get("contractAddress", "").lower(),
            "timestamp": int(tf.get("timeStamp", 0)),
            "type": "token_transfer",
            "source": "token_transfer",
        })
    merged.sort(key=lambda x: x.get("timestamp", 0))
    return merged


def _generate_events_from_rounds(nodes: List[Dict], transactions: List[Dict]) -> List[Dict]:
    """Generate analysis events from decision nodes and transactions."""
    events = []
    for i, node in enumerate(nodes[:20]):  # limit events
        events.append({
            "id": f"event_{i}",
            "type": node.get("type", "transaction"),
            "label": f"{node.get('type', 'Event')} #{i+1}",
            "description": node.get("reason", node.get("reason_en", "")),
            "data": node,
        })

    # If no nodes, create events from raw transactions
    if not events and transactions:
        for i, tx in enumerate(transactions[:10]):
            events.append({
                "id": f"tx_event_{i}",
                "type": tx.get("type", "transaction"),
                "label": f"Transaction {tx.get('hash', '')[:10]}",
                "description": f"{tx.get('type', 'transfer')} from {tx.get('from', '')[:8]}... to {tx.get('to', '')[:8]}...",
                "data": tx,
            })

    return events


def _group_events(events: list) -> list:
    """Group events for sequential/parallel processing."""
    if not events:
        return []
    return [events[i:i + 2] for i in range(0, len(events), 2)]


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
                 "label": node.get("label"), "type": node.get("type")},
            )

        for edge in edges:
            await neo4j.execute(
                "MATCH (a:Node {id: $src, analysis_id: $aid}) "
                "MATCH (b:Node {id: $tgt, analysis_id: $aid}) "
                "MERGE (a)-[r:CAUSES {analysis_id: $aid}]->(b) "
                "SET r.strength = $strength, r.verified = $verified",
                {"src": edge.get("source"), "tgt": edge.get("target"),
                 "aid": analysis_id, "strength": edge.get("strength"),
                 "verified": edge.get("verified")},
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
            json.dumps(results, ensure_ascii=False, default=str),
        )
    except Exception as e:
        logger.warning(f"PostgreSQL save failed (non-fatal): {e}")
