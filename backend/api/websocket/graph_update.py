"""WebSocket endpoint for graph updates."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


@router.websocket("/ws/analysis/{analysis_id}/graph")
async def ws_graph_update(websocket: WebSocket, analysis_id: str):
    await websocket.accept()
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
