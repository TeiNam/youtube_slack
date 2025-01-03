# apis/status.py
from fastapi import APIRouter
from typing import Dict, Any
from utils.config import Config
from utils.db_manager import DatabaseManager

router = APIRouter()

@router.get("/system/status")
async def get_system_status() -> Dict[str, Any]:
    """시스템 상태를 반환합니다."""
    youtube_api = Config.YOUTUBE_API
    return {
        "status": "running",
        "background_task_running": True,  # main.py의 background task 상태에 따라 변경
        "youtube_api_quota_used": youtube_api.get_daily_quota_used()
    }