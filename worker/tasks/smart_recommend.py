"""Smart Recommend Task - Generate whale recommendations.

Analyzes market conditions and whale behavior to generate
personalized recommendations for the user.
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


async def execute(payload: Dict, context: Dict) -> Dict[str, Any]:
    """Generate smart recommendations."""
    publish = context["publish_progress"]
    pg = context["pg"]
    redis = context["redis"]

    user_id = payload.get("user_id", "default")
    chain = payload.get("chain", "all")
    limit = payload.get("limit", 10)

    # ── Step 1: Fetch qualified whales ───────────────────────
    publish(10, "Loading whale database...")
    try:
        whales = await pg.fetch(
            "SELECT * FROM whales WHERE score >= 60 "
            "ORDER BY score DESC LIMIT 50"
        )
    except Exception:
        # Fallback to cached data
        whales = []

    if not whales:
        publish(100, "No qualified whales found")
        return {"recommendations": [], "count": 0}

    # ── Step 2: Analyze patterns ─────────────────────────────
    publish(30, "Analyzing behavioral patterns...")
    from backend.services.smart_recommend import SmartRecommend

    recommender = SmartRecommend()
    recommendations: List[Dict] = []

    for i, whale in enumerate(whales[:limit]):
        whale_addr = whale.get("address") if isinstance(whale, dict) else whale[0]

        # Get cached analysis or skip
        cached = await redis.get_cached_whale(whale_addr)
        if not cached:
            continue

        rec = await recommender.generate(
            whale_data=cached,
            market_context={},
            user_preferences=payload.get("preferences", {})
        )

        if rec:
            recommendations.append({
                "address": whale_addr,
                "score": cached.get("score", 0),
                "reason": rec.get("reason", ""),
                "confidence": rec.get("confidence", "medium"),
                "pattern": rec.get("pattern", ""),
                "insight": rec.get("insight", ""),
                "profit": cached.get("profit_usd", 0),
                "winrate": cached.get("win_rate", 0),
                "timeframe": rec.get("timeframe", "7d"),
                "tags": cached.get("labels", [])
            })

        pct = 30 + int((i + 1) / limit * 50)
        publish(pct, f"Analyzed {i + 1}/{limit} whales")

    # ── Step 3: Rank and deduplicate ─────────────────────────
    publish(85, "Ranking recommendations...")
    recommendations.sort(key=lambda x: x.get("score", 0), reverse=True)

    # ── Step 4: Store ────────────────────────────────────────
    publish(92, "Caching recommendations...")
    await redis.set_json(
        f"recommendations:{user_id}",
        recommendations,
        ttl=3600
    )

    publish(100, f"Generated {len(recommendations)} recommendations")

    return {
        "user_id": user_id,
        "count": len(recommendations),
        "recommendations": recommendations
    }
