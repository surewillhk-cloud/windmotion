"""History API routes."""
from fastapi import APIRouter, Query, Request

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("")
async def get_history(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    type: str = Query("all"),
):
    """Get analysis history from PostgreSQL, ordered by created_at DESC."""
    pg = request.app.state.pg
    offset = (page - 1) * limit

    if type == "all":
        rows = await pg.fetch(
            """
            SELECT id, whale_address, analysis_type, status, mode, chain,
                   progress_pct, current_phase, started_at, completed_at,
                   duration_s, report IS NOT NULL AS has_report, created_at
            FROM analyses
            ORDER BY created_at DESC
            LIMIT $1 OFFSET $2
            """,
            limit, offset,
        )
        count_row = await pg.fetchrow("SELECT COUNT(*) AS cnt FROM analyses")
    else:
        rows = await pg.fetch(
            """
            SELECT id, whale_address, analysis_type, status, mode, chain,
                   progress_pct, current_phase, started_at, completed_at,
                   duration_s, report IS NOT NULL AS has_report, created_at
            FROM analyses
            WHERE analysis_type = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
            """,
            type, limit, offset,
        )
        count_row = await pg.fetchrow(
            "SELECT COUNT(*) AS cnt FROM analyses WHERE analysis_type = $1",
            type,
        )

    total = count_row["cnt"] if count_row else 0
    return {"analyses": rows, "total": total, "page": page, "limit": limit}


@router.get("/whale-library")
async def get_whale_library(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    sort_by: str = Query("score"),
):
    """Get whale library entries from PostgreSQL."""
    pg = request.app.state.pg
    offset = (page - 1) * limit

    allowed_sorts = {"score", "added_at", "nickname"}
    order_col = sort_by if sort_by in allowed_sorts else "score"

    rows = await pg.fetch(
        f"""
        SELECT wl.address, wl.chain, wl.nickname, wl.notes, wl.tags, wl.added_at,
               w.score, w.total_profit_usd, w.win_rate, w.roi, w.trade_count
        FROM whale_library wl
        LEFT JOIN whales w ON wl.address = w.address
        ORDER BY {order_col} DESC NULLS LAST
        LIMIT $1 OFFSET $2
        """,
        limit, offset,
    )
    count_row = await pg.fetchrow("SELECT COUNT(*) AS cnt FROM whale_library")
    total = count_row["cnt"] if count_row else 0

    return {"whales": rows, "total": total, "page": page}
