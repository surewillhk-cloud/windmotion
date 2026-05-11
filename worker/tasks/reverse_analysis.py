"""Reverse Analysis Task - 5-step reverse inference pipeline.

Steps:
    1. Pattern Recognition (match against known strategy patterns)
    2. Factor Analysis (5-factor scoring: F1-F5)
    3. Decision Reconstruction (round-by-round timeline)
    4. Deliberation (if factor spread > threshold)
    5. Conclusion & Recommendation
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def execute(payload: Dict, context: Dict) -> Dict[str, Any]:
    """Execute the reverse analysis pipeline."""
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

    # ── Step 1: Pattern Recognition ──────────────────────────
    publish(10, "Step 1: Scanning strategy patterns...")
    from backend.skills.factor_reverse import FactorReverse

    factor_reverse = FactorReverse()

    # Fetch whale data
    from backend.skills.data_fetch import DataFetch
    data_fetch = DataFetch()

    fetch_result = await data_fetch.execute({
        "address": address,
        "chain": chain,
        "data_types": ["transactions", "token_transfers", "dex_swaps", "internal_txns"]
    })

    if not fetch_result.success:
        raise Exception(f"Data fetch failed: {fetch_result.error}")

    publish(20, "Step 1: Matching against pattern library...")
    factor_result = await factor_reverse.execute({
        "whale_address": address,
        "trade_history": fetch_result.data.get("transactions", []),
        "token_price_history": {}
    })

    if not factor_result.success:
        raise Exception(f"Factor analysis failed: {factor_result.error}")

    patterns = factor_result.data.get("matched_patterns", [])
    factor_scores = factor_result.data.get("factor_scores", {})
    rounds = factor_result.data.get("rounds", [])

    results["step_1"] = {"patterns": patterns, "raw_data": fetch_result.data}

    # ── Step 2: Factor Analysis ──────────────────────────────
    publish(35, "Step 2: Computing 5-factor scores...")
    from backend.skills.context_manage import ContextManage

    context_mgr = ContextManage()
    env_state = await context_mgr.execute({
        "address": address,
        "chain": chain,
        "timeframe": payload.get("timeframe", "90d")
    })

    results["step_2"] = {
        "factor_scores": factor_scores,
        "environment_state": env_state.data if env_state.success else {}
    }

    # ── Step 3: Decision Reconstruction ──────────────────────
    publish(50, "Step 3: Reconstructing decision timeline...")
    round_details = []

    for ri, round_data in enumerate(rounds):
        round_nodes = []
        for trade in round_data.get("trades", []):
            round_nodes.append({
                "label": trade.get("description", f"Trade {ri}"),
                "type": "decision",
                "description": trade.get("reasoning", ""),
                "weight": trade.get("confidence", 0),
                "confidence": trade.get("confidence", 0)
            })

        round_details.append({
            "round": ri + 1,
            "nodes": round_nodes,
            "summary": round_data.get("summary", "")
        })

        pct = 50 + int((ri + 1) / max(len(rounds), 1) * 15)
        publish(pct, f"Step 3: Reconstructed round {ri + 1}/{len(rounds)}")

    results["step_3"] = {"rounds": round_details}

    # ── Step 4: Deliberation ─────────────────────────────────
    publish(68, "Step 4: Checking deliberation trigger...")
    from backend.skills.deliberate import Deliberate

    scores = list(factor_scores.values())
    score_spread = max(scores) - min(scores) if scores else 0

    if score_spread > 2.0:
        publish(72, f"Step 4: Deliberation triggered (spread={score_spread:.1f})...")
        deliberation = Deliberate()
        delib_result = await deliberation.execute({
            "trigger_reason": f"Factor score spread {score_spread:.1f} > 2.0",
            "factor_scores": factor_scores,
            "patterns": patterns,
            "participants": ["factor_analyst", "behavior_score", "pattern_matcher"],
            "context": ""
        }, context={"agent_pool": agent_pool, "model_router": model_router})

        results["step_4"] = {
            "triggered": True,
            "records": delib_result.data if delib_result.success else {}
        }
    else:
        results["step_4"] = {"triggered": False, "records": {}}

    # ── Step 5: Conclusion ───────────────────────────────────
    publish(88, "Step 5: Generating conclusion...")
    from backend.skills.report_generate import ReportGenerate

    report_skill = ReportGenerate()
    report_result = await report_skill.execute({
        "analysis_type": "reverse",
        "factor_scores": factor_scores,
        "patterns": patterns,
        "rounds": round_details,
        "deliberation": results["step_4"],
        "format": payload.get("format", "full")
    }, context={"agent_pool": agent_pool})

    results["step_5"] = report_result.data if report_result.success else {}

    # ── Persist ──────────────────────────────────────────────
    publish(95, "Saving results...")
    await _save_reverse_analysis(pg, analysis_id, address, chain, results)

    await redis.set_json(f"analysis:{analysis_id}:result", results, ttl=86400)

    return {
        "analysis_id": analysis_id,
        "address": address,
        "chain": chain,
        "patterns": patterns,
        "factor_scores": factor_scores,
        "rounds": round_details,
        "deliberation": results["step_4"],
        "report": results["step_5"]
    }


async def _save_reverse_analysis(pg, analysis_id: str, address: str, chain: str, results: Dict):
    """Persist reverse analysis to PostgreSQL."""
    import json
    try:
        await pg.execute(
            "INSERT INTO analyses (id, address, chain, type, status, result, created_at) "
            "VALUES ($1, $2, $3, 'reverse', 'completed', $4, NOW()) "
            "ON CONFLICT (id) DO UPDATE SET status = 'completed', result = $4",
            analysis_id, address, chain,
            json.dumps(results, ensure_ascii=False, default=str)
        )
    except Exception as e:
        logger.warning(f"PostgreSQL save failed (non-fatal): {e}")
