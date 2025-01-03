# main.py
import time
import logging
import asyncio
from dotenv import load_dotenv
import os

from datetime import timedelta
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apis.routers import api_router
from utils.config import Config
from utils.db_manager import DatabaseManager
from utils.slack_sender import SlackSender
from utils.time_utils import get_current_utc, format_utc


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 공유 객체
db = DatabaseManager()
youtube_api = Config.YOUTUBE_API
slack_sender = SlackSender(db)

# 백그라운드 작업 상태
is_running = False
background_task = None


async def check_new_videos():
    """새로운 영상을 확인하고 알림을 보냅니다."""
    global is_running
    try:
        logger.info("Checking for new videos...")
        start_time = time.time()

        # 모든 채널 조회
        channels = db.get_all_channels()
        if not channels:
            logger.info("No channels to check")
            return

        logger.info(f"Checking {len(channels)} channels for new videos")

        # 채널 정보 준비
        channel_infos = [
            {
                'yt_channel_id': ch.yt_channel_id,
                'yt_ch_name': ch.yt_ch_name
            }
            for ch in channels
        ]

        # 최신 동영상 배치 조회
        try:
            last_check = get_current_utc() - timedelta(hours=1)  # 1시간 전부터 체크
            new_videos_by_channel = youtube_api.check_new_videos_batch(
                channel_infos,
                last_check
            )
        except Exception as e:
            logger.error(f"Error checking new videos: {e}")
            return

        # 알림 전송
        notification_count = 0
        for channel in channels:
            new_videos = new_videos_by_channel.get(channel.yt_channel_id, [])

            for video in new_videos:
                success = slack_sender.send_notification(
                    channel.yt_channel_id,
                    {
                        'title': video['title'],
                        'url': f"https://www.youtube.com/watch?v={video['video_id']}",
                        'published_at': format_utc(video['published_at'])
                    }
                )
                if success:
                    notification_count += 1

            # 마지막 확인 시간 업데이트
            if new_videos:
                db.update_last_check_time(channel.yt_channel_id)

        elapsed_time = time.time() - start_time
        logger.info(
            f"Check completed in {elapsed_time:.2f} seconds. "
            f"Sent {notification_count} notifications. "
            f"Quota usage: {youtube_api.get_daily_quota_used()}"
        )

    except Exception as e:
        logger.error(f"Error in check_new_videos: {e}", exc_info=True)

    finally:
        if is_running:
            await asyncio.sleep(Config.CHECK_INTERVAL)
            asyncio.create_task(check_new_videos())


async def start_background_task():
    """백그라운드 작업을 시작합니다."""
    global is_running, background_task
    if not is_running:
        is_running = True
        background_task = asyncio.create_task(check_new_videos())
        logger.info("Background task started")


async def stop_background_task():
    """백그라운드 작업을 중지합니다."""
    global is_running, background_task
    if is_running:
        is_running = False
        if background_task:
            background_task.cancel()
        logger.info("Background task stopped")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시
    await start_background_task()
    yield
    # 종료 시
    await stop_background_task()


# FastAPI 애플리케이션 생성
# .env 파일 로드
load_dotenv()

# 환경 변수에서 API 호스트와 포트 가져오기
API_HOST = os.getenv('VITE_API_HOST', 'http://localhost')
API_PORT = os.getenv('VITE_API_PORT', '8000')

app = FastAPI(lifespan=lifespan)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"{API_HOST}:{API_PORT}"],  # 환경 변수에서 가져온 주소 사용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"status": "running"}

# 서비스 상태 확인 엔드포인트
@app.get("/status")
async def get_status():
    return {
        "status": "running",
        "background_task_running": is_running,
        "youtube_api_quota_used": youtube_api.get_daily_quota_used()
    }


# 백그라운드 작업 제어 엔드포인트
@app.post("/background/start")
async def start_task():
    await start_background_task()
    return {"status": "started"}


@app.post("/background/stop")
async def stop_task():
    await stop_background_task()
    return {"status": "stopped"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)