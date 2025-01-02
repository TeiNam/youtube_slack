# apis/channel.py
from fastapi import APIRouter, HTTPException
from typing import List
from utils.db_manager import DatabaseManager
from utils.config import Config
from apis.models import ChannelCreate, ChannelResponse

router = APIRouter()
db = DatabaseManager()
youtube_api = Config.YOUTUBE_API

@router.post("/channels", response_model=ChannelResponse, status_code=201)
async def create_channel(channel: ChannelCreate):
    """핸들링 ID와 웹훅 ID로 새로운 채널을 등록합니다."""
    try:
        # 웹훅 존재 여부 확인
        webhook = db.get_webhook(channel.webhook_id)
        if webhook is None:
            raise HTTPException(status_code=404, detail="Webhook not found")

        # 채널이 이미 존재하는지 확인
        existing_channel = db.get_channel_by_handling_id(channel.yt_handling_id)
        if existing_channel:
            raise HTTPException(
                status_code=400,
                detail="Channel with this handling ID already exists"
            )

        # YouTube API를 통해 채널 정보 조회
        try:
            channel_info = youtube_api.get_channel_info(channel.yt_handling_id)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to get YouTube channel info: {str(e)}"
            )

        # 채널 등록
        channel_id = db.add_channel(
            webhook_id=channel.webhook_id,
            yt_channel_id=channel_info['channel_id'],
            yt_handling_id=channel.yt_handling_id,
            yt_ch_name=channel_info['channel_name']
        )

        created_channel = db.get_channel_by_id(channel_id)
        if created_channel is None:
            raise HTTPException(status_code=500, detail="Failed to create channel")
        return created_channel

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/channels", response_model=List[ChannelResponse])
async def list_channels():
    """등록된 모든 채널 목록을 조회합니다."""
    try:
        channels = db.get_all_channels()
        return channels
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve channels: {str(e)}")

@router.delete("/channels/{channel_id}", status_code=204)
async def delete_channel(channel_id: int):
    """채널을 삭제합니다."""
    success = db.delete_channel(channel_id)
    if not success:
        raise HTTPException(status_code=404, detail="Channel not found")