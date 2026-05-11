"""Database migration runner for Wind Motion."""
import asyncio
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
logger = logging.getLogger("migrate")


async def run_migrations():
    """Run all pending SQL migrations against PostgreSQL."""
    import asyncpg

    dsn = os.getenv("DATABASE_URL", "postgresql://windmotion:windmotion_dev@localhost:5432/windmotion")

    migrations_dir = os.path.dirname(os.path.abspath(__file__))
    sql_files = sorted(
        f for f in os.listdir(migrations_dir) if f.endswith('.sql')
    )

    if not sql_files:
        logger.info("No migration files found")
        return

    try:
        conn = await asyncpg.connect(dsn)

        # Create migrations tracking table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS _migrations (
                filename VARCHAR(255) PRIMARY KEY,
                applied_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)

        applied = await conn.fetch("SELECT filename FROM _migrations")
        applied_set = {r['filename'] for r in applied}

        for sql_file in sql_files:
            if sql_file in applied_set:
                logger.info(f"  ✓ {sql_file} (already applied)")
                continue

            logger.info(f"  → Applying {sql_file}...")
            path = os.path.join(migrations_dir, sql_file)
            with open(path, 'r') as f:
                sql = f.read()

            try:
                await conn.execute(sql)
                await conn.execute(
                    "INSERT INTO _migrations (filename) VALUES ($1)", sql_file
                )
                logger.info(f"  ✓ {sql_file} applied successfully")
            except Exception as e:
                logger.error(f"  ✗ {sql_file} failed: {e}")
                raise

        await conn.close()
        logger.info("All migrations completed")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_migrations())
