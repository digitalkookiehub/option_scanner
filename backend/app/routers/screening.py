from fastapi import APIRouter, Depends

from app.core.dependencies import get_upstox_api
from app.core.constants import STOCK_LIST
from app.core.timezone import now_ist
from app.services.upstox_api import UpstoxAPI
from app.services import screening_service
from app.models.schemas import ScreeningResponse

router = APIRouter(prefix="/api/screening", tags=["screening"])

# Cache for last screening results
_last_results: dict | None = None


@router.post("/run", response_model=ScreeningResponse)
async def run_screening(
    use_mock: bool = True,
    use_live_data: bool = False,
    intraday_interval: int = 1,
    api: UpstoxAPI = Depends(get_upstox_api),
):
    """Screen all 211 stocks (returns bullish/bearish/neutral)."""
    global _last_results

    results = await screening_service.screen_stocks(
        STOCK_LIST, api, use_live_data, intraday_interval, use_mock
    )

    bullish = [r for r in results if r["trend"] == "Bullish"]
    bearish = [r for r in results if r["trend"] == "Bearish"]
    neutral = [r for r in results if r["trend"] == "Neutral/Mixed"]

    # Sort by intraday strength
    bullish.sort(key=lambda x: x["intraday_strength_pct"], reverse=False)
    bearish.sort(key=lambda x: x["intraday_strength_pct"], reverse=False)

    response = ScreeningResponse(
        bullish=bullish,
        bearish=bearish,
        neutral=neutral,
        total=len(results),
        timestamp=now_ist().strftime("%Y-%m-%d %H:%M:%S"),
    )

    _last_results = response.model_dump()
    return response


@router.get("/results")
async def get_results():
    """Get last cached screening results."""
    if _last_results:
        return _last_results
    return {"bullish": [], "bearish": [], "neutral": [], "total": 0, "timestamp": ""}


@router.get("/stock/{symbol}")
async def screen_single_stock(
    symbol: str,
    use_mock: bool = True,
    use_live_data: bool = False,
    intraday_interval: int = 1,
    api: UpstoxAPI = Depends(get_upstox_api),
):
    """Screen a single stock with full indicators."""
    stock = None
    for s in STOCK_LIST:
        if s["symbol"] == symbol:
            stock = s
            break

    if not stock:
        return {"error": f"Stock {symbol} not found"}

    result = await screening_service.fetch_single_stock_data(
        stock, api, use_live_data, intraday_interval, use_mock
    )

    if not result:
        return {"error": f"Could not process stock {symbol}"}

    return result
