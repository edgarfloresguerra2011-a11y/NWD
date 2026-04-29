"""
Analytics Service: Aggregation and reporting for email deliverability metrics.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional


def calculate_trend(data: list[float], window: int = 7) -> list[float]:
    """Calculate moving average trend"""
    if len(data) < window:
        return data
    result = []
    for i in range(len(data)):
        if i < window - 1:
            result.append(sum(data[:i + 1]) / (i + 1))
        else:
            result.append(sum(data[i - window + 1:i + 1]) / window)
    return result


def generate_date_range(days: int = 30) -> list[str]:
    """Generate list of dates for the last N days"""
    today = datetime.now(timezone.utc)
    return [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days - 1, -1, -1)]


def calculate_deliverability_score(
    inbox_rate: float,
    spam_rate: float,
    bounce_rate: float,
) -> float:
    """Calculate overall deliverability health score (0-100)"""
    score = 100.0
    score -= spam_rate * 100  # -1 per 1% spam
    score -= bounce_rate * 50  # -0.5 per 1% bounce
    score += inbox_rate * 20   # +20 max for good inbox placement
    return max(0, min(100, round(score, 1)))
