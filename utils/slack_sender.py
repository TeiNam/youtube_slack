# utils/slack_sender.py
import logging
from slack_sdk.webhook import WebhookClient
from typing import Dict
from utils.db_manager import DatabaseManager

logger = logging.getLogger(__name__)

class SlackSender:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def send_notification(self, yt_channel_id: str, video: Dict) -> bool:
        """새로운 동영상 알림을 Slack으로 전송합니다.

        Args:
            yt_channel_id: YouTube 채널 ID
            video: 동영상 정보 {'title': str, 'url': str, 'published_at': str}

        Returns:
            bool: 알림 전송 성공 여부
        """
        try:
            # 채널 정보로 웹훅 URL 조회
            channel = self.db.get_channel_by_yt_channel_id(yt_channel_id)
            if not channel:
                logger.error(f"Channel not found for ID: {yt_channel_id}")
                return False

            webhook = self.db.get_webhook(channel.webhook_id)
            if not webhook:
                logger.error(f"Webhook not found for ID: {channel.webhook_id}")
                return False

            # Slack 메시지 생성
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*새로운 영상이 업로드되었습니다!*\n*채널:* {channel.yt_ch_name}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*제목:* <{video['url']}|{video['title']}>"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*업로드 시간:* {video['published_at']}"
                    }
                }
            ]

            # Slack으로 알림 전송
            webhook_client = WebhookClient(webhook.url)
            response = webhook_client.send(blocks=blocks)

            if response.status_code != 200:
                logger.error(
                    f"Failed to send Slack notification: {response.status_code} - "
                    f"Channel: {channel.yt_ch_name}, Video: {video['title']}"
                )
                return False

            logger.info(
                f"Successfully sent notification for channel '{channel.yt_ch_name}' - "
                f"Video: {video['title']}"
            )
            return True

        except Exception as e:
            logger.error(
                f"Error sending Slack notification for channel {yt_channel_id}: {str(e)}"
            )
            return False