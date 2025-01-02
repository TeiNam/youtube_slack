# main.py
import time
import logging
import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from apis.routers import api_router
from utils.config import Config
from utils.db_manager import DatabaseManager
from utils.slack_sender import SlackSender


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
        logger.info(f"Checking {len(channels)} channels for new videos")

        notification_count = 0
        for channel in channels:
            try:
                # 마지막 확인 시간 조회
                last_check = db.get_last_check_time(channel.yt_channel_id)

                # 새 동영상 확인
                new_videos = youtube_api.check_new_videos(channel.yt_channel_id, last_check)

                # 새 동영상이 있으면 알림 전송
                for video in new_videos:
                    success = slack_sender.send_notification(
                        channel.yt_channel_id,
                        video
                    )
                    if success:
                        notification_count += 1

                # 마지막 확인 시간 업데이트
                db.update_last_check_time(channel.yt_channel_id)

            except Exception as e:
                logger.error(f"Error processing channel {channel.yt_channel_id}: {e}")
                continue

        elapsed_time = time.time() - start_time
        logger.info(
            f"Check completed in {elapsed_time:.2f} seconds. "
            f"Sent {notification_count} notifications. "
            f"Quota usage: {youtube_api.get_daily_quota_used()}"
        )

    except Exception as e:
        logger.error(f"Error in check_new_videos: {e}", exc_info=True)

    finally:
        # 다음 실행을 위해 대기
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
app = FastAPI(lifespan=lifespan)
app.include_router(api_router, prefix="/api/v1")


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