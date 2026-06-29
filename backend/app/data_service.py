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

MIN_TRADING_DAYS = 60  # Minimum rows needed for stable covariance estimation


def get_historical_data(
    symbols: list[str],
    period: str = "1y"
) -> tuple[np.ndarray, np.ndarray, list[str], dict[str, float]]:
    """
    Fetch historical daily closing prices, compute log returns, and
    return annualised expected returns and the covariance matrix.

    Returns:
        expected_returns: np.ndarray of shape (n_assets,) — annualised mean returns
        cov_matrix: np.ndarray of shape (n_assets, n_assets) — annualised covariance
        valid_symbols: list[str] — symbols for which data was successfully fetched
        last_prices: dict[str, float] — terminal closing price for each valid symbol
            (used to keep current-weight and frontier calculations consistent)
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
    # yfinance returns MultiIndex columns ('Close', ticker) for multi-symbol downloads.
    # For single-symbol downloads the structure can vary by version.
    if isinstance(data.columns, pd.MultiIndex):
        # Multi-level: ('Price', 'Ticker') or ('Close', 'TICKER')
        # Get the 'Close' price level
        if "Close" in data.columns.get_level_values(0):
            closes = data["Close"]
            # If result is a Series (single ticker), wrap as DataFrame
            if isinstance(closes, pd.Series):
                closes = closes.to_frame(name=symbols[0])
        else:
            # Fallback: use first available price column
            closes = data.iloc[:, :len(symbols)].copy()
            closes.columns = symbols[:closes.shape[1]]
    else:
        # Flat columns (single ticker downloaded with group_by=None)
        if "Close" in data.columns:
            closes = data[["Close"]].copy()
            closes.columns = [symbols[0]] if len(symbols) == 1 else symbols[:1]
        else:
            closes = data.copy()
            if closes.shape[1] == len(symbols):
                closes.columns = symbols

    # ── NaN handling ────────────────────────────────────────────────
    # 1. Drop columns with too many NaN values (>30% missing)
    threshold = len(closes) * 0.7
    closes = closes.dropna(axis=1, thresh=int(threshold))

    # 2. Forward-fill small gaps (holidays, short suspensions)
    closes = closes.ffill()

    # 3. Drop any remaining rows with NaN (start-of-series alignment)
    closes = closes.dropna()

    if closes.empty or closes.shape[1] < 2:
        raise ValueError(
            "Insufficient historical data. Need at least 2 instruments with "
            "overlapping trading history."
        )

    # 4. Enforce minimum trading days for stable covariance estimation
    if closes.shape[0] < MIN_TRADING_DAYS:
        raise ValueError(
            f"Only {closes.shape[0]} trading days available, but at least "
            f"{MIN_TRADING_DAYS} are required for stable covariance estimation. "
            f"Try a longer lookback period."
        )

    valid_symbols = list(closes.columns)

    # ── Extract terminal prices ─────────────────────────────────────
    # Use the last close from the SAME data source that generates returns,
    # so current-weight calculations and frontier points share one price snapshot.
    last_prices = {
        sym: float(closes[sym].iloc[-1])
        for sym in valid_symbols
    }

    # ── Compute log returns ─────────────────────────────────────────
    log_returns = np.log(closes / closes.shift(1)).dropna()

    # Annualised expected returns (mean daily log return × trading days)
    expected_returns = log_returns.mean().values * TRADING_DAYS_PER_YEAR

    # Annualised covariance matrix
    # NOTE: .cov() returns the sample covariance of daily log returns.
    # Covariance scales linearly with time under i.i.d. assumption,
    # so we multiply by 252 (NOT sqrt(252) — that's for std dev only).
    cov_matrix = log_returns.cov().values * TRADING_DAYS_PER_YEAR

    # Sanity check: covariance matrix should not contain NaN
    if np.any(np.isnan(cov_matrix)) or np.any(np.isnan(expected_returns)):
        raise ValueError(
            "Computed returns or covariance matrix contains NaN values. "
            "This usually means one or more instruments have constant prices "
            "(e.g., near-cash ETFs like LIQUIDBEES). Try removing them."
        )

    result = (expected_returns, cov_matrix, valid_symbols, last_prices)
    _history_cache.set(cache_key, result)

    return result
