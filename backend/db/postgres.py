"""PostgreSQL database connection and operations."""
import os
import logging
from typing import Optional, Dict, List, Any
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class PostgresClient:
    """Async PostgreSQL client using asyncpg."""

    def __init__(self, dsn: Optional[str] = None):
        self.dsn = dsn or os.getenv("DATABASE_URL", "postgresql://windmotion:windmotion_dev@localhost:5432/windmotion")
        self.pool = None

    async def connect(self):
        try:
            import asyncpg
            import asyncio
            self.pool = await asyncio.wait_for(
                asyncpg.create_pool(self.dsn, min_size=1, max_size=5, timeout=5),
                timeout=15
            )
            logger.info("PostgreSQL connected")
        except ImportError:
            logger.warning("asyncpg not installed, using mock mode")
            self.pool = None
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            self.pool = None

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    @asynccontextmanager
    async def acquire(self):
        if self.pool:
            async with self.pool.acquire() as conn:
                yield conn
        else:
            yield None

    async def execute(self, query: str, *args) -> Any:
        async with self.acquire() as conn:
            if conn:
                return await conn.execute(query, *args)
            logger.warning("No DB connection, query skipped")
            return None

    async def fetch(self, query: str, *args) -> List[Dict]:
        async with self.acquire() as conn:
            if conn:
                rows = await conn.fetch(query, *args)
                return [dict(r) for r in rows]
            return []

    async def fetchrow(self, query: str, *args) -> Optional[Dict]:
        async with self.acquire() as conn:
            if conn:
                row = await conn.fetchrow(query, *args)
                return dict(row) if row else None
            return None

    async def init_tables(self):
        """Initialize database tables."""
        await self.execute("""
            CREATE TABLE IF NOT EXISTS whales (
                address VARCHAR(42) PRIMARY KEY,
                chain VARCHAR(10) DEFAULT 'bsc',
                total_profit_usd DECIMAL DEFAULT 0,
                win_rate DECIMAL DEFAULT 0,
                roi DECIMAL DEFAULT 0,
                trade_count INTEGER DEFAULT 0,
                token_count INTEGER DEFAULT 0,
                score DECIMAL DEFAULT 0,
                labels JSONB DEFAULT '[]',
                strategy_patterns JSONB DEFAULT '[]',
                first_seen TIMESTAMPTZ,
                last_active TIMESTAMPTZ,
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS transactions (
                hash VARCHAR(66) PRIMARY KEY,
                from_address VARCHAR(42),
                to_address VARCHAR(42),
                chain VARCHAR(10) DEFAULT 'bsc',
                block_number BIGINT,
                timestamp TIMESTAMPTZ,
                value_usd DECIMAL DEFAULT 0,
                token_address VARCHAR(42),
                token_symbol VARCHAR(20),
                token_amount DECIMAL DEFAULT 0,
                tx_type VARCHAR(20),
                dex VARCHAR(30),
                metadata JSONB DEFAULT '{}'
            );

            CREATE TABLE IF NOT EXISTS filters (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(100),
                config JSONB,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS analyses (
                id VARCHAR(36) PRIMARY KEY,
                whale_address VARCHAR(42),
                analysis_type VARCHAR(20),
                status VARCHAR(20) DEFAULT 'pending',
                mode VARCHAR(20) DEFAULT 'deep',
                chain VARCHAR(10) DEFAULT 'bsc',
                progress_pct DECIMAL DEFAULT 0,
                current_phase VARCHAR(50),
                started_at TIMESTAMPTZ,
                completed_at TIMESTAMPTZ,
                duration_s DECIMAL DEFAULT 0,
                report JSONB,
                graph JSONB,
                factor_scores JSONB,
                matched_patterns JSONB DEFAULT '[]',
                error TEXT,
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS whale_library (
                address VARCHAR(42) PRIMARY KEY,
                alias VARCHAR(100),
                notes TEXT,
                tags JSONB DEFAULT '[]',
                added_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
