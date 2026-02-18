from fastapi import APIRouter, Depends
import asyncpg

from app.core.dependencies import get_database
from app.core.constants import STOCK_LIST
from app.repositories import stock_repository
from app.database import populate_stocks

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


@router.get("/")
async def list_stocks(pool: asyncpg.Pool = Depends(get_database)):
    """List all 211 stocks."""
    stocks = await stock_repository.get_all_stocks(pool)
    if not stocks:
        # Fallback to STOCK_LIST constant
        return STOCK_LIST
    # Validate ISINs — fill from STOCK_LIST if null
    stock_map = {s["symbol"]: s["isin"] for s in STOCK_LIST}
    for s in stocks:
        if not s.get("isin"):
            s["isin"] = stock_map.get(s["symbol"])
    return stocks


@router.post("/reload")
async def reload_stocks():
    """Reload stock list from constants into database."""
    await populate_stocks(STOCK_LIST)
    return {"success": True, "count": len(STOCK_LIST)}
