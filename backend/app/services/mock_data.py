"""
Mock Data Generator - EXACT COPY from ScreenerV13.py lines 2424-2449.
DO NOT modify any generation logic.
"""
import random
from datetime import datetime, timedelta


def generate_mock_historical_data(symbol, days=200):
    random.seed(hash(symbol) % 2**32)
    base_price = random.uniform(100, 5000)
    volatility = random.uniform(0.01, 0.03)
    data = []
    current_price = base_price

    for i in range(days):
        date = (datetime.now() - timedelta(days=days - i - 1)).strftime("%Y-%m-%d")
        change = random.gauss(0.0002, volatility)
        current_price *= 1 + change
        daily_range = current_price * random.uniform(0.01, 0.03)
        open_price = current_price + random.uniform(-daily_range / 2, daily_range / 2)
        high_price = max(open_price, current_price) + random.uniform(0, daily_range / 2)
        low_price = min(open_price, current_price) - random.uniform(0, daily_range / 2)
        data.append(
            {
                "date": date,
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(current_price, 2),
                "volume": int(random.uniform(100000, 10000000)),
            }
        )
    return data[::-1]
