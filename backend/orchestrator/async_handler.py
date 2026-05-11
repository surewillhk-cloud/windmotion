"""Async Handler - Manages parallel and sequential task execution."""
import asyncio
import logging
from typing import Dict, List, Callable, Any, Optional

logger = logging.getLogger(__name__)


class AsyncHandler:
    """Handles async execution of skills and agent tasks."""

    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._running_tasks: Dict[str, asyncio.Task] = {}

    async def run_with_semaphore(self, task_id: str, coro):
        async with self._semaphore:
            try:
                return await coro
            except Exception as e:
                logger.error(f"Task {task_id} failed: {e}")
                raise

    async def run_parallel(self, tasks: List[Dict[str, Any]]) -> List[Any]:
        """Run multiple tasks in parallel with concurrency limit."""
        async_tasks = []
        for task in tasks:
            task_id = task.get("id", "unknown")
            handler = task["handler"]
            args = task.get("args", {})
            async_tasks.append(self.run_with_semaphore(task_id, handler(**args)))

        results = await asyncio.gather(*async_tasks, return_exceptions=True)
        return results

    async def run_parallel_agents(self, agents: List[Dict], prompt: str,
                                  model_router: Any) -> List[Dict]:
        """Run multiple agent reasoning tasks in parallel."""
        async def run_agent(agent_info: Dict) -> Dict:
            agent = agent_info["agent"]
            tier = agent_info.get("model_tier", agent.model_tier)
            system_prompt = agent.get_system_prompt()
            # In production: call LLM via model_router
            return {
                "agent_id": agent.id,
                "agent_name": agent.name,
                "result": "reasoning_output",
                "model_tier": tier
            }

        tasks = [{"id": a["agent"].id, "handler": run_agent, "args": {"agent_info": a}} for a in agents]
        return await self.run_parallel(tasks)

    async def run_with_timeout(self, coro, timeout_s: float, default=None):
        """Run a coroutine with timeout, returning default on timeout."""
        try:
            return await asyncio.wait_for(coro, timeout=timeout_s)
        except asyncio.TimeoutError:
            logger.warning(f"Task timed out after {timeout_s}s")
            return default

    def cancel_all(self):
        for task_id, task in self._running_tasks.items():
            if not task.done():
                task.cancel()
                logger.info(f"Cancelled task {task_id}")
        self._running_tasks.clear()
