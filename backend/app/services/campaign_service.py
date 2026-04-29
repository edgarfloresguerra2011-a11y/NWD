"""
Campaign Service: Manages campaign lifecycle and multi-step sequences.
"""
import random
from datetime import datetime, timezone
from typing import Optional, List


def generate_sending_windows(
    start_hour: int = 8,
    end_hour: int = 18,
    timezone_offset: int = -5,
) -> list[int]:
    """Generate business hour windows for sending"""
    return list(range(start_hour, end_hour))


def should_send_now(hour: int, sending_hours: list[int]) -> bool:
    """Check if current hour is within sending window"""
    return hour in sending_hours


def select_account_for_sending(accounts: list) -> Optional[dict]:
    """
    Smart account selection:
    - Prefer accounts with lowest daily sent count
    - Avoid accounts in 'risk' or 'paused' status
    """
    available = [
        a for a in accounts
        if a.get("status") in ("stable", "warming")
        and a.get("emails_sent_today", 0) < a.get("warmup_max_per_day", 50)
    ]
    if not available:
        return None
    return min(available, key=lambda a: a.get("emails_sent_today", 0))
