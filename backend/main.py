"""Wind Motion - Main FastAPI Application."""
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger("windmotion")
logger.info(f"Starting on port {os.getenv('PORT', '8080')}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    logger.info("Wind Motion starting up...")

    # Initialize DB connections (non-fatal if they fail)
    from backend.db.postgres import PostgresClient
    from backend.db.neo4j_client import Neo4jClient
    from backend.db.redis_client import RedisClient

    pg = PostgresClient()
    neo = Neo4jClient()
    redis = RedisClient()

    # Connect with timeouts to prevent startup hang
    import asyncio
    try:
        await asyncio.wait_for(pg.connect(), timeout=10)
    except Exception as e:
        logger.warning(f"PostgreSQL connection failed (will retry later): {e}")

    try:
        await asyncio.wait_for(neo.connect(), timeout=10)
    except Exception as e:
        logger.warning(f"Neo4j connection failed (will retry later): {e}")

    try:
        await asyncio.wait_for(redis.connect(), timeout=10)
    except Exception as e:
        logger.warning(f"Redis connection failed (will retry later): {e}")

    app.state.pg = pg
    app.state.neo = neo
    app.state.redis = redis
    logger.info("Wind Motion started successfully")

    yield

    logger.info("Wind Motion shutting down...")
    try:
        await pg.disconnect()
    except Exception:
        pass
    try:
        await neo.disconnect()
    except Exception:
        pass
    try:
        await redis.disconnect()
    except Exception:
        pass


app = FastAPI(
    title="Wind Motion API",
    description="链上交易推演引擎 API",
    version="0.1.0",
    lifespan=lifespan
)

# CORS - allow configured origins + common dev/production patterns
cors_raw = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:5173,http://localhost:8080"
)

# Support both JSON array and comma-separated formats
import json as _json
try:
    allowed_origins = _json.loads(cors_raw) if cors_raw.strip().startswith("[") else [o.strip() for o in cors_raw.split(",")]
except _json.JSONDecodeError:
    allowed_origins = [o.strip() for o in cors_raw.split(",")]

# Also allow any *.railway.app or *.up.railway.app in production
if os.getenv("RAILWAY_PUBLIC_DOMAIN"):
    allowed_origins.append(f"https://{os.getenv('RAILWAY_PUBLIC_DOMAIN')}")
if os.getenv("FRONTEND_URL"):
    allowed_origins.append(os.getenv("FRONTEND_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in allowed_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and register routes
from backend.api.routes import whale, filter, analysis, reverse, replay, history, embed, settings
from backend.api.websocket import progress, graph_update, feed

app.include_router(whale.router)
app.include_router(filter.router)
app.include_router(analysis.router)
app.include_router(reverse.router)
app.include_router(replay.router)
app.include_router(history.router)
app.include_router(embed.router)
app.include_router(settings.router)
app.include_router(progress.router)
app.include_router(graph_update.router)
app.include_router(feed.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "windmotion"}


@app.get("/")
async def root():
    return {
        "name": "Wind Motion API",
        "version": "0.1.0",
        "docs": "/docs"
    }


# Serve frontend static files in production (single-service Railway deployment)
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="static-assets")

    from fastapi.responses import FileResponse

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve Vue SPA - all non-API routes return index.html."""
        file_path = frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(frontend_dist / "index.html"))
