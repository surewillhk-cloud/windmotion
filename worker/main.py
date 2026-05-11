"""Wind Motion - Async Worker Service.

Consumes heavy analysis tasks from Redis queue, executes multi-agent
pipelines, and publishes progress/results back via Redis pub/sub.

Architecture:
    Backend API → Redis Queue → Worker → Redis Pub/Sub → Backend WS → Frontend

Tasks:
    - forward_analysis  : 6-phase forward inference pipeline
    - reverse_analysis  : 5-step reverse inference
    - whale_screen      : periodic whale discovery & scoring
    - graph_sync        : sync causal graph to Neo4j
    - batch_analysis    : batch analysis for filter results
    - smart_recommend   : generate recommendations
"""
import asyncio
import json
import logging
import os
import signal
import sys
import time
from contextlib import asynccontextmanager
from typing import Dict, Optional

import redis.asyncio as aioredis

from backend.db.postgres import PostgresClient
from backend.db.neo4j_client import Neo4jClient
from backend.db.redis_client import RedisClient
from backend.agents.pool import AgentPool
from backend.skills.model_route import ModelRouter

logger = logging.getLogger("windmotion.worker")

# ─── Configuration ──────────────────────────────────────────────
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://windmotion:windmotion_dev@localhost:5432/windmotion")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "windmotion_dev")

QUEUE_KEY = "wm:task_queue"
RESULT_PREFIX = "wm:result:"
PROGRESS_CHANNEL = "wm:progress"
HEARTBEAT_KEY = "wm:worker:heartbeat"
MAX_CONCURRENT = int(os.getenv("WORKER_CONCURRENCY", "3"))
TASK_TIMEOUT = int(os.getenv("TASK_TIMEOUT", "600"))  # 10 min default


# ─── Task Registry ──────────────────────────────────────────────
TASK_REGISTRY: Dict[str, str] = {
    "forward_analysis":  "worker.tasks.forward_analysis",
    "reverse_analysis":  "worker.tasks.reverse_analysis",
    "whale_screen":      "worker.tasks.whale_screen",
    "graph_sync":        "worker.tasks.graph_sync",
    "batch_analysis":    "worker.tasks.batch_analysis",
    "smart_recommend":   "worker.tasks.smart_recommend",
}


