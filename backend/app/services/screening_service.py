"""
Screening Service - Async port of ScreenerV13.py fetch_single_stock_data (lines 2623-2857).
ALL screening conditions preserved EXACTLY. No logic changes.
"""
import asyncio
from datetime import datetime, date

from app.services.indicators import calculate_indicators
from app.services.mock_data import generate_mock_historical_data
from app.services.upstox_api import UpstoxAPI
from app.database import get_pool
from app.repositories import price_repository
from app.core.timezone import now_ist


async def fetch_single_stock_data(
    stock, api: UpstoxAPI, use_live_data, intraday_interval, use_mock=False
):
    try:
        symbol = stock["symbol"]
        if use_mock:
            data_desc = generate_mock_historical_data(symbol, days=200)
        else:
            pool = await get_pool()
            data_desc = await price_repository.get_historical_data(pool, symbol, days=200)
            if not data_desc:
                data_desc = await api.get_historical_data(symbol, days=200)
                if data_desc:
                    await price_repository.save_historical_data(pool, symbol, data_desc)
                else:
                    data_desc = generate_mock_historical_data(symbol, days=200)

        if not data_desc or len(data_desc) < 60:
            return None

        current_price = data_desc[0]["close"]
        high_price = data_desc[0]["high"]
        low_price = data_desc[0]["low"]
        open_price = data_desc[0]["open"]

        # Fetch current/live price if enabled
        if use_live_data and not use_mock:
            try:
                intraday_data, error = await api.get_current_data(
                    symbol, interval_minutes=intraday_interval
                )
                if intraday_data and len(intraday_data) > 0:
                    # Get the most recent candle for current price
                    current_price = intraday_data[0]["close"]
                    # Get the high and low from today's intraday data
                    high_price = max([c["high"] for c in intraday_data])
                    low_price = min([c["low"] for c in intraday_data])
                    # Sort intraday data by datetime ascending to get open price
                    sorted_intraday = sorted(intraday_data, key=lambda x: x["datetime"])
                    open_price = sorted_intraday[0]["open"]
                    new_row_dict = {
                        "date": date.today(),
                        "open": open_price,
                        "high": high_price,
                        "low": low_price,
                        "close": current_price,
                        "volume": 22,
                    }
                    data_desc.append(new_row_dict)
                    for row in data_desc:
                        # If the date is a string, convert it to a datetime object
                        if isinstance(row["date"], str):
                            row["date"] = datetime.strptime(row["date"], "%Y-%m-%d").date()

                    # Now the sort will work perfectly
                    data_desc.sort(key=lambda x: x["date"], reverse=True)

            except Exception:
                pass  # Fall back to historical data

        data_asc = data_desc[::-1]
        indicators_desc, _ = calculate_indicators(data_asc)

        if not indicators_desc or len(indicators_desc) < 6:
            return None

        latest = indicators_desc[0]
        previous = indicators_desc[1]

        if (
            latest["senkou_span_b"] is None
            or latest["macd_hist"] is None
            or previous["macd_hist"] is None
        ):
            return None

        senkou_span_b = latest["senkou_span_b"]
        latest_macd_hist = latest["macd_hist"]
        previous_macd_hist = previous["macd_hist"]

        cloud_bullish = current_price > senkou_span_b
        cloud_bearish = current_price < senkou_span_b
        macd_hist_increasing = latest_macd_hist > previous_macd_hist
        macd_hist_decreasing = latest_macd_hist < previous_macd_hist

        # Calculate MACD differences for last 5 days
        macd_diffs = []
        for i in range(5):
            if i + 1 < len(indicators_desc):
                curr = indicators_desc[i]["macd_hist"]
                prev = indicators_desc[i + 1]["macd_hist"]
                if curr is not None and prev is not None:
                    macd_diffs.append(round(curr - prev, 4))
                else:
                    macd_diffs.append(0)
            else:
                macd_diffs.append(0)

        # Get MACD hist values for last 6 days
        macd_hist_values = []
        for i in range(6):
            if i < len(indicators_desc) and indicators_desc[i]["macd_hist"] is not None:
                macd_hist_values.append(
                    {
                        "day": i,
                        "date": indicators_desc[i]["date"],
                        "macd_hist": round(indicators_desc[i]["macd_hist"], 4),
                        "close": round(indicators_desc[i]["close"], 2),
                    }
                )

        if current_price > open_price:
            intraday_strength_pct = (
                ((high_price - current_price) / current_price) * 100
                if current_price > 0
                else 0
            )
        else:
            intraday_strength_pct = (
                ((current_price - low_price) / current_price) * 100
                if current_price > 0
                else 0
            )

        # Additional Ichimoku checks for 26 periods ago
        ichimoku_bullish_pass = False
        ichimoku_bearish_pass = False
        if len(indicators_desc) > 26:
            cloud_a_26 = indicators_desc[26]["senkou_span_a"]
            cloud_b_26 = indicators_desc[26]["senkou_span_b"]
            candle_26_close = indicators_desc[26]["close"]
            chikou_span = latest["chikou_span"]

            # Bullish checks
            cloud_color_bullish_26 = cloud_a_26 > cloud_b_26 if cloud_a_26 and cloud_b_26 else False
            cloud_position_bullish_26 = current_price > cloud_a_26 and current_price > cloud_b_26 if cloud_a_26 and cloud_b_26 else False
            chikou_above = chikou_span > candle_26_close if chikou_span and candle_26_close else False
            ichimoku_bullish_pass = cloud_position_bullish_26 and cloud_color_bullish_26 and chikou_above

            # Bearish checks
            cloud_color_bearish_26 = cloud_b_26 > cloud_a_26 if cloud_a_26 and cloud_b_26 else False
            cloud_position_bearish_26 = current_price < cloud_a_26 and current_price < cloud_b_26 if cloud_a_26 and cloud_b_26 else False
            chikou_below = chikou_span < candle_26_close if chikou_span and candle_26_close else False
            ichimoku_bearish_pass = cloud_position_bearish_26 and cloud_color_bearish_26 and chikou_below

        # MACD check: Histogram or Signal Line > 0
        macd_positive = (latest_macd_hist > 0 and (latest["macd_signal"] and latest["macd_signal"] > 0))

        # MACD check for bearish: Histogram or Signal Line < 0
        macd_negative = (latest_macd_hist < 0 and (latest["macd_signal"] and latest["macd_signal"] < 0))

        if cloud_bullish and macd_positive and macd_hist_increasing and ichimoku_bullish_pass and latest['close'] > latest['open']:
            trend, color = "Bullish", "green"
        elif cloud_bearish and macd_negative and macd_hist_decreasing and ichimoku_bearish_pass and latest['close'] < latest['open']:
            trend, color = "Bearish", "red"
        else:
            trend, color = "Neutral/Mixed", "gray"

        # Serialize dates to strings for JSON response
        serialized_indicators = []
        for ind in indicators_desc:
            d = dict(ind)
            if isinstance(d.get("date"), date):
                d["date"] = d["date"].isoformat()
            serialized_indicators.append(d)

        serialized_raw = []
        for rd in data_desc:
            d = dict(rd)
            if isinstance(d.get("date"), date):
                d["date"] = d["date"].isoformat()
            serialized_raw.append(d)

        serialized_macd_hist = []
        for mv in macd_hist_values:
            d = dict(mv)
            if isinstance(d.get("date"), date):
                d["date"] = d["date"].isoformat()
            serialized_macd_hist.append(d)

        return {
            "symbol": symbol,
            "name": stock["name"],
            "current_price": round(current_price, 2),
            "high_price": round(high_price, 2),
            "low_price": round(low_price, 2),
            "senkou_span_b": round(senkou_span_b, 2),
            "macd_hist": round(latest_macd_hist, 4),
            "prev_macd_hist": round(previous_macd_hist, 4),
            "trend": trend,
            "color": color,
            "macd_diffs_5d": macd_diffs,
            "macd_hist_values": serialized_macd_hist,
            "intraday_strength_pct": round(intraday_strength_pct, 4),
            "indicators": serialized_indicators,
            "raw_data": serialized_raw,
            "last_updated": now_ist().strftime("%H:%M:%S"),
        }
    except Exception:
        return None


async def screen_stocks(
    stock_list,
    api: UpstoxAPI,
    use_live_data,
    intraday_interval,
    use_mock=False,
):
    """Screen stocks using async concurrency (replaces ThreadPoolExecutor)."""
    semaphore = asyncio.Semaphore(50)

    async def _fetch_with_semaphore(stock):
        async with semaphore:
            return await fetch_single_stock_data(
                stock, api, use_live_data, intraday_interval, use_mock
            )

    tasks = [_fetch_with_semaphore(stock) for stock in stock_list]
    raw_results = await asyncio.gather(*tasks, return_exceptions=True)

    results = []
    for r in raw_results:
        if isinstance(r, dict) and r is not None:
            results.append(r)

    return results
