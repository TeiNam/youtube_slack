# apis/models.py
from pydantic import BaseModel, HttpUrl, constr
from datetime import datetime

# 웹훅 모델
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

# 채널 모델
class ChannelCreate(BaseModel):
    webhook_id: int
    yt_handling_id: constr(min_length=1, max_length=30)

class ChannelResponse(BaseModel):
    id: int
    webhook_id: int
    yt_channel_id: str
    yt_handling_id: str
    yt_ch_name: str
    create_at: datetime
    update_at: datetime