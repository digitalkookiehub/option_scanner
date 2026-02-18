from fastapi import APIRouter, Depends

from app.core.dependencies import get_upstox_api
from app.services.upstox_api import UpstoxAPI

router = APIRouter(prefix="/api/market", tags=["market_data"])


@router.get("/historical/{symbol}")
async def get_historical(
    symbol: str,
    days: int = 200,
    api: UpstoxAPI = Depends(get_upstox_api),
):
    """Historical daily candles (200 days)."""
    data = await api.get_historical_data(symbol, days=days)
    if data:
        return {"data": data}
    return {"data": [], "error": "No historical data available"}


@router.get("/intraday/{symbol}")
async def get_intraday(
    symbol: str,
    interval: int = 1,
    api: UpstoxAPI = Depends(get_upstox_api),
):
    """Intraday candles (1min or 30min)."""
    data, error = await api.get_current_data(symbol, interval_minutes=interval)
    if data:
        return {"data": data}
    return {"data": [], "error": error}


@router.get("/ltp/{instrument_key:path}")
async def get_ltp(
    instrument_key: str,
    api: UpstoxAPI = Depends(get_upstox_api),
):
    """Last traded price."""
    ltp, error = await api.get_ltp(instrument_key)
    if ltp is not None:
        return {"ltp": ltp}
    return {"ltp": None, "error": error}
