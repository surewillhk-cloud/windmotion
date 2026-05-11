"""Smart Recommend API routes."""
from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/recommend", tags=["recommend"])


@router.get("")
async def get_recommendations(request: Request):
    """Get smart recommendations based on historical analysis data."""
    pg = request.app.state.pg

    recommendations = []

    # Get top whales for analysis
    top_whales = await pg.fetch(
        "SELECT * FROM whales ORDER BY score DESC LIMIT 50"
    )

    if not top_whales:
        return {"recommendations": [], "total": 0}

    # Analyze patterns and generate recommendations
    avg_win_rate = sum(w.get("win_rate", 0) for w in top_whales) / len(top_whales)
    avg_roi = sum(w.get("roi", 0) for w in top_whales) / len(top_whales)

    if avg_win_rate > 65:
        recommendations.append({
            "id": "rec-winrate",
            "type": "filter_adjust",
            "title": "Increase win rate threshold",
            "description": f"Top whales average {avg_win_rate:.0f}% win rate. Consider raising your filter threshold.",
            "reason": "Historical data shows high performer concentration",
            "expected_impact": "Better quality whale selection",
            "config_patch": {"min_win_rate": int(avg_win_rate - 5)},
            "score": 85,
            "confidence": "high",
            "status": "pending",
        })

    if avg_roi > 200:
        recommendations.append({
            "id": "rec-roi",
            "type": "filter_adjust",
            "title": "Focus on high ROI patterns",
            "description": f"Top whales average {avg_roi:.0f}% ROI. Filter for similar profiles.",
            "reason": "ROI patterns identified in whale library",
            "expected_impact": "Higher return potential",
            "config_patch": {"min_roi": int(avg_roi * 0.7)},
            "score": 78,
            "confidence": "medium",
            "status": "pending",
        })

    # Check for unanalyzed high-score whales
    unanalyzed = await pg.fetch(
        """
        SELECT w.address, w.score, w.total_profit_usd
        FROM whales w
        LEFT JOIN analyses a ON w.address = a.whale_address
        WHERE a.id IS NULL AND w.score > 70
        ORDER BY w.score DESC LIMIT 10
        """
    )

    for whale in unanalyzed:
        recommendations.append({
            "id": f"rec-analyze-{whale['address'][:8]}",
            "type": "new_analysis",
            "title": f"Analyze high-score whale {whale['address'][:10]}...",
            "description": f"Score: {whale['score']:.0f}, Profit: ${whale.get('total_profit_usd', 0):,.0f}",
            "reason": "High-score whale not yet analyzed",
            "expected_impact": "New strategy insights",
            "address": whale["address"],
            "score": int(whale["score"]),
            "confidence": "high",
            "status": "pending",
        })

    # Store recommendations
    for rec in recommendations:
        await pg.execute(
            """
            INSERT INTO recommendations (recommendation_type, title, description, reason, expected_impact, config_patch, status)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT DO NOTHING
            """,
            rec["type"], rec["title"], rec["description"],
            rec["reason"], rec["expected_impact"],
            rec.get("config_patch", {}), rec["status"],
        )

    return {"recommendations": recommendations, "total": len(recommendations)}


@router.post("/{rec_id}/apply")
async def apply_recommendation(rec_id: str, request: Request):
    """Apply a recommendation."""
    pg = request.app.state.pg
    await pg.execute(
        "UPDATE recommendations SET status = 'applied' WHERE id = $1",
        int(rec_id) if rec_id.isdigit() else 0,
    )
    return {"status": "applied", "id": rec_id}


@router.post("/{rec_id}/ignore")
async def ignore_recommendation(rec_id: str, request: Request):
    """Ignore a recommendation."""
    pg = request.app.state.pg
    await pg.execute(
        "UPDATE recommendations SET status = 'ignored' WHERE id = $1",
        int(rec_id) if rec_id.isdigit() else 0,
    )
    return {"status": "ignored", "id": rec_id}
