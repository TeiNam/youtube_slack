# utils/db_manager.py
import sqlite3
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass
import logging
from contextlib import contextmanager
from utils.time_utils import to_utc, get_current_utc, format_utc

logger = logging.getLogger(__name__)


@dataclass
class Webhook:
    webhook_id: int
    workspace_name: str
    webhook_name: str
    url: str
    create_at: str
    update_at: str


@dataclass
class Channel:
    id: int
    webhook_id: int
    yt_channel_id: str
    yt_handling_id: str
    yt_ch_name: str
    last_check_at: str
    create_at: str
    update_at: str


class DatabaseManager:
    def __init__(self, db_path: str = "youtube_manager.db"):
        self.db_path = db_path
        self.initialize_db()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def initialize_db(self):
        """데이터베이스와 테이블을 초기화합니다."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 각 SQL 명령어를 개별적으로 실행
            sql_commands = [
                # webhook 테이블 생성
                """
                CREATE TABLE IF NOT EXISTS webhook (
                    webhook_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workspace_name TEXT NOT NULL,
                    webhook_name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    create_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    update_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """,

                # channel 테이블 생성
                """
                CREATE TABLE IF NOT EXISTS channel (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    webhook_id INTEGER NOT NULL,
                    yt_channel_id TEXT NOT NULL,
                    yt_handling_id TEXT NOT NULL,
                    yt_ch_name TEXT NOT NULL,
                    last_check_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    create_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    update_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (webhook_id) REFERENCES webhook(webhook_id)
                )
                """,

                # 인덱스 생성
                "CREATE INDEX IF NOT EXISTS idx_webhook_name ON webhook(webhook_name)",
                "CREATE INDEX IF NOT EXISTS idx_yt_channel_id ON channel(yt_channel_id)",
                "CREATE INDEX IF NOT EXISTS idx_yt_handling_id ON channel(yt_handling_id)",
                "CREATE INDEX IF NOT EXISTS idx_last_check_at ON channel(last_check_at)",

                # webhook 테이블 트리거
                """
                CREATE TRIGGER IF NOT EXISTS update_webhook_timestamp 
                AFTER UPDATE ON webhook
                BEGIN
                    UPDATE webhook SET update_at = CURRENT_TIMESTAMP 
                    WHERE webhook_id = NEW.webhook_id;
                END
                """,

                # channel 테이블 트리거
                """
                CREATE TRIGGER IF NOT EXISTS update_channel_timestamp 
                AFTER UPDATE ON channel
                BEGIN
                    UPDATE channel SET update_at = CURRENT_TIMESTAMP 
                    WHERE id = NEW.id;
                END
                """
            ]

            # 각 명령어 실행
            for command in sql_commands:
                cursor.execute(command.strip())

            conn.commit()

    def add_webhook(self, workspace_name: str, webhook_name: str, url: str) -> int:
        """새로운 웹훅을 추가합니다."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO webhook (workspace_name, webhook_name, url)
                VALUES (?, ?, ?)
            """, (workspace_name, webhook_name, url))
            conn.commit()
            return cursor.lastrowid

    def get_webhook(self, webhook_id: int) -> Optional[Webhook]:
        """특정 웹훅 정보를 조회합니다."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM webhook WHERE webhook_id = ?", (webhook_id,))
            row = cursor.fetchone()
            if row:
                return Webhook(**dict(row))
            return None

    def get_all_webhooks(self) -> List[Webhook]:
        """모든 웹훅 목록을 조회합니다."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM webhook ORDER BY webhook_id")
            return [Webhook(**dict(row)) for row in cursor.fetchall()]

    def delete_webhook(self, webhook_id: int) -> bool:
        """웹훅을 삭제합니다."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM webhook WHERE webhook_id = ?", (webhook_id,))
            conn.commit()
            return cursor.rowcount > 0

    def add_channel(self, webhook_id: int, yt_channel_id: str,
                   yt_handling_id: str, yt_ch_name: str) -> int:
        """새로운 채널을 추가합니다."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            current_time = format_utc(get_current_utc())
            cursor.execute("""
                INSERT INTO channel (
                    webhook_id, yt_channel_id, yt_handling_id, yt_ch_name,
                    last_check_at, create_at, update_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                webhook_id, yt_channel_id, yt_handling_id, yt_ch_name,
                current_time, current_time, current_time
            ))
            conn.commit()
            return cursor.lastrowid

    def get_channel_by_id(self, channel_id: int) -> Optional[Channel]:
        """ID로 채널을 조회합니다."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM channel WHERE id = ?", (channel_id,))
            row = cursor.fetchone()
            if row:
                return Channel(**dict(row))
            return None

    def get_all_channels(self) -> List[Channel]:
        """모든 채널 목록을 조회합니다."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM channel ORDER BY id")
            return [Channel(**dict(row)) for row in cursor.fetchall()]

    def get_channels_by_webhook(self, webhook_id: int) -> List[Channel]:
        """특정 웹훅에 등록된 채널 목록을 조회합니다."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM channel WHERE webhook_id = ?", (webhook_id,))
            return [Channel(**dict(row)) for row in cursor.fetchall()]

    def get_channel_by_handling_id(self, yt_handling_id: str) -> Optional[Channel]:
        """핸들링 ID로 채널을 조회합니다."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM channel WHERE yt_handling_id = ?", (yt_handling_id,))
            row = cursor.fetchone()
            if row:
                return Channel(**dict(row))
            return None

    def delete_channel(self, channel_id: int) -> bool:
        """채널을 삭제합니다."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM channel WHERE id = ?", (channel_id,))
            conn.commit()
            return cursor.rowcount > 0

    def update_last_check_time(self, yt_channel_id: str, check_time: Optional[datetime] = None) -> bool:
        """채널의 마지막 확인 시간을 업데이트합니다. (UTC 기준)"""
        if check_time is None:
            check_time = get_current_utc()
        else:
            check_time = to_utc(check_time)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE channel 
                SET last_check_at = ? 
                WHERE yt_channel_id = ?
            """, (format_utc(check_time), yt_channel_id))
            conn.commit()
            return cursor.rowcount > 0

    def get_last_check_time(self, yt_channel_id: str) -> datetime:
        """채널의 마지막 확인 시간을 조회합니다. (UTC 기준)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT last_check_at 
                FROM channel 
                WHERE yt_channel_id = ?
            """, (yt_channel_id,))
            row = cursor.fetchone()
            if row and row['last_check_at']:
                return to_utc(row['last_check_at'])
            return get_current_utc()  # 기본값으로 현재 UTC 시간 반환

    def get_channel_by_yt_channel_id(self, yt_channel_id: str) -> Optional[Channel]:
        """YouTube 채널 ID로 채널을 조회합니다."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM channel 
                WHERE yt_channel_id = ?
            """, (yt_channel_id,))
            row = cursor.fetchone()
            if row:
                return Channel(**dict(row))
            return None