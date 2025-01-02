# apis/models.py
from pydantic import BaseModel, HttpUrl, constr
from datetime import datetime

class WebhookCreate(BaseModel):
    workspace_name: constr(min_length=1, max_length=30)
    webhook_name: constr(min_length=1, max_length=20)
    url: HttpUrl

class WebhookResponse(BaseModel):
    webhook_id: int
    workspace_name: str
    webhook_name: str
    url: str
    create_at: datetime
    update_at: datetime

# apis/webhook.py
from fastapi import APIRouter, HTTPException
from typing import List
from utils.db_manager import DatabaseManager
from .models import WebhookCreate, WebhookResponse

router = APIRouter()
db = DatabaseManager()

@router.post("/webhooks", response_model=WebhookResponse, status_code=201)
async def create_webhook(webhook: WebhookCreate):
    """새로운 웹훅을 등록합니다."""
    try:
        webhook_id = db.add_webhook(
            workspace_name=webhook.workspace_name,
            webhook_name=webhook.webhook_name,
            url=str(webhook.url)
        )
        created_webhook = db.get_webhook(webhook_id)
        if created_webhook:
            return created_webhook
        raise HTTPException(status_code=500, detail="Failed to create webhook")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/webhooks", response_model=List[WebhookResponse])
async def list_webhooks():
    """등록된 모든 웹훅 목록을 조회합니다."""
    return db.get_all_webhooks()

@router.delete("/webhooks/{webhook_id}", status_code=204)
async def delete_webhook(webhook_id: int):
    """웹훅을 삭제합니다."""
    # 연결된 채널이 있는지 확인
    channels = db.get_channels_by_webhook(webhook_id)
    if channels:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete webhook with associated channels"
        )

    success = db.delete_webhook(webhook_id)
    if not success:
        raise HTTPException(status_code=404, detail="Webhook not found")