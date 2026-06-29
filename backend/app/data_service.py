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

def _batch_download_prices(symbols: list[str]) -> dict[str, dict]:
    """
    Download 2 days of close prices for all symbols in ONE yfinance call.
    Returns {symbol: {"price": float, "change_pct": float|None}}.
    Much faster than N individual yf.Ticker() calls.
    """
    if not symbols:
        return {}
    try:
        raw = yf.download(
            symbols,
            period="5d",          # 5 days for change_pct (handles holidays)
            auto_adjust=True,
            progress=False,
            threads=True,
        )
    except Exception as e:
        logger.error("Batch price download failed: %s", e)
        return {}

    # Extract closes — handle MultiIndex (multi-ticker) and flat (single-ticker)
    if isinstance(raw.columns, pd.MultiIndex):
        if "Close" in raw.columns.get_level_values(0):
            closes = raw["Close"]
            if isinstance(closes, pd.Series):
                closes = closes.to_frame(name=symbols[0])
        else:
            closes = pd.DataFrame()
    else:
        if "Close" in raw.columns:
            closes = raw[["Close"]].copy()
            closes.columns = [symbols[0]]
        else:
            closes = pd.DataFrame()

    if closes.empty:
        return {}

    closes = closes.ffill().dropna(how="all")

    result: dict[str, dict] = {}
    for sym in symbols:
        col = sym if sym in closes.columns else None
        if col is None:
            continue
        col_data = closes[col].dropna()
        if col_data.empty:
            continue
        price = float(col_data.iloc[-1])
        change_pct = None
        if len(col_data) >= 2:
            prev = float(col_data.iloc[-2])
            if prev > 0:
                change_pct = round(((price - prev) / prev) * 100, 2)
        result[sym] = {"price": price, "change_pct": change_pct}

    return result


def get_current_prices(symbols: list[str]) -> dict[str, float]:
    """
    Fetch the latest price for each symbol.
    Uses a SINGLE batch yf.download() call (not N individual calls).
    Results cached for PRICE_CACHE_TTL seconds.
    """
    results: dict[str, float] = {}
    symbols_to_fetch: list[str] = []

    for symbol in symbols:
        cached = _price_cache.get(f"price:{symbol}", PRICE_CACHE_TTL)
        if cached is not None:
            results[symbol] = cached
        else:
            symbols_to_fetch.append(symbol)

    if symbols_to_fetch:
        batch = _batch_download_prices(symbols_to_fetch)
        for sym, data in batch.items():
            price = data["price"]
            results[sym] = price
            _price_cache.set(f"price:{sym}", price)
            # Opportunistically cache change_pct too
            if data["change_pct"] is not None:
                _price_cache.set(f"chg:{sym}", data["change_pct"])

    return results


def get_price_changes(symbols: list[str]) -> dict[str, float]:
    """
    Get the day's % change for each symbol.
    Reuses the same batch download as get_current_prices (via shared cache).
    """
    changes: dict[str, float] = {}
    symbols_to_fetch: list[str] = []

    for symbol in symbols:
        cached = _price_cache.get(f"chg:{symbol}", PRICE_CACHE_TTL)
        if cached is not None:
            changes[symbol] = cached
        else:
            symbols_to_fetch.append(symbol)

    if symbols_to_fetch:
        batch = _batch_download_prices(symbols_to_fetch)
        for sym, data in batch.items():
            _price_cache.set(f"price:{sym}", data["price"])
            if data["change_pct"] is not None:
                changes[sym] = data["change_pct"]
                _price_cache.set(f"chg:{sym}", data["change_pct"])

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
