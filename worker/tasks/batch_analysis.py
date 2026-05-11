"""Batch Analysis Task - Run analysis on multiple whales.

Used by Filter Results page to analyze a batch of selected whales.
Individual analyses are queued as separate tasks; this task
orchestrates and aggregates results.
"""
import asyncio
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


async def execute(payload: Dict, context: Dict) -> Dict[str, Any]:
    """Execute batch analysis."""
    publish = context["publish_progress"]
    redis = context["redis"]

    addresses: List[str] = payload["addresses"]
    chain = payload.get("chain", "bsc")
    analysis_type = payload.get("type", "reverse")  # forward | reverse
    batch_id = context["task_id"]

    total = len(addresses)
    completed = 0
    failed = 0
    results = {}

    publish(5, f"Starting batch {analysis_type} analysis for {total} whales...")

    # ── Queue individual tasks ───────────────────────────────
    task_ids = []
    for addr in addresses:
        task_id = f"{batch_id}-{addr[:8]}"
        task_ids.append(task_id)

        task_payload = {
            "task_type": f"{analysis_type}_analysis",
            "task_id": task_id,
            "payload": {
                "address": addr,
                "chain": chain,
                "source": "batch",
                "batch_id": batch_id
            }
        }
        await redis.client.rpush("wm:task_queue", json.dumps(task_payload))

    publish(15, f"Queued {total} tasks, waiting for results...")

    # ── Poll for results ─────────────────────────────────────
    for i, task_id in enumerate(task_ids):
        addr = addresses[i]
        max_wait = 600  # 10 min per task
        waited = 0

        while waited < max_wait:
            result_data = await redis.get(f"wm:result:{task_id}")
            if result_data:
                result = json.loads(result_data)
                if result.get("status") == "completed":
                    results[addr] = result.get("result", {})
                    completed += 1
                else:
                    results[addr] = {"error": result.get("error", "Unknown error")}
                    failed += 1
                break

            await asyncio.sleep(5)
            waited += 5

            # Update progress
            pct = 15 + int((i + waited / max_wait) / total * 80)
            publish(pct, f"Waiting for {addr[:10]}... ({i + 1}/{total})")

        if waited >= max_wait:
            results[addr] = {"error": "Timeout"}
            failed += 1

        pct = 15 + int((i + 1) / total * 80)
        publish(pct, f"Completed {i + 1}/{total}")

    # ── Aggregate ────────────────────────────────────────────
    publish(95, "Aggregating results...")
    summary = {
        "total": total,
        "completed": completed,
        "failed": failed,
        "avg_score": _avg_score(results),
        "top_whale": _top_whale(results)
    }

    publish(100, f"Batch complete: {completed}/{total} succeeded")

    return {
        "batch_id": batch_id,
        "analysis_type": analysis_type,
        "summary": summary,
        "results": results
    }


def _avg_score(results: Dict) -> float:
    scores = []
    for r in results.values():
        if "error" not in r:
            score = r.get("report", {}).get("score") or r.get("factor_scores", {}).get("F1", 0)
            if score:
                scores.append(float(score))
    return round(sum(scores) / len(scores), 1) if scores else 0


def _top_whale(results: Dict) -> str:
    best = None
    best_score = -1
    for addr, r in results.items():
        if "error" in r:
            continue
        score = r.get("report", {}).get("score") or 0
        if score > best_score:
            best_score = score
            best = addr
    return best or ""
