from datetime import datetime, timedelta, timezone

# IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))


def now_ist():
    """Return current time in IST."""
    return datetime.now(IST)


def is_market_hours() -> bool:
    """Check if Indian stock market is currently open (9:15 AM - 3:30 PM IST)."""
    _now = now_ist()
    current_hour = _now.hour
    current_minute = _now.minute
    return (
        (current_hour == 9 and current_minute >= 15)
        or (current_hour > 9 and current_hour < 15)
        or (current_hour == 15 and current_minute <= 30)
    )
