"""Embed API routes - serves embed case data."""
from fastapi import APIRouter, HTTPException
import json
import os

router = APIRouter(prefix="/api/embed", tags=["embed"])


@router.get("/cases")
async def list_embed_cases():
    """List available embed cases."""
    cases_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'frontend', 'embed', 'cases')
    cases = []
    if os.path.exists(cases_dir):
        for f in os.listdir(cases_dir):
            if f.endswith('.json'):
                with open(os.path.join(cases_dir, f), 'r') as fh:
                    data = json.load(fh)
                    cases.append({
                        "id": data.get("id", f.replace('.json', '')),
                        "title": data.get("title", ""),
                        "description": data.get("description", ""),
                        "token": data.get("token", ""),
                        "result": data.get("result", "")
                    })
    return {"cases": cases}


@router.get("/cases/{case_id}")
async def get_embed_case(case_id: str):
    """Get embed case data."""
    cases_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'frontend', 'embed', 'cases')
    filepath = os.path.join(cases_dir, f"{case_id}.json")
    if not os.path.exists(filepath):
        raise HTTPException(404, "Case not found")
    with open(filepath, 'r') as f:
        return json.load(f)
