"""WebSocket endpoint for analysis progress."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/analysis/{analysis_id}/progress")
async def ws_analysis_progress(websocket: WebSocket, analysis_id: str):
    await websocket.accept()
    try:
        while True:
            # Keep connection alive, progress pushed by WSProgressManager
            data = await websocket.receive_text()
            # Client can send ping/pong
    except WebSocketDisconnect:
        logger.info(f"WS disconnected: {analysis_id}")
    except Exception as e:
        logger.error(f"WS error: {e}")
