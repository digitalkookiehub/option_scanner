"""
Upstox API Service - Async port of ScreenerV13.py UpstoxAPI class (lines 1611-2273).
All logic preserved exactly, converted from requests/HTTP_SESSION to httpx.AsyncClient.
"""
import asyncio
import urllib.parse

import httpx

from app.config import settings
from app.core.timezone import now_ist, is_market_hours
from app.services.token_manager import TokenManager
from app.database import get_pool
from app.repositories import stock_repository


class UpstoxAPI:
    def __init__(self, token_manager: TokenManager):
        self.token_manager = token_manager
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=settings.API_TIMEOUT)
        return self._client

    async def get_headers(self):
        token = await self.token_manager.get_token()
        return (
            {"Accept": "application/json", "Authorization": f"Bearer {token}"}
            if token
            else None
        )

    async def _get_instrument_key(self, symbol):
        pool = await get_pool()
        isin = await stock_repository.get_stock_isin(pool, symbol)
        if not isin:
            # Fallback to STOCK_LIST
            from app.core.constants import STOCK_LIST
            for stock in STOCK_LIST:
                if stock["symbol"] == symbol:
                    isin = stock["isin"]
                    break
        return f"NSE_EQ|{isin}" if isin else None

    async def get_historical_data(self, symbol, days=200):
        try:
            headers = await self.get_headers()
            if not headers:
                return None
            instrument_key = await self._get_instrument_key(symbol)
            if not instrument_key:
                return None
            from datetime import datetime, timedelta
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            url = f"{settings.HISTORICAL_CANDLE_V2_URL}/{instrument_key}/day/{end_date}/{start_date}"
            client = await self._get_client()
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                candles = response.json().get("data", {}).get("candles", [])
                return [
                    {
                        "date": c[0][:10],
                        "open": c[1],
                        "high": c[2],
                        "low": c[3],
                        "close": c[4],
                        "volume": c[5],
                    }
                    for c in candles
                ]
        except Exception:
            pass
        return None

    async def get_current_data(self, symbol, interval_minutes=1):
        """Get intraday candle data for a symbol"""
        try:
            headers = await self.get_headers()
            if not headers:
                return None, "No valid API token found"
            instrument_key = await self._get_instrument_key(symbol)
            if not instrument_key:
                return None, f"Could not find instrument key for {symbol}"

            # Correct interval mapping for Upstox API
            interval_map = {1: "1minute", 30: "30minute"}
            interval_str = interval_map.get(interval_minutes, "1minute")

            url = f"{settings.INTRADAY_CANDLE_V2_URL}/{instrument_key}/{interval_str}"

            client = await self._get_client()
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                candles = response.json().get("data", {}).get("candles", [])
                if candles:
                    return [
                        {
                            "datetime": c[0],
                            "open": c[1],
                            "high": c[2],
                            "low": c[3],
                            "close": c[4],
                            "volume": c[5],
                        }
                        for c in candles
                    ], None
                else:
                    if not is_market_hours():
                        return None, "Market closed - No live data available"
                    else:
                        return None, "No candle data available"
            elif response.status_code == 401:
                return None, "Token expired"
            elif response.status_code == 429:
                return None, "Rate limited"
            else:
                return None, f"HTTP {response.status_code}"

        except httpx.TimeoutException:
            return None, "Timeout"
        except Exception as e:
            return None, str(e)[:50]

    async def get_option_contracts(self, instrument_key, expiry_date=None):
        """Fetch option contracts for an underlying symbol"""
        try:
            headers = await self.get_headers()
            if not headers:
                return None, "No valid API token found"

            encoded_key = urllib.parse.quote(instrument_key, safe="")
            url = f"{settings.OPTION_CONTRACT_URL}?instrument_key={encoded_key}"

            if expiry_date:
                url += f"&expiry_date={expiry_date}"

            max_retries = 3
            for attempt in range(max_retries):
                async with httpx.AsyncClient(timeout=15) as client:
                    response = await client.get(url, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success":
                        contracts = data.get("data", [])
                        return contracts, None
                    else:
                        return (
                            None,
                            f"API Error: {data.get('message', 'Unknown error')}",
                        )
                elif response.status_code == 401:
                    return None, "Authentication failed - Token may be expired"
                elif response.status_code == 429:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2)
                        continue
                    else:
                        return (
                            None,
                            "Rate limited (429) - Too many requests. Please wait a few seconds and try again.",
                        )
                elif response.status_code == 400:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("errors", [{}])[0].get(
                            "message", "Bad request"
                        )
                    except Exception:
                        error_msg = "Bad request"
                    return None, f"Bad Request: {error_msg}"
                else:
                    return None, f"HTTP {response.status_code}"

        except httpx.TimeoutException:
            return None, "Request timed out"
        except Exception as e:
            return None, f"Error: {str(e)}"

    async def get_option_contracts_for_stock(self, symbol, expiry_date=None):
        """Fetch option contracts for a stock symbol"""
        try:
            pool = await get_pool()
            isin = await stock_repository.get_stock_isin(pool, symbol)
            if not isin:
                from app.core.constants import STOCK_LIST
                for stock in STOCK_LIST:
                    if stock["symbol"] == symbol:
                        isin = stock["isin"]
                        break
            if not isin:
                return None, f"Could not find ISIN for {symbol}", None

            instrument_key = f"NSE_EQ|{isin}"
            contracts, error = await self.get_option_contracts(instrument_key, expiry_date)
            return contracts, error, instrument_key
        except Exception as e:
            return None, f"Error: {str(e)}", None

    async def get_option_chain_for_index(self, index_name="Nifty 50", expiry_date=None):
        """Fetch option contracts for an index"""
        try:
            instrument_key = f"NSE_INDEX|{index_name}"
            return await self.get_option_contracts(instrument_key, expiry_date)
        except Exception:
            return None

    async def get_option_chain(self, instrument_key, expiry_date):
        """Fetch full option chain with market data and Greeks"""
        try:
            headers = await self.get_headers()
            if not headers:
                return None, None, "No valid API token found"

            encoded_key = urllib.parse.quote(instrument_key, safe="")
            url = f"{settings.OPTION_CHAIN_URL}?instrument_key={encoded_key}&expiry_date={expiry_date}"

            client = await self._get_client()
            response = await client.get(url, headers=headers, timeout=15)

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    option_data = data.get("data", [])

                    if not option_data:
                        return (
                            None,
                            None,
                            f"No option chain data for expiry {expiry_date}. Try a valid expiry date (usually Thursday).",
                        )

                    option_chain = []
                    spot_price = None

                    for option in option_data:
                        expiry = option.get("expiry")
                        strike_price = option.get("strike_price")
                        underlying_spot_price = option.get("underlying_spot_price")

                        if spot_price is None and underlying_spot_price:
                            spot_price = underlying_spot_price

                        # Call options
                        call_option = option.get("call_options", {})
                        call_market_data = call_option.get("market_data", {})
                        call_greeks = call_option.get("option_greeks", {})

                        if call_market_data:
                            option_chain.append(
                                {
                                    "strike_price": strike_price,
                                    "expiry": expiry,
                                    "option_type": "CE",
                                    "oi": call_market_data.get("oi", 0),
                                    "oi_change": call_market_data.get("oi_day_change", 0),
                                    "volume": call_market_data.get("volume", 0),
                                    "ltp": call_market_data.get("ltp", 0),
                                    "bid_price": call_market_data.get("bid_price", 0),
                                    "ask_price": call_market_data.get("ask_price", 0),
                                    "iv": call_greeks.get("iv", 0),
                                    "delta": call_greeks.get("delta", 0),
                                    "theta": call_greeks.get("theta", 0),
                                    "gamma": call_greeks.get("gamma", 0),
                                    "vega": call_greeks.get("vega", 0),
                                    "instrument_key": call_option.get("instrument_key", ""),
                                }
                            )

                        # Put options
                        put_option = option.get("put_options", {})
                        put_market_data = put_option.get("market_data", {})
                        put_greeks = put_option.get("option_greeks", {})

                        if put_market_data:
                            option_chain.append(
                                {
                                    "strike_price": strike_price,
                                    "expiry": expiry,
                                    "option_type": "PE",
                                    "oi": put_market_data.get("oi", 0),
                                    "oi_change": put_market_data.get("oi_day_change", 0),
                                    "volume": put_market_data.get("volume", 0),
                                    "ltp": put_market_data.get("ltp", 0),
                                    "bid_price": put_market_data.get("bid_price", 0),
                                    "ask_price": put_market_data.get("ask_price", 0),
                                    "iv": put_greeks.get("iv", 0),
                                    "delta": put_greeks.get("delta", 0),
                                    "theta": put_greeks.get("theta", 0),
                                    "gamma": put_greeks.get("gamma", 0),
                                    "vega": put_greeks.get("vega", 0),
                                    "instrument_key": put_option.get("instrument_key", ""),
                                }
                            )

                    return option_chain, spot_price, None
                else:
                    error_msg = data.get("message", "Unknown error")
                    return None, None, f"API Error: {error_msg}"
            elif response.status_code == 401:
                return (
                    None,
                    None,
                    "Token expired. Please get a new token from Upstox and update in Token Management.",
                )
            elif response.status_code == 429:
                return (
                    None,
                    None,
                    "Rate limited - Please wait a few seconds and try again",
                )
            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("errors", [{}])[0].get(
                        "message", "Bad request"
                    )
                    if "expiry" in error_msg.lower() or "date" in error_msg.lower():
                        return (
                            None,
                            None,
                            f"Invalid expiry date: {expiry_date}. Select a valid expiry (usually Thursday).",
                        )
                except Exception:
                    error_msg = "Bad request"
                return None, None, f"Bad Request: {error_msg}"
            else:
                return None, None, f"HTTP Error: {response.status_code}"

        except httpx.TimeoutException:
            return None, None, "Request timed out - Try again"
        except Exception as e:
            return None, None, f"Error: {str(e)}"

    async def get_option_chain_for_stock(self, symbol, expiry_date):
        """Fetch option chain for a stock symbol"""
        try:
            pool = await get_pool()
            isin = await stock_repository.get_stock_isin(pool, symbol)
            if not isin:
                from app.core.constants import STOCK_LIST
                for stock in STOCK_LIST:
                    if stock["symbol"] == symbol:
                        isin = stock["isin"]
                        break
            if not isin:
                return None, None, f"Could not find ISIN for {symbol}"

            instrument_key = f"NSE_EQ|{isin}"
            return await self.get_option_chain(instrument_key, expiry_date)
        except Exception as e:
            return None, None, f"Error: {str(e)}"

    async def get_ltp(self, instrument_key):
        """Get Last Traded Price for an instrument"""
        try:
            headers = await self.get_headers()
            if not headers:
                return None, "No valid API token found"

            encoded_key = urllib.parse.quote(instrument_key, safe="")
            url = f"{settings.UPSTOX_BASE_URL}/v2/market-quote/ltp?instrument_key={encoded_key}"
            client = await self._get_client()
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    ltp_data = data.get("data", {})
                    for key, value in ltp_data.items():
                        if "last_price" in value:
                            return value["last_price"], None
                    return None, "LTP not found in response"
                else:
                    return None, f"API Error: {data.get('message', 'Unknown error')}"
            else:
                return None, f"HTTP {response.status_code}"
        except Exception as e:
            return None, f"Error: {str(e)}"

    async def place_order(
        self,
        instrument_key,
        quantity,
        transaction_type,
        order_type="MARKET",
        price=None,
        trigger_price=None,
        product="D",
    ):
        """Place an order via Upstox API"""
        try:
            headers = await self.get_headers()
            if not headers:
                return None, "No valid API token found"

            headers["Content-Type"] = "application/json"

            order_data = {
                "quantity": quantity,
                "product": product,
                "validity": "DAY",
                "price": price if price else 0,
                "tag": "SCREENER_AUTO",
                "instrument_token": instrument_key,
                "order_type": order_type,
                "transaction_type": transaction_type,
                "disclosed_quantity": 0,
                "trigger_price": trigger_price if trigger_price else 0,
                "is_amo": False,
            }

            url = f"{settings.UPSTOX_BASE_URL}/v2/order/place"
            client = await self._get_client()
            response = await client.post(url, headers=headers, json=order_data)

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    order_id = data.get("data", {}).get("order_id")
                    return order_id, None
                else:
                    return None, f"API Error: {data.get('message', 'Unknown error')}"
            elif response.status_code == 401:
                return None, "Authentication failed - Token may be expired"
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get(
                        "message",
                        error_data.get("errors", [{}])[0].get(
                            "message", "Unknown error"
                        ),
                    )
                except Exception:
                    error_msg = f"HTTP {response.status_code}"
                return None, error_msg
        except Exception as e:
            return None, f"Error: {str(e)}"

    async def get_order_status(self, order_id):
        """Get status of a specific order"""
        try:
            headers = await self.get_headers()
            if not headers:
                return None, "No valid API token found"

            url = f"{settings.UPSTOX_BASE_URL}/v2/order/details?order_id={order_id}"
            client = await self._get_client()
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    return data.get("data"), None
                else:
                    return None, f"API Error: {data.get('message', 'Unknown error')}"
            else:
                return None, f"HTTP {response.status_code}"
        except Exception as e:
            return None, f"Error: {str(e)}"

    async def get_order_book(self):
        """Get all orders for today"""
        try:
            headers = await self.get_headers()
            if not headers:
                return None, "No valid API token found"

            url = f"{settings.UPSTOX_BASE_URL}/v2/order/retrieve-all"
            client = await self._get_client()
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    return data.get("data", []), None
                else:
                    return None, f"API Error: {data.get('message', 'Unknown error')}"
            else:
                return None, f"HTTP {response.status_code}"
        except Exception as e:
            return None, f"Error: {str(e)}"

    async def get_positions(self):
        """Get current positions"""
        try:
            headers = await self.get_headers()
            if not headers:
                return None, "No valid API token found"

            url = f"{settings.UPSTOX_BASE_URL}/v2/portfolio/short-term-positions"
            client = await self._get_client()
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    return data.get("data", []), None
                else:
                    return None, f"API Error: {data.get('message', 'Unknown error')}"
            else:
                return None, f"HTTP {response.status_code}"
        except Exception as e:
            return None, f"Error: {str(e)}"

    async def get_nearest_expiry(self, symbol):
        """Get the nearest expiry date for a stock's options"""
        try:
            contracts, error, _ = await self.get_option_contracts_for_stock(symbol)
            if contracts:
                expiry_dates = set()
                for c in contracts:
                    if c.get("expiry"):
                        expiry_dates.add(c.get("expiry"))
                if expiry_dates:
                    sorted_dates = sorted(expiry_dates)
                    return sorted_dates[0], None  # Return nearest expiry
            return None, error if error else "No expiry dates found"
        except Exception as e:
            return None, str(e)

    async def find_itm_option(self, symbol, current_price, option_type, expiry_date=None):
        """Find the closest In-The-Money (ITM) option contract"""
        try:
            contracts, error, instrument_key = await self.get_option_contracts_for_stock(
                symbol, expiry_date
            )

            if not contracts:
                return None, error if error else "No contracts found"

            # Filter by option type
            filtered_contracts = [
                c for c in contracts if c.get("instrument_type") == option_type
            ]

            if not filtered_contracts:
                return None, f"No {option_type} contracts found"

            # Find ITM options
            itm_contracts = []
            for c in filtered_contracts:
                strike = c.get("strike_price", 0)
                if option_type == "CE":
                    # For Call: ITM when strike < current price
                    if strike < current_price:
                        itm_contracts.append(
                            (c, current_price - strike)
                        )
                else:  # PE
                    # For Put: ITM when strike > current price
                    if strike > current_price:
                        itm_contracts.append(
                            (c, strike - current_price)
                        )

            if not itm_contracts:
                return (
                    None,
                    f"No ITM {option_type} contracts found for price {current_price}",
                )

            # Sort by distance (closest ITM first)
            itm_contracts.sort(key=lambda x: x[1])

            # Return the closest ITM contract
            return itm_contracts[0][0], None

        except Exception as e:
            return None, f"Error: {str(e)}"

    async def validate_token(self):
        """Validate token by calling user profile API"""
        try:
            headers = await self.get_headers()
            if not headers:
                return False, None, "No valid API token found"

            url = settings.USER_PROFILE_URL
            client = await self._get_client()
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    return True, data.get("data"), None
                return False, None, data.get("message", "Unknown error")
            elif response.status_code == 401:
                return False, None, "Token expired or invalid"
            else:
                return False, None, f"HTTP {response.status_code}"
        except Exception as e:
            return False, None, f"Error: {str(e)}"
