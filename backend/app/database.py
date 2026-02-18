import asyncpg
from app.config import settings

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    """Get the shared connection pool."""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(settings.DATABASE_URL, min_size=2, max_size=10)
    return _pool


async def init_db():
    """Initialize database tables."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS stocks (
                symbol TEXT PRIMARY KEY,
                name TEXT,
                isin TEXT,
                has_options BOOLEAN,
                last_updated TEXT
            )""")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_prices (
                id SERIAL PRIMARY KEY,
                symbol TEXT,
                date TEXT,
                open DOUBLE PRECISION,
                high DOUBLE PRECISION,
                low DOUBLE PRECISION,
                close DOUBLE PRECISION,
                volume BIGINT,
                UNIQUE(symbol, date)
            )""")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS api_tokens (
                id SERIAL PRIMARY KEY,
                access_token TEXT,
                refresh_token TEXT,
                expires_at TEXT,
                created_at TEXT
            )""")
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_daily_prices_symbol_date ON daily_prices(symbol, date)"
        )


async def close_db():
    """Close the connection pool."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


async def populate_stocks(stock_list: list[dict]):
    """Insert/update all stocks from STOCK_LIST."""
    from datetime import datetime

    pool = await get_pool()
    async with pool.acquire() as conn:
        for stock in stock_list:
            await conn.execute(
                """INSERT INTO stocks (symbol, name, isin, has_options, last_updated)
                   VALUES ($1, $2, $3, $4, $5)
                   ON CONFLICT (symbol) DO UPDATE SET
                     name = EXCLUDED.name,
                     isin = EXCLUDED.isin,
                     has_options = EXCLUDED.has_options,
                     last_updated = EXCLUDED.last_updated""",
                stock["symbol"],
                stock["name"],
                stock["isin"],
                bool(stock["has_options"]),
                datetime.now().strftime("%Y-%m-%d"),
            )
