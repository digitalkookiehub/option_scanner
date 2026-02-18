import asyncpg


async def get_all_stocks(pool: asyncpg.Pool) -> list[dict]:
    """Get all stocks from database."""
    rows = await pool.fetch("SELECT symbol, name, isin, has_options FROM stocks")
    return [
        {
            "symbol": row["symbol"],
            "name": row["name"],
            "isin": row["isin"],
            "has_options": row["has_options"],
        }
        for row in rows
    ]


async def get_stock_isin(pool: asyncpg.Pool, symbol: str) -> str | None:
    """Get ISIN for a symbol from database."""
    result = await pool.fetchval("SELECT isin FROM stocks WHERE symbol = $1", symbol)
    return result
