# utils/config.py
import os
from dotenv import load_dotenv
from utils.youtube_api import YouTubeAPI

load_dotenv()

class Config:
    # YouTube API 설정
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    if not YOUTUBE_API_KEY:
        raise ValueError("YOUTUBE_API_KEY must be set in environment variables")

    # YouTube API 인스턴스 초기화
    YOUTUBE_API = YouTubeAPI.initialize(YOUTUBE_API_KEY)

    # 새 영상 체크 간격 (기본 30분)
    CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '1800'))