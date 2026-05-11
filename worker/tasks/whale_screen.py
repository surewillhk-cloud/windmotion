"""Whale Screen Task - Periodic whale discovery and scoring.

Scans blockchain for new whale wallets, scores them against
user-defined filters, and triggers auto-analysis when matched.
"""
import logging
import json
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


async def execute(payload: Dict, context: Dict) -> Dict[str, Any]:
    """Execute whale screening."""
    publish = context["publish_progress"]
    pg = context["pg"]
    redis = context["redis"]

    chain = payload.get("chain", "bsc")
    filters = payload.get("filters", {})
    scan_mode = payload.get("mode", "full")  # full | incremental

    from backend.skills.whale_screen import WhaleScreen
    from backend.skills.data_fetch import DataFetch

    whale_screen = WhaleScreen()
    data_fetch = DataFetch()

    # ── Step 1: Discover candidates ──────────────────────────
    publish(10, f"Scanning {chain} for whale candidates...")
    discovery_result = await whale_screen.execute({
        "chain": chain,
        "min_balance_usd": filters.get("min_portfolio_usd", 100000),
        "min_tx_count": filters.get("min_trades", 20),
        "scan_mode": scan_mode
    })

    if not discovery_result.success:
        raise Exception(f"Whale discovery failed: {discovery_result.error}")

    candidates = discovery_result.data.get("candidates", [])
    publish(30, f"Found {len(candidates)} candidates, scoring...")

    # ── Step 2: Score each candidate ─────────────────────────
    from backend.services.whale_discovery import WhaleDiscovery
    whale_discovery = WhaleDiscovery()

    scored_whales: List[Dict] = []
    for i, candidate in enumerate(candidates):
        address = candidate["address"]

        # Fetch detailed history
        history = await data_fetch.execute({
            "address": address,
            "chain": chain,
            "data_types": ["transactions", "token_transfers"]
        })

        # Calculate score
        score_result = await whale_discovery.score_whale(
            address=address,
            history=history.data if history.success else {},
            filters=filters
        )

        scored_whales.append({
            "address": address,
            "chain": chain,
            "score": score_result.get("score", 0),
            "profit_usd": score_result.get("profit_usd", 0),
            "win_rate": score_result.get("win_rate", 0),
            "roi": score_result.get("roi", 0),
            "trade_count": score_result.get("trade_count", 0),
            "labels": score_result.get("labels", [])
        })

        pct = 30 + int((i + 1) / len(candidates) * 40)
        publish(pct, f"Scored {i + 1}/{len(candidates)} whales")

    # ── Step 3: Apply filters ────────────────────────────────
    publish(75, "Applying filter criteria...")
    qualified = _apply_filters(scored_whales, filters)

    # ── Step 4: Store results ────────────────────────────────
    publish(85, "Storing whale data...")
    for whale in scored_whales:
        await redis.cache_whale_data(whale["address"], whale, ttl=3600)

    # Store qualified whales to DB
    try:
        for whale in qualified:
            await pg.execute(
                "INSERT INTO whales (address, chain, score, profit_usd, win_rate, roi, trade_count, labels, updated_at) "
                "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW()) "
                "ON CONFLICT (address) DO UPDATE SET "
                "score = $3, profit_usd = $4, win_rate = $5, roi = $6, trade_count = $7, labels = $8, updated_at = NOW()",
                whale["address"], whale["chain"], whale["score"],
                whale["profit_usd"], whale["win_rate"], whale["roi"],
                whale["trade_count"], json.dumps(whale["labels"])
            )
    except Exception as e:
        logger.warning(f"PostgreSQL save failed (non-fatal): {e}")

    # ── Step 5: Trigger auto-analysis if enabled ─────────────
    auto_analyze = payload.get("auto_analyze", False)
    triggered = []
    if auto_analyze and qualified:
        publish(92, f"Triggering auto-analysis for {len(qualified)} whales...")
        for whale in qualified[:5]:  # Limit to top 5
            task_payload = {
                "task_type": "forward_analysis",
                "task_id": f"auto-{whale['address'][:8]}",
                "payload": {
                    "address": whale["address"],
                    "chain": whale["chain"],
                    "source": "auto_whale_screen"
                }
            }
            await redis.client.rpush("wm:task_queue", json.dumps(task_payload))
            triggered.append(whale["address"])

    publish(100, f"Done. {len(qualified)} whales qualified.")

    return {
        "chain": chain,
        "candidates_found": len(candidates),
        "scored": len(scored_whales),
        "qualified": len(qualified),
        "auto_triggered": len(triggered),
        "top_whales": qualified[:10],
        "triggered_analyses": triggered
    }


def _apply_filters(whales: List[Dict], filters: Dict) -> List[Dict]:
    """Apply user filter criteria to scored whales."""
    result = []
    for w in whales:
        if filters.get("min_win_rate") and w.get("win_rate", 0) < filters["min_win_rate"]:
            continue
        if filters.get("min_roi") and w.get("roi", 0) < filters["min_roi"]:
            continue
        if filters.get("min_profit") and w.get("profit_usd", 0) < filters["min_profit"]:
            continue
        if filters.get("min_score") and w.get("score", 0) < filters["min_score"]:
            continue
        result.append(w)

    # Sort by score descending
    result.sort(key=lambda x: x.get("score", 0), reverse=True)
    return result
