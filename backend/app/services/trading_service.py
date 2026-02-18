"""
Trading Service - Async port of ScreenerV13.py execute_option_trade_strategy (lines 2276-2420).
ALL trading logic preserved EXACTLY. No logic changes.
"""
from app.config import settings
from app.services.upstox_api import UpstoxAPI


async def execute_option_trade_strategy(api: UpstoxAPI, stocks_to_trade, profit_target_pct=2.5):
    """
    Execute the option trading strategy:
    1. At 3:05 PM, identify the closest ITM option contract
    2. Purchase at current market price
    3. Place limit sell order at 2.5% profit
    """
    trade_results = []

    for stock in stocks_to_trade:
        symbol = stock.get("symbol")
        trend = stock.get("trend")
        current_price = stock.get("current_price", 0)

        result = {
            "symbol": symbol,
            "trend": trend,
            "current_price": current_price,
            "status": "pending",
            "option_type": None,
            "contract": None,
            "buy_order_id": None,
            "sell_order_id": None,
            "error": None,
        }

        try:
            # Determine option type based on trend
            if trend == "Bullish":
                option_type = "CE"  # Call option for bullish
            elif trend == "Bearish":
                option_type = "PE"  # Put option for bearish
            else:
                result["error"] = "Stock is not Bullish or Bearish"
                result["status"] = "skipped"
                trade_results.append(result)
                continue

            result["option_type"] = option_type

            # Get nearest expiry
            expiry_date, error = await api.get_nearest_expiry(symbol)
            if not expiry_date:
                result["error"] = f"Could not get expiry: {error}"
                result["status"] = "failed"
                trade_results.append(result)
                continue

            result["expiry_date"] = expiry_date

            # Find closest ITM option
            contract, error = await api.find_itm_option(
                symbol, current_price, option_type, expiry_date
            )
            if not contract:
                result["error"] = f"Could not find ITM option: {error}"
                result["status"] = "failed"
                trade_results.append(result)
                continue

            result["contract"] = contract
            result["strike_price"] = contract.get("strike_price")
            result["trading_symbol"] = contract.get("trading_symbol")
            result["lot_size"] = contract.get("lot_size", 1)

            # Get instrument key for the option
            option_instrument_key = contract.get("instrument_key")
            if not option_instrument_key:
                result["error"] = "No instrument key in contract"
                result["status"] = "failed"
                trade_results.append(result)
                continue

            # Get LTP for the option
            option_ltp, error = await api.get_ltp(option_instrument_key)
            if not option_ltp:
                result["error"] = f"Could not get option LTP: {error}"
                result["status"] = "failed"
                trade_results.append(result)
                continue

            result["option_ltp"] = option_ltp

            # Calculate buy limit price (slightly above LTP for better fill)
            buy_limit_price = round(
                option_ltp * (1 + settings.DEFAULT_BUY_BUFFER_PCT / 100), 2
            )
            result["buy_limit_price"] = buy_limit_price

            # Calculate sell target price (default profit target)
            sell_target_price = round(option_ltp * (1 + profit_target_pct / 100), 2)
            result["sell_target_price"] = sell_target_price

            # NOTE: Actual order placement is commented out in original code (preview mode)
            # Buy and sell orders would go here when enabled
            result["status"] = "success"

        except Exception as e:
            result["error"] = str(e)
            result["status"] = "exception"

        trade_results.append(result)

    return trade_results
