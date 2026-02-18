from fastapi import APIRouter, Depends

from app.core.dependencies import get_upstox_api
from app.services.upstox_api import UpstoxAPI

router = APIRouter(prefix="/api/options", tags=["options"])


@router.get("/contracts/{symbol}")
async def get_option_contracts(
    symbol: str,
    expiry_date: str | None = None,
    api: UpstoxAPI = Depends(get_upstox_api),
):
    """Option contracts for a stock."""
    contracts, error, instrument_key = await api.get_option_contracts_for_stock(
        symbol, expiry_date
    )
    if contracts:
        return {"contracts": contracts, "instrument_key": instrument_key}
    return {"contracts": [], "error": error}


@router.get("/chain/{symbol}")
async def get_option_chain(
    symbol: str,
    expiry_date: str,
    api: UpstoxAPI = Depends(get_upstox_api),
):
    """Full option chain with Greeks."""
    chain, spot_price, error = await api.get_option_chain_for_stock(symbol, expiry_date)
    if chain:
        return {"chain": chain, "spot_price": spot_price}
    return {"chain": [], "spot_price": None, "error": error}


@router.get("/expiries/{symbol}")
async def get_expiries(
    symbol: str,
    api: UpstoxAPI = Depends(get_upstox_api),
):
    """Available expiry dates."""
    contracts, error, _ = await api.get_option_contracts_for_stock(symbol)
    if contracts:
        expiry_dates = sorted(set(c.get("expiry") for c in contracts if c.get("expiry")))
        return {"expiries": expiry_dates}
    return {"expiries": [], "error": error}


@router.get("/itm/{symbol}")
async def find_itm_option(
    symbol: str,
    current_price: float,
    option_type: str,
    expiry_date: str | None = None,
    api: UpstoxAPI = Depends(get_upstox_api),
):
    """Find closest ITM option."""
    contract, error = await api.find_itm_option(
        symbol, current_price, option_type, expiry_date
    )
    if contract:
        return {"contract": contract}
    return {"contract": None, "error": error}
