from enum import Enum


class Trend(str, Enum):
    BULLISH = "Bullish"
    BEARISH = "Bearish"
    NEUTRAL = "Neutral/Mixed"


class OptionType(str, Enum):
    CE = "CE"
    PE = "PE"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    SL = "SL"
    SL_M = "SL-M"


class TransactionType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class ProductType(str, Enum):
    INTRADAY = "I"
    DELIVERY = "D"
    CO = "CO"
    OCO = "OCO"
