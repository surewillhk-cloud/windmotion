"""Wind Motion - Main FastAPI Application."""
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger("windmotion")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    logger.info("Wind Motion starting up...")
    # Initialize DB connections here
    yield
    logger.info("Wind Motion shutting down...")


app = FastAPI(
    title="Wind Motion API",
    description="链上交易推演引擎 API",
    version="0.1.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
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
