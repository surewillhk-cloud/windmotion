"""Settings API routes with PostgreSQL backend."""
from fastapi import APIRouter, Request
from typing import Dict
from datetime import datetime, timezone

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("")
async def get_settings(request: Request):
    """Read all settings from PostgreSQL settings table."""
    pg = request.app.state.pg
    rows = await pg.fetch("SELECT key, value FROM settings")

    settings = {}
    for row in rows:
        settings[row["key"]] = row["value"]
    return settings


@router.put("")
async def update_settings(config: Dict, request: Request):
    """Upsert settings into PostgreSQL settings table."""
    pg = request.app.state.pg
    now = datetime.now(timezone.utc)

    for key, value in config.items():
        await pg.execute(
            """
            INSERT INTO settings (key, value, updated_at)
            VALUES ($1, $2, $3)
            ON CONFLICT (key) DO UPDATE SET value = $2, updated_at = $3
            """,
            key, value, now,
        )

    # Return the full settings after update
    rows = await pg.fetch("SELECT key, value FROM settings")
    settings = {}
    for row in rows:
        settings[row["key"]] = row["value"]
    return settings
