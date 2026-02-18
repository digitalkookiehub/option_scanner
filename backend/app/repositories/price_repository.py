import asyncpg


async def save_historical_data(pool: asyncpg.Pool, symbol: str, data: list[dict]) -> bool:
    """Save historical price data to database."""
    try:
        async with pool.acquire() as conn:
            for day in data:
                await conn.execute(
                    """INSERT INTO daily_prices (symbol, date, open, high, low, close, volume)
                       VALUES ($1, $2, $3, $4, $5, $6, $7)
                       ON CONFLICT (symbol, date) DO UPDATE SET
                         open = EXCLUDED.open,
                         high = EXCLUDED.high,
                         low = EXCLUDED.low,
                         close = EXCLUDED.close,
                         volume = EXCLUDED.volume""",
                    symbol,
                    day["date"],
                    day["open"],
                    day["high"],
                    day["low"],
                    day["close"],
                    day["volume"],
                )
        return True
    except Exception:
        return False


async def get_historical_data(pool: asyncpg.Pool, symbol: str, days: int = 200) -> list[dict]:
    """Get historical price data from database."""
    try:
        rows = await pool.fetch(
            "SELECT date, open, high, low, close, volume FROM daily_prices WHERE symbol = $1 ORDER BY date DESC LIMIT $2",
            symbol,
            days,
        )
        return [
            {
                "date": r["date"],
                "open": r["open"],
                "high": r["high"],
                "low": r["low"],
                "close": r["close"],
                "volume": r["volume"],
            }
            for r in rows
        ]
    except Exception:
        return []
