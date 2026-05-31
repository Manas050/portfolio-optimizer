"""
Yahoo Finance data layer with TTL-based caching.
Handles fetching current prices and historical returns for Indian market instruments.
"""

import time
import logging
import numpy as np
import pandas as pd
import yfinance as yf

from app.config import PRICE_CACHE_TTL, HISTORICAL_CACHE_TTL, TRADING_DAYS_PER_YEAR

logger = logging.getLogger(__name__)


# ── In-Memory Cache ─────────────────────────────────────────────────

class TTLCache:
    """Simple TTL-based cache."""

    def __init__(self):
        self._store: dict[str, tuple[float, object]] = {}

    def get(self, key: str, ttl: int) -> object | None:
        if key in self._store:
            timestamp, value = self._store[key]
            if time.time() - timestamp < ttl:
                return value
            else:
                del self._store[key]
        return None

    def set(self, key: str, value: object):
        self._store[key] = (time.time(), value)

    def clear(self):
        self._store.clear()


_price_cache = TTLCache()
_history_cache = TTLCache()


# ── Price Fetching ──────────────────────────────────────────────────

def get_current_prices(symbols: list[str]) -> dict[str, float]:
    """
    Fetch the latest available price for each symbol.
    Uses regularMarketPrice from yfinance fast_info, falling back to last close.
    Results are cached for PRICE_CACHE_TTL seconds.
    """
    results: dict[str, float] = {}
    symbols_to_fetch: list[str] = []

    # Check cache first
    for symbol in symbols:
        cached = _price_cache.get(f"price:{symbol}", PRICE_CACHE_TTL)
        if cached is not None:
            results[symbol] = cached
        else:
            symbols_to_fetch.append(symbol)

    if not symbols_to_fetch:
        return results

    # Fetch uncached prices
    for symbol in symbols_to_fetch:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            price = getattr(info, "last_price", None)
            if price is None or price <= 0:
                # Fallback: get last close from recent history
                hist = ticker.history(period="5d")
                if not hist.empty:
                    price = float(hist["Close"].iloc[-1])
                else:
                    logger.warning(f"No price data for {symbol}")
                    continue

            results[symbol] = float(price)
            _price_cache.set(f"price:{symbol}", float(price))
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            continue

    return results


def get_price_changes(symbols: list[str]) -> dict[str, float]:
    """
    Get the day's percentage change for each symbol.
    """
    changes: dict[str, float] = {}
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            if len(hist) >= 2:
                prev_close = float(hist["Close"].iloc[-2])
                curr_close = float(hist["Close"].iloc[-1])
                if prev_close > 0:
                    changes[symbol] = ((curr_close - prev_close) / prev_close) * 100
        except Exception as e:
            logger.error(f"Error fetching change for {symbol}: {e}")
    return changes


# ── Historical Returns ──────────────────────────────────────────────

def get_historical_data(
    symbols: list[str],
    period: str = "1y"
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """
    Fetch historical daily closing prices, compute log returns, and
    return annualised expected returns and the covariance matrix.

    Returns:
        expected_returns: np.ndarray of shape (n_assets,) — annualised mean returns
        cov_matrix: np.ndarray of shape (n_assets, n_assets) — annualised covariance
        valid_symbols: list[str] — symbols for which data was successfully fetched
    """
    cache_key = f"hist:{'|'.join(sorted(symbols))}:{period}"
    cached = _history_cache.get(cache_key, HISTORICAL_CACHE_TTL)
    if cached is not None:
        return cached

    # Download historical data for all symbols at once
    try:
        data = yf.download(
            symbols,
            period=period,
            auto_adjust=True,
            progress=False,
            threads=True,
        )
    except Exception as e:
        logger.error(f"Error downloading historical data: {e}")
        raise ValueError(f"Failed to fetch historical data: {e}")

    # Extract closing prices
    if isinstance(data.columns, pd.MultiIndex):
        closes = data["Close"]
    else:
        # Single ticker case
        closes = data[["Close"]]
        closes.columns = symbols

    # Drop columns with too many NaN values (>30% missing)
    threshold = len(closes) * 0.7
    closes = closes.dropna(axis=1, thresh=int(threshold))
    closes = closes.dropna()

    if closes.empty or closes.shape[1] < 2:
        raise ValueError(
            "Insufficient historical data. Need at least 2 instruments with "
            "overlapping trading history."
        )

    valid_symbols = list(closes.columns)

    # Compute log returns
    log_returns = np.log(closes / closes.shift(1)).dropna()

    # Annualised expected returns (mean daily return × trading days)
    expected_returns = log_returns.mean().values * TRADING_DAYS_PER_YEAR

    # Annualised covariance matrix
    cov_matrix = log_returns.cov().values * TRADING_DAYS_PER_YEAR

    result = (expected_returns, cov_matrix, valid_symbols)
    _history_cache.set(cache_key, result)

    return result
