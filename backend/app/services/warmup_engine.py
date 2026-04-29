"""
Warmup Engine: The heart of Nexus Engine.
Calculates and manages email warmup schedules with real ramp-up logic.
"""
import math
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional


def calculate_daily_target(day: int, max_per_day: int, ramp_days: int = 28) -> int:
    """
    Calculate how many emails to send on a given warmup day.

    Day 1 starts at 3 emails.
    Increases by ~15% each day.
    Caps at max_per_day after ramp_days.

    Formula: min(3 * 1.15^(day-1), max_per_day)
    """
    if day <= 0:
        return 0
    emails = int(3 * math.pow(1.15, day - 1))
    return min(emails, max_per_day)


def calculate_target_opens(emails_sent: int) -> int:
    """Target ~30% open rate"""
    return max(1, int(emails_sent * 0.3))


def calculate_target_replies(emails_sent: int, reply_rate: float = 0.05) -> int:
    """Target 3-8% reply rate"""
    return max(1, int(emails_sent * reply_rate))


def calculate_reputation_score(
    sent: int,
    opened: int,
    replied: int,
    bounced: int,
    spammed: int,
) -> float:
    """
    Calculate reputation score (0-100).

    Factors:
    - Open rate contribution (30 points max)
    - Reply rate contribution (30 points max)
    - Bounce penalty (-1 per % over 3%)
    - Spam penalty (-2 per % over 0.3%)
    - Volume bonus (up to 10 bonus for consistency)
    """
    if sent == 0:
        return 50.0  # Neutral starting score

    open_rate = min(opened / sent, 1.0)
    reply_rate = min(replied / sent, 1.0)
    bounce_rate = bounced / sent if sent > 0 else 0
    spam_rate = spammed / sent if sent > 0 else 0

    score = 50.0  # Base

    # Open rate contribution (up to +30)
    score += open_rate * 30

    # Reply rate contribution (up to +30)
    score += reply_rate * 30

    # Bounce penalty
    if bounce_rate > 0.03:
        score -= (bounce_rate - 0.03) * 100

    # Spam penalty
    if spam_rate > 0.003:
        score -= (spam_rate - 0.003) * 200

    return max(10, min(100, round(score, 1)))


def should_pause_warmup(spam_rate: float, bounce_rate: float) -> tuple[bool, str]:
    """
    Check if warmup should be paused.
    Returns (should_pause, reason)
    """
    if spam_rate > 0.003:  # 0.3% spam rate threshold
        return True, f"Spam rate too high: {spam_rate*100:.2f}% (limit: 0.3%)"
    if bounce_rate > 0.05:  # 5% bounce rate threshold
        return True, f"Bounce rate too high: {bounce_rate*100:.2f}% (limit: 5%)"
    return False, ""


def get_warmup_phase(day: int, ramp_days: int = 28) -> str:
    """Determine which phase of warmup we're in"""
    progress = day / ramp_days
    if progress < 0.15:
        return "Initial Ramp-up"
    elif progress < 0.35:
        return "Growth Phase"
    elif progress < 0.65:
        return "Stabilization"
    elif progress < 1.0:
        return "Fine-tuning"
    else:
        return "Maintenance"


def generate_schedule(ramp_days: int = 28, max_per_day: int = 100) -> list[dict]:
    """Generate a complete warmup schedule"""
    schedule = []
    for day in range(1, ramp_days + 1):
        daily_max = calculate_daily_target(day, max_per_day, ramp_days)
        phase = get_warmup_phase(day, ramp_days)
        schedule.append({
            "day": day,
            "phase": phase,
            "max_emails": daily_max,
            "target_opens": calculate_target_opens(daily_max),
            "target_replies": calculate_target_replies(daily_max),
            "total_emails_cumulative": sum(
                calculate_daily_target(d, max_per_day, ramp_days) for d in range(1, day + 1)
            ),
        })
    return schedule


async def run_warmup_cycle(account_id: int):
    """
    Simulated warmup cycle for an account.
    In production, this would be a Celery task or background job.
    """
    # This would connect to the email account via IMAP/SMTP,
    # send warmup emails to the pool, check for replies,
    # and update metrics in the database.
    await asyncio.sleep(0.1)  # Simulate work
    return {"status": "cycle_complete", "account_id": account_id}
