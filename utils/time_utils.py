# utils/time_utils.py
from datetime import datetime, timezone
from typing import Union


def to_utc(dt: Union[str, datetime]) -> datetime:
    """datetime 객체나 문자열을 UTC timezone이 있는 datetime으로 변환합니다.

    Args:
        dt: datetime 객체 또는 ISO 형식의 문자열

    Returns:
        UTC timezone이 설정된 datetime 객체
    """
    if isinstance(dt, str):
        # ISO 형식 문자열을 datetime으로 변환
        dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))

    # timezone이 없는 경우 UTC로 설정
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    # 다른 timezone인 경우 UTC로 변환
    elif dt.tzinfo != timezone.utc:
        dt = dt.astimezone(timezone.utc)

    return dt


def get_current_utc() -> datetime:
    """현재 시간을 UTC timezone으로 반환합니다."""
    return datetime.now(timezone.utc)


def format_utc(dt: datetime) -> str:
    """datetime 객체를 ISO 8601 형식의 UTC 문자열로 변환합니다."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()