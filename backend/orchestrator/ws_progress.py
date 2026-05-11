"""WebSocket Progress - Pushes analysis progress to connected clients."""
import asyncio
import json
import logging
from typing import Dict, Set, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ProgressEvent:
    analysis_id: str
    phase: str
    step: str
    status: str  # running, completed, failed
    progress_pct: float
    message: str
    data: Dict = field(default_factory=dict)
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat() + "Z"

    def to_json(self) -> str:
        return json.dumps({
            "analysis_id": self.analysis_id,
            "phase": self.phase,
            "step": self.step,
            "status": self.status,
            "progress_pct": self.progress_pct,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp
        }, ensure_ascii=False)


class WSProgressManager:
    """Manages WebSocket connections and progress broadcasting."""

    def __init__(self):
        self.connections: Dict[str, Set] = {}  # analysis_id -> set of websocket connections
        self.latest_progress: Dict[str, ProgressEvent] = {}

    async def subscribe(self, analysis_id: str, websocket):
        if analysis_id not in self.connections:
            self.connections[analysis_id] = set()
        self.connections[analysis_id].add(websocket)
        # Send latest progress if available
        if analysis_id in self.latest_progress:
            try:
                await websocket.send_text(self.latest_progress[analysis_id].to_json())
            except Exception:
                pass

    def unsubscribe(self, analysis_id: str, websocket):
        if analysis_id in self.connections:
            self.connections[analysis_id].discard(websocket)
            if not self.connections[analysis_id]:
                del self.connections[analysis_id]

    async def broadcast(self, event: ProgressEvent):
        self.latest_progress[event.analysis_id] = event
        connections = self.connections.get(event.analysis_id, set())
        if not connections:
            return

        message = event.to_json()
        dead = set()
        for ws in connections:
            try:
                await ws.send_text(message)
            except Exception:
                dead.add(ws)

        for ws in dead:
            connections.discard(ws)

    async def notify_phase_start(self, analysis_id: str, phase: str, message: str):
        await self.broadcast(ProgressEvent(
            analysis_id=analysis_id,
            phase=phase,
            step="start",
            status="running",
            progress_pct=self._phase_progress(phase, "start"),
            message=message
        ))

    async def notify_phase_complete(self, analysis_id: str, phase: str, data: Dict = None):
        await self.broadcast(ProgressEvent(
            analysis_id=analysis_id,
            phase=phase,
            step="complete",
            status="completed",
            progress_pct=self._phase_progress(phase, "complete"),
            message=f"{phase} completed",
            data=data or {}
        ))

    async def notify_step(self, analysis_id: str, phase: str, step: str,
                         progress: float, message: str, data: Dict = None):
        await self.broadcast(ProgressEvent(
            analysis_id=analysis_id,
            phase=phase,
            step=step,
            status="running",
            progress_pct=progress,
            message=message,
            data=data or {}
        ))

    async def notify_error(self, analysis_id: str, phase: str, error: str):
        await self.broadcast(ProgressEvent(
            analysis_id=analysis_id,
            phase=phase,
            step="error",
            status="failed",
            progress_pct=0,
            message=error
        ))

    async def notify_graph_update(self, analysis_id: str, graph_data: Dict):
        await self.broadcast(ProgressEvent(
            analysis_id=analysis_id,
            phase="graph",
            step="update",
            status="running",
            progress_pct=0,
            message="Graph updated",
            data={"graph": graph_data}
        ))

    async def notify_probability_update(self, analysis_id: str, prob_data: Dict):
        await self.broadcast(ProgressEvent(
            analysis_id=analysis_id,
            phase="probability",
            step="update",
            status="running",
            progress_pct=0,
            message="Probability updated",
            data=prob_data
        ))

    def _phase_progress(self, phase: str, step: str) -> float:
        phases = {
            "phase_0": 0, "phase_1": 15, "phase_2": 35,
            "phase_3": 60, "phase_4": 75, "phase_5": 90
        }
        base = phases.get(phase, 0)
        return base + (10 if step == "complete" else 0)