class Worker:
    """Main worker process that consumes and executes tasks."""

    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self.pg: Optional[PostgresClient] = None
        self.neo4j: Optional[Neo4jClient] = None
        self.agent_pool: Optional[AgentPool] = None
        self.model_router: Optional[ModelRouter] = None
        self.running = False
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.semaphore: Optional[asyncio.Semaphore] = None
        self.worker_id = f"worker-{os.getpid()}"

    async def start(self):
        """Initialize connections and start consuming."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
        )
        logger.info(f"Starting {self.worker_id} (concurrency={MAX_CONCURRENT})")

        # Connect to Redis
        self.redis = aioredis.from_url(REDIS_URL, decode_responses=True)
        await self.redis.ping()
        logger.info("Redis connected")

        # Connect to PostgreSQL
        self.pg = PostgresClient(DATABASE_URL)
        await self.pg.connect()
        logger.info("PostgreSQL connected")

        # Connect to Neo4j
        self.neo4j = Neo4jClient(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
        await self.neo4j.connect()
        logger.info("Neo4j connected")

        # Initialize agent pool and model router
        self.agent_pool = AgentPool()
        await self.agent_pool.initialize()
        logger.info(f"Agent pool ready ({len(self.agent_pool.agents)} agents)")

        self.model_router = ModelRouter()
        logger.info("Model router ready")

        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        self.running = True

        # Start heartbeat
        asyncio.create_task(self._heartbeat_loop())

        logger.info(f"{self.worker_id} ready, listening on {QUEUE_KEY}")

    async def stop(self):
        """Graceful shutdown."""
        logger.info(f"Shutting down {self.worker_id}...")
        self.running = False

        # Cancel active tasks
        for task_id, task in self.active_tasks.items():
            logger.info(f"Cancelling task {task_id}")
            task.cancel()

        if self.active_tasks:
            await asyncio.gather(*self.active_tasks.values(), return_exceptions=True)

        # Close connections
        if self.neo4j:
            await self.neo4j.close()
        if self.pg:
            await self.pg.close()
        if self.redis:
            await self.redis.close()

        logger.info(f"{self.worker_id} stopped")

    async def consume(self):
        """Main consume loop - pops tasks from Redis queue."""
        while self.running:
            try:
                # Block-pop from queue (timeout to check self.running)
                result = await self.redis.blpop(QUEUE_KEY, timeout=2)
                if not result:
                    continue

                _, raw = result
                task_data = json.loads(raw)
                task_id = task_data.get("task_id", "unknown")
                task_type = task_data.get("task_type", "unknown")

                logger.info(f"Received task: {task_type} ({task_id})")

                if task_type not in TASK_REGISTRY:
                    logger.warning(f"Unknown task type: {task_type}")
                    await self._publish_result(task_id, {
                        "status": "failed",
                        "error": f"Unknown task type: {task_type}"
                    })
                    continue

                # Acquire semaphore (limit concurrency)
                async with self.semaphore:
                    task = asyncio.create_task(
                        self._execute_task(task_id, task_type, task_data)
                    )
                    self.active_tasks[task_id] = task
                    try:
                        await task
                    except asyncio.CancelledError:
                        logger.info(f"Task {task_id} cancelled")
                    finally:
                        self.active_tasks.pop(task_id, None)

            except asyncio.CancelledError:
                break
            except json.JSONDecodeError as e:
                logger.error(f"Invalid task JSON: {e}")
            except Exception as e:
                logger.error(f"Consume error: {e}", exc_info=True)
                await asyncio.sleep(1)

    async def _execute_task(self, task_id: str, task_type: str, task_data: Dict):
        """Execute a single task with timeout and error handling."""
        start = time.time()

        # Mark task as running
        await self._publish_progress(task_id, task_type, "running", 0, "Task started")

        try:
            # Dynamic import of task module
            module_path = TASK_REGISTRY[task_type]
            module = __import__(module_path, fromlist=["execute"])
            
            # Build context for the task
            context = {
                "task_id": task_id,
                "redis": self.redis,
                "pg": self.pg,
                "neo4j": self.neo4j,
                "agent_pool": self.agent_pool,
                "model_router": self.model_router,
                "publish_progress": lambda pct, msg: asyncio.ensure_future(
                    self._publish_progress(task_id, task_type, "running", pct, msg)
                ),
            }

            # Execute with timeout
            result = await asyncio.wait_for(
                module.execute(task_data.get("payload", {}), context),
                timeout=task_data.get("timeout", TASK_TIMEOUT)
            )

            elapsed = time.time() - start
            logger.info(f"Task {task_id} completed in {elapsed:.1f}s")

            # Publish result
            await self._publish_result(task_id, {
                "status": "completed",
                "task_type": task_type,
                "result": result,
                "elapsed_s": round(elapsed, 1)
            })

            await self._publish_progress(task_id, task_type, "completed", 100, "Done")

        except asyncio.TimeoutError:
            elapsed = time.time() - start
            logger.error(f"Task {task_id} timed out after {elapsed:.1f}s")
            await self._publish_result(task_id, {
                "status": "timeout",
                "task_type": task_type,
                "error": f"Task exceeded {TASK_TIMEOUT}s limit"
            })
            await self._publish_progress(task_id, task_type, "failed", 0, "Timeout")

        except Exception as e:
            elapsed = time.time() - start
            logger.error(f"Task {task_id} failed: {e}", exc_info=True)
            await self._publish_result(task_id, {
                "status": "failed",
                "task_type": task_type,
                "error": str(e),
                "elapsed_s": round(elapsed, 1)
            })
            await self._publish_progress(task_id, task_type, "failed", 0, str(e))

    async def _publish_result(self, task_id: str, result: Dict):
        """Store task result in Redis (TTL 1h)."""
        await self.redis.set(
            f"{RESULT_PREFIX}{task_id}",
            json.dumps(result, ensure_ascii=False, default=str),
            ex=3600
        )

    async def _publish_progress(self, task_id: str, task_type: str,
                                 status: str, pct: float, message: str):
        """Publish progress event to Redis pub/sub channel."""
        event = {
            "task_id": task_id,
            "task_type": task_type,
            "status": status,
            "progress_pct": pct,
            "message": message,
            "worker_id": self.worker_id,
            "timestamp": time.time()
        }
        await self.redis.publish(PROGRESS_CHANNEL, json.dumps(event, default=str))

    async def _heartbeat_loop(self):
        """Periodic heartbeat so backend knows worker is alive."""
        while self.running:
            try:
                await self.redis.set(HEARTBEAT_KEY, json.dumps({
                    "worker_id": self.worker_id,
                    "active_tasks": len(self.active_tasks),
                    "timestamp": time.time()
                }), ex=30)
            except Exception:
                pass
            await asyncio.sleep(10)


# ─── Entry Point ────────────────────────────────────────────────
async def main():
    worker = Worker()
    loop = asyncio.get_event_loop()

    # Graceful shutdown on SIGTERM/SIGINT
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(worker.stop()))

    await worker.start()
    await worker.consume()


if __name__ == "__main__":
    asyncio.run(main())
