# utils/youtube_api.py
import logging
from functools import wraps
from datetime import datetime
from googleapiclient.discovery import build
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


def log_api_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        try:
            result = func(*args, **kwargs)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"YouTube API call: {func.__name__} - Duration: {duration}s")
            return result
        except Exception as e:
            logger.error(f"YouTube API error in {func.__name__}: {str(e)}")
            raise

    return wrapper


class YouTubeAPI:
    _instance = None

    def __init__(self):
        self.youtube = None
        self._daily_quota_used = 0

    @classmethod
    def initialize(cls, api_key: str):
        if cls._instance is None:
            cls._instance = cls()
            cls._instance.youtube = build('youtube', 'v3', developerKey=api_key)
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise RuntimeError("YouTubeAPI not initialized. Call initialize() first")
        return cls._instance

    @log_api_call
    def get_channel_info(self, handling_id: str) -> Dict[str, str]:
        """채널 핸들링 ID를 채널 ID로 변환합니다.

        Args:
            handling_id: 채널 핸들링 ID (@username 형식) 또는 채널 ID

        Returns:
            dict: {'channel_id': str, 'channel_name': str}

        Raises:
            ValueError: 채널을 찾을 수 없는 경우
        """
        try:
            clean_handling_id = handling_id.lstrip('@')

            # 이미 채널 ID인 경우
            if clean_handling_id.startswith('UC'):
                self._daily_quota_used += 1
                response = self.youtube.channels().list(
                    id=clean_handling_id,
                    part='snippet'
                ).execute()
            else:
                # username으로 시도 (quota: 1)
                self._daily_quota_used += 1
                response = self.youtube.channels().list(
                    forUsername=clean_handling_id,
                    part='id,snippet'
                ).execute()

                # 실패 시 검색 시도 (quota: 100)
                if not response.get('items'):
                    self._daily_quota_used += 100
                    response = self.youtube.search().list(
                        q=handling_id,
                        type='channel',
                        part='snippet',
                        maxResults=1
                    ).execute()

            if not response.get('items'):
                raise ValueError(f"Channel not found for handling ID: {handling_id}")

            item = response['items'][0]
            return {
                'channel_id': item.get('id', {}).get('channelId', item.get('id')),
                'channel_name': item['snippet']['title']
            }

        except Exception as e:
            logger.error(f"Error getting channel info for {handling_id}: {e}")
            raise ValueError(f"Failed to get channel info: {str(e)}")

    # utils/youtube_api.py

    @log_api_call
    def check_new_videos_batch(self, channels: List[dict], last_check_time: datetime) -> Dict[str, List[Dict]]:
        """여러 채널의 새 동영상을 확인합니다.

        Args:
            channels: [{'yt_channel_id': str, 'yt_ch_name': str}, ...]
            last_check_time: 마지막 확인 시간

        Returns:
            Dict[str, List[Dict]]: 채널 ID별 새 동영상 목록
        """
        try:
            # 1. 모든 채널 ID로 한 번에 플레이리스트 ID 조회 (quota: 1)
            channel_ids = [ch['yt_channel_id'] for ch in channels]
            channel_response = self.youtube.channels().list(
                id=','.join(channel_ids),
                part='contentDetails',
                maxResults=50
            ).execute()

            # 채널별 플레이리스트 ID 매핑
            playlist_mapping = {}
            for item in channel_response.get('items', []):
                channel_id = item['id']
                playlist_id = item['contentDetails']['relatedPlaylists']['uploads']
                playlist_mapping[channel_id] = playlist_id

            # 2. 각 플레이리스트의 최근 동영상 개별 조회
            new_videos_by_channel = {}

            for channel_id, playlist_id in playlist_mapping.items():
                try:
                    # 플레이리스트 항목 조회 (quota: 1 per request)
                    playlist_response = self.youtube.playlistItems().list(
                        playlistId=playlist_id,
                        part='snippet',
                        maxResults=5
                    ).execute()

                    # 새 동영상 필터링
                    new_videos = []
                    for item in playlist_response.get('items', []):
                        published_at = datetime.fromisoformat(
                            item['snippet']['publishedAt'].replace('Z', '+00:00')
                        )

                        if published_at > last_check_time:
                            new_videos.append({
                                'video_id': item['snippet']['resourceId']['videoId'],
                                'title': item['snippet']['title'],
                                'published_at': published_at
                            })

                    if new_videos:
                        new_videos_by_channel[channel_id] = new_videos

                except Exception as e:
                    logger.error(f"Error checking videos for channel {channel_id}: {e}")
                    continue

            return new_videos_by_channel

        except Exception as e:
            logger.error(f"Error checking new videos in batch: {e}")
            raise ValueError(f"Failed to check new videos: {str(e)}")

    def get_daily_quota_used(self) -> int:
        """하루 동안 사용된 quota를 반환합니다."""
        return self._daily_quota_used