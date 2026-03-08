"""Timezone utilities for consistent time handling."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

DEFAULT_TZ = ZoneInfo("Asia/Shanghai")


def now() -> datetime:
    """Get current time in Beijing timezone (timezone-aware)."""
    return datetime.now(DEFAULT_TZ)


def now_iso() -> str:
    """Get current time as ISO string in Beijing timezone."""
    return now().isoformat()


def now_str(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Get current time as formatted string in Beijing timezone."""
    return now().strftime(fmt)


def now_display() -> str:
    """Get current time as display string with timezone info."""
    n = now()
    return f"{n.strftime('%Y-%m-%d %H:%M:%S')} (北京时间 UTC+8)"


def now_date() -> str:
    """Get current date in Beijing timezone."""
    return now().strftime("%Y-%m-%d")


def now_time() -> str:
    """Get current time in Beijing timezone."""
    return now().strftime("%H:%M:%S")


def now_weekday() -> str:
    """Get current weekday in Chinese."""
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return weekdays[now().weekday()]


def to_beijing(dt: datetime) -> datetime:
    """Convert any datetime to Beijing timezone."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=DEFAULT_TZ)
    return dt.astimezone(DEFAULT_TZ)


def format_beijing(dt: datetime | None = None, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime in Beijing timezone."""
    if dt is None:
        dt = now()
    elif dt.tzinfo is None:
        dt = dt.replace(tzinfo=DEFAULT_TZ)
    else:
        dt = dt.astimezone(DEFAULT_TZ)
    return dt.strftime(fmt)
