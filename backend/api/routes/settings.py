"""Settings API routes."""
from fastapi import APIRouter
from typing import Dict

router = APIRouter(prefix="/api/settings", tags=["settings"])

_settings: Dict = {
    "language": "zh-CN",
    "model_routing": {
        "heavy": "deepseek-r1",
        "medium": "deepseek-v3",
        "light": "qwen-turbo"
    },
    "notifications": {
        "email": False,
        "telegram": False,
        "webhook": False
    },
    "cost_limits": {
        "daily_budget_cny": 100,
        "single_analysis_max_cny": 10
    }
}


@router.get("")
async def get_settings():
    return _settings


@router.put("")
async def update_settings(config: Dict):
    _settings.update(config)
    return _settings
