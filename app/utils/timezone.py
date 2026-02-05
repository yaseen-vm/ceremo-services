"""Timezone utilities."""

from datetime import datetime
from zoneinfo import ZoneInfo


def now_ist() -> datetime:
    """Get current time in IST timezone."""
    return datetime.now(ZoneInfo("Asia/Kolkata"))
