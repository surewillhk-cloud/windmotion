"""Analysis API routes."""
from fastapi import APIRouter, HTTPException, Query, Request
from typing import Optional

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/{analysis_id}")
async def get_analysis(analysis_id: str, request: Request):
    """Get analysis details from PostgreSQL."""
    pg = request.app.state.pg
    row = await pg.fetchrow(
        """
        SELECT id, whale_address, analysis_type, status, mode, chain,
               progress_pct, current_phase, started_at, completed_at,
               duration_s, report, factor_scores, matched_patterns,
               error, metadata, created_at
        FROM analyses
        WHERE id = $1
        """,
        analysis_id,
    )
    if not row:
        raise HTTPException(404, "Analysis not found")
    return row


@router.get("/{analysis_id}/progress")
async def get_analysis_progress(analysis_id: str, request: Request):
    """Get analysis progress from PostgreSQL."""
    pg = request.app.state.pg
    row = await pg.fetchrow(
        "SELECT id, status, progress_pct, current_phase FROM analyses WHERE id = $1",
        analysis_id,
    )
    if not row:
        raise HTTPException(404, "Analysis not found")
    return row


@router.get("/{analysis_id}/report")
async def get_analysis_report(analysis_id: str, request: Request):
    """Get analysis report from PostgreSQL."""
    pg = request.app.state.pg
    row = await pg.fetchrow(
        "SELECT id, report, status FROM analyses WHERE id = $1",
        analysis_id,
    )
    if not row:
        raise HTTPException(404, "Analysis not found")
    return row


@router.get("/{analysis_id}/replay")
async def get_analysis_replay(analysis_id: str, request: Request):
    """Get replay data: rounds + decision_nodes."""
    pg = request.app.state.pg

    analysis = await pg.fetchrow(
        "SELECT id, whale_address, probability_timeline FROM analyses WHERE id = $1",
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

    # Fetch decision nodes for all rounds of this analysis
    round_ids = [r["id"] for r in rounds]
    decision_nodes = []
    if round_ids:
        decision_nodes = await pg.fetch(
            """
            SELECT dn.id, dn.round_id, dn.node_type, dn.timestamp,
                   dn.token_address, dn.token_symbol, dn.price_at_decision,
                   dn.price_change_pct, dn.market_cap, dn.liquidity_depth,
                   dn.holder_count, dn.volume_24h, dn.social_mentions,
                   dn.btc_trend, dn.market_sentiment, dn.position_size_pct,
                   dn.inferred_logic, dn.factor_scores
            FROM decision_nodes dn
            WHERE dn.round_id = ANY($1)
            ORDER BY dn.timestamp
            """,
            round_ids,
        )

    return {
        "id": analysis_id,
        "rounds": rounds,
        "decision_nodes": decision_nodes,
        "probability_timeline": analysis.get("probability_timeline", []),
    }


@router.post("/{analysis_id}/cancel")
async def cancel_analysis(analysis_id: str, request: Request):
    """Cancel a running analysis."""
    pg = request.app.state.pg
    result = await pg.execute(
        """
        UPDATE analyses SET status = 'cancelled'
        WHERE id = $1 AND status IN ('pending', 'running')
        """,
        analysis_id,
    )
    if not result or result == "UPDATE 0":
        row = await pg.fetchrow("SELECT status FROM analyses WHERE id = $1", analysis_id)
        if not row:
            raise HTTPException(404, "Analysis not found")
        raise HTTPException(400, f"Cannot cancel analysis in status: {row['status']}")
    return {"id": analysis_id, "status": "cancelled"}
