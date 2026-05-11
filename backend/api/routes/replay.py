"""Replay API routes with PostgreSQL backend."""
from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/api/replay", tags=["replay"])


@router.get("/{analysis_id}")
async def get_replay(analysis_id: str, request: Request):
    """Get full replay data: rounds + decision_nodes + probability_timeline."""
    pg = request.app.state.pg

    analysis = await pg.fetchrow(
        """
        SELECT id, whale_address, analysis_type, probability_timeline,
               deliberation_records
        FROM analyses
        WHERE id = $1
        """,
        analysis_id,
    )
    if not analysis:
        raise HTTPException(404, "Analysis not found")

    rounds = await pg.fetch(
        """
        SELECT id, whale_address, token_address, token_symbol,
               start_time, end_time, total_invested_usd, total_returned_usd,
               net_profit_usd, roi, max_drawdown_pct, avg_entry_price,
               avg_exit_price, trade_count, hold_days, status
        FROM rounds
        WHERE analysis_id = $1
        ORDER BY start_time
        """,
        analysis_id,
    )

    round_ids = [r["id"] for r in rounds]
    decision_nodes = []
    if round_ids:
        decision_nodes = await pg.fetch(
            """
            SELECT id, round_id, node_type, timestamp, token_address,
                   token_symbol, price_at_decision, price_change_pct,
                   market_cap, liquidity_depth, holder_count, volume_24h,
                   social_mentions, btc_trend, market_sentiment,
                   position_size_pct, inferred_logic, factor_scores
            FROM decision_nodes
            WHERE round_id = ANY($1)
            ORDER BY timestamp
            """,
            round_ids,
        )

    # Fetch price data from transactions for the whale
    price_data = await pg.fetch(
        """
        SELECT timestamp, value_usd, token_symbol, tx_type
        FROM transactions
        WHERE from_address = $1
        ORDER BY timestamp
        LIMIT 500
        """,
        analysis.get("whale_address", ""),
    )

    return {
        "analysis_id": analysis_id,
        "rounds": rounds,
        "decision_nodes": decision_nodes,
        "probability_timeline": analysis.get("probability_timeline", []),
        "deliberation_markers": analysis.get("deliberation_records", []),
        "price_data": price_data,
    }


@router.get("/{analysis_id}/cases")
async def list_cases(analysis_id: str, request: Request):
    """List available embed cases."""
    pg = request.app.state.pg

    existing = await pg.fetchrow("SELECT id FROM analyses WHERE id = $1", analysis_id)
    if not existing:
        raise HTTPException(404, "Analysis not found")

    return {"cases": []}
