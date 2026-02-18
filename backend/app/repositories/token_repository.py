import asyncpg
from datetime import datetime


async def save_token(
    pool: asyncpg.Pool,
    access_token: str,
    refresh_token: str | None = None,
    expires_at: str | None = None,
) -> bool:
    """Save access token, replacing any existing one."""
    try:
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM api_tokens")
            await conn.execute(
                "INSERT INTO api_tokens (access_token, refresh_token, expires_at, created_at) VALUES ($1, $2, $3, $4)",
                access_token,
                refresh_token,
                expires_at,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
        return True
    except Exception:
        return False


async def get_latest_token(pool: asyncpg.Pool) -> dict | None:
    """Get the most recent token record."""
    try:
        result = await pool.fetchrow(
            "SELECT access_token, refresh_token, expires_at, created_at FROM api_tokens ORDER BY id DESC LIMIT 1"
        )
        if result:
            return {
                "access_token": result["access_token"],
                "refresh_token": result["refresh_token"],
                "expires_at": result["expires_at"],
                "created_at": result["created_at"],
            }
        return None
    except Exception:
        return None


async def delete_token(pool: asyncpg.Pool) -> bool:
    """Delete all stored tokens."""
    try:
        await pool.execute("DELETE FROM api_tokens")
        return True
    except Exception:
        return False
