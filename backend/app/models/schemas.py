from pydantic import BaseModel


# --- Stock Schemas ---
class StockBase(BaseModel):
    symbol: str
    name: str
    isin: str
    has_options: int


class StockResponse(StockBase):
    last_updated: str | None = None


# --- Auth Schemas ---
class AuthStatus(BaseModel):
    authenticated: bool
    expires_at: str | None = None
    created_at: str | None = None
    has_refresh_token: bool = False
    status: str = "no_token"


class AuthCallback(BaseModel):
    code: str


class ManualToken(BaseModel):
    access_token: str
    refresh_token: str | None = None
    expires_in: int | None = None


class LoginUrlResponse(BaseModel):
    url: str


class TokenValidation(BaseModel):
    valid: bool
    profile: dict | None = None
    error: str | None = None


# --- Indicator / Screening Schemas ---
class IndicatorData(BaseModel):
    date: object  # can be str or date
    close: float
    open: float
    high: float
    low: float
    macd: float | None = None
    macd_signal: float | None = None
    macd_hist: float | None = None
    tenkan_sen: float | None = None
    kijun_sen: float | None = None
    senkou_span_a: float | None = None
    senkou_span_b: float | None = None
    chikou_span: float | None = None


class MacdHistValue(BaseModel):
    day: int
    date: object
    macd_hist: float
    close: float


class ScreeningResult(BaseModel):
    symbol: str
    name: str
    current_price: float
    high_price: float
    low_price: float
    senkou_span_b: float
    macd_hist: float
    prev_macd_hist: float
    trend: str
    color: str
    macd_diffs_5d: list[float]
    macd_hist_values: list[dict]
    intraday_strength_pct: float
    indicators: list[dict]
    raw_data: list[dict]
    last_updated: str


class ScreeningResponse(BaseModel):
    bullish: list[ScreeningResult]
    bearish: list[ScreeningResult]
    neutral: list[ScreeningResult]
    total: int
    timestamp: str


# --- Market Data Schemas ---
class CandleData(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class IntradayCandleData(BaseModel):
    datetime: str
    open: float
    high: float
    low: float
    close: float
    volume: int


# --- Option Schemas ---
class OptionContract(BaseModel):
    strike_price: float
    expiry: str | None = None
    option_type: str
    oi: float = 0
    oi_change: float = 0
    volume: float = 0
    ltp: float = 0
    bid_price: float = 0
    ask_price: float = 0
    iv: float = 0
    delta: float = 0
    theta: float = 0
    gamma: float = 0
    vega: float = 0
    instrument_key: str = ""


class OptionChainResponse(BaseModel):
    chain: list[OptionContract]
    spot_price: float | None = None
    error: str | None = None


class ITMOptionResponse(BaseModel):
    contract: dict | None = None
    error: str | None = None


# --- Order Schemas ---
class PlaceOrderRequest(BaseModel):
    instrument_key: str
    quantity: int
    transaction_type: str
    order_type: str = "MARKET"
    price: float | None = None
    trigger_price: float | None = None
    product: str = "D"


class OrderResponse(BaseModel):
    order_id: str | None = None
    error: str | None = None


class ExecuteStrategyRequest(BaseModel):
    stocks: list[dict]
    profit_target_pct: float = 2.5


class TradeResult(BaseModel):
    symbol: str
    trend: str
    current_price: float
    status: str
    option_type: str | None = None
    strike_price: float | None = None
    trading_symbol: str | None = None
    lot_size: int | None = None
    expiry_date: str | None = None
    option_ltp: float | None = None
    buy_limit_price: float | None = None
    sell_target_price: float | None = None
    buy_order_id: str | None = None
    sell_order_id: str | None = None
    error: str | None = None
