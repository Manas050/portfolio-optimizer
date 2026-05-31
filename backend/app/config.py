"""
Application configuration constants.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Risk-free rate for Sharpe Ratio (India 10Y government bond yield ~7%)
RISK_FREE_RATE = float(os.getenv("RISK_FREE_RATE", "0.07"))

# Default lookback period for historical returns (yfinance period strings)
DEFAULT_LOOKBACK_PERIOD = os.getenv("DEFAULT_LOOKBACK_PERIOD", "1y")

# Number of trading days in a year (India: ~252)
TRADING_DAYS_PER_YEAR = 252

# Cache TTL for live prices (seconds)
PRICE_CACHE_TTL = int(os.getenv("PRICE_CACHE_TTL", "60"))

# Cache TTL for historical data (seconds)
HISTORICAL_CACHE_TTL = int(os.getenv("HISTORICAL_CACHE_TTL", "300"))

# Number of points on the efficient frontier
FRONTIER_POINTS = 50

# CORS origins (Vite dev server & Production)
cors_env = os.getenv("CORS_ORIGINS", "*")
if cors_env == "*":
    CORS_ORIGINS = ["*"]
else:
    CORS_ORIGINS = [origin.strip() for origin in cors_env.split(",")]
