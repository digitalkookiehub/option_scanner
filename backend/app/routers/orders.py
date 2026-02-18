from fastapi import APIRouter, Depends

from app.core.dependencies import get_upstox_api
from app.services.upstox_api import UpstoxAPI
from app.services.trading_service import execute_option_trade_strategy
from app.models.schemas import PlaceOrderRequest, ExecuteStrategyRequest

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("/place")
async def place_order(
    body: PlaceOrderRequest,
    api: UpstoxAPI = Depends(get_upstox_api),
):
    """Place buy/sell order."""
    order_id, error = await api.place_order(
        instrument_key=body.instrument_key,
        quantity=body.quantity,
        transaction_type=body.transaction_type,
        order_type=body.order_type,
        price=body.price,
        trigger_price=body.trigger_price,
        product=body.product,
    )
    if order_id:
        return {"order_id": order_id}
    return {"order_id": None, "error": error}


@router.get("/book")
async def get_order_book(api: UpstoxAPI = Depends(get_upstox_api)):
    """Today's order book."""
    orders, error = await api.get_order_book()
    if orders is not None:
        return {"orders": orders}
    return {"orders": [], "error": error}


@router.get("/positions")
async def get_positions(api: UpstoxAPI = Depends(get_upstox_api)):
    """Current positions with P&L."""
    positions, error = await api.get_positions()
    if positions is not None:
        return {"positions": positions}
    return {"positions": [], "error": error}


@router.post("/execute-strategy")
async def execute_strategy(
    body: ExecuteStrategyRequest,
    api: UpstoxAPI = Depends(get_upstox_api),
):
    """Execute full ITM trade strategy."""
    results = await execute_option_trade_strategy(
        api, body.stocks, body.profit_target_pct
    )
    return {"results": results}


@router.post("/preview-strategy")
async def preview_strategy(
    body: ExecuteStrategyRequest,
    api: UpstoxAPI = Depends(get_upstox_api),
):
    """Preview trades without executing (same as execute but orders are not placed)."""
    results = await execute_option_trade_strategy(
        api, body.stocks, body.profit_target_pct
    )
    return {"results": results, "preview": True}
