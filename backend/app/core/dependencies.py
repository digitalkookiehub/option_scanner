import asyncpg
from app.database import get_pool
from app.services.token_manager import TokenManager
from app.services.upstox_api import UpstoxAPI


async def get_database() -> asyncpg.Pool:
    """FastAPI dependency for database connection pool."""
    return await get_pool()


async def get_token_manager() -> TokenManager:
    """FastAPI dependency for token manager."""
    pool = await get_pool()
    return TokenManager(pool)


async def get_upstox_api() -> UpstoxAPI:
    """FastAPI dependency for Upstox API client."""
    pool = await get_pool()
    token_manager = TokenManager(pool)
    return UpstoxAPI(token_manager)
