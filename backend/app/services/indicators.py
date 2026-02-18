"""
Technical Analysis Indicators - EXACT COPY from ScreenerV13.py lines 2453-2535.
DO NOT modify any calculation logic.
"""


def calculate_ema(prices, period):
    if len(prices) < period:
        return [None] * len(prices)
    ema = [None] * (period - 1) + [sum(prices[:period]) / period]
    multiplier = 2 / (period + 1)
    for i in range(period, len(prices)):
        ema.append((prices[i] * multiplier) + (ema[-1] * (1 - multiplier)))
    return ema


def calculate_macd(prices, fast=12, slow=26, signal=9):
    if len(prices) < slow + signal:
        return None, None, None
    fast_ema = calculate_ema(prices, fast)
    slow_ema = calculate_ema(prices, slow)
    macd = [f - s if f and s else None for f, s in zip(fast_ema, slow_ema)]
    valid_macd = [m for m in macd if m is not None]
    if len(valid_macd) < signal:
        return macd, [None] * len(macd), [None] * len(macd)
    signal_ema = calculate_ema(valid_macd, signal)
    signal_line = [None] * (len(macd) - len(signal_ema)) + signal_ema
    histogram = [m - s if m and s else None for m, s in zip(macd, signal_line)]
    return macd, signal_line, histogram


def calculate_ichimoku(data, tenkan=9, kijun=26, senkou_b=52):
    results = []
    for i in range(len(data)):
        result = {"date": data[i]["date"]}
        if i >= tenkan - 1:
            highs = [data[j]["high"] for j in range(i - tenkan + 1, i + 1)]
            lows = [data[j]["low"] for j in range(i - tenkan + 1, i + 1)]
            result["tenkan_sen"] = (max(highs) + min(lows)) / 2
        else:
            result["tenkan_sen"] = None
        if i >= kijun - 1:
            highs = [data[j]["high"] for j in range(i - kijun + 1, i + 1)]
            lows = [data[j]["low"] for j in range(i - kijun + 1, i + 1)]
            result["kijun_sen"] = (max(highs) + min(lows)) / 2
        else:
            result["kijun_sen"] = None
        result["senkou_span_a"] = (
            (result["tenkan_sen"] + result["kijun_sen"]) / 2
            if result["tenkan_sen"] and result["kijun_sen"]
            else None
        )
        if i >= senkou_b - 1:
            highs = [data[j]["high"] for j in range(i - senkou_b + 1, i + 1)]
            lows = [data[j]["low"] for j in range(i - senkou_b + 1, i + 1)]
            result["senkou_span_b"] = (max(highs) + min(lows)) / 2
        else:
            result["senkou_span_b"] = None
        result["chikou_span"] = data[i]["close"]
        results.append(result)
    return results


def calculate_indicators(data):
    if not data or len(data) < 60:
        return None, (None, None, None)
    closes = [d["close"] for d in data]
    macd, signal, histogram = calculate_macd(closes)
    ichimoku = calculate_ichimoku(data)
    results = []
    for i in range(len(data)):
        results.append(
            {
                "date": data[i]["date"],
                "close": data[i]["close"],
                "open": data[i]["open"],
                "high": data[i]["high"],
                "low": data[i]["low"],
                "macd": macd[i] if macd and i < len(macd) else None,
                "macd_signal": signal[i] if signal and i < len(signal) else None,
                "macd_hist": histogram[i] if histogram and i < len(histogram) else None,
                "tenkan_sen": ichimoku[i]["tenkan_sen"],
                "kijun_sen": ichimoku[i]["kijun_sen"],
                "senkou_span_a": ichimoku[i]["senkou_span_a"],
                "senkou_span_b": ichimoku[i]["senkou_span_b"],
                "chikou_span": ichimoku[i]["chikou_span"],
            }
        )
    return results[::-1], (macd, signal, histogram)
