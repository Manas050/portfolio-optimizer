"""
API route definitions for the portfolio optimizer.
"""

import logging
from fastapi import APIRouter, HTTPException, Query

from app.config import RISK_FREE_RATE, DEFAULT_LOOKBACK_PERIOD
from app.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    HoldingDetail,
    InstrumentInfo,
    PriceInfo,
    PriceRequest,
)
from app.instruments import search_instruments, get_popular_instruments, get_instrument_name, get_instruments_by_sector
from app.data_service import get_current_prices, get_price_changes, get_historical_data
from app.optimizer import (
    compute_portfolio_metrics,
    optimize_max_sharpe,
    optimize_min_volatility,
    compute_efficient_frontier,
    generate_monte_carlo_portfolios,
)

import numpy as np

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")


# ── Instrument Search ───────────────────────────────────────────────

@router.get("/search", response_model=list[InstrumentInfo])
async def api_search_instruments(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=50),
):
    """Search the instrument catalog by name, symbol, or sector."""
    results = search_instruments(q, limit=limit)
    return results


@router.get("/instruments/popular", response_model=list[InstrumentInfo])
async def api_popular_instruments():
    """Return popular instruments for quick selection."""
    return get_popular_instruments()


@router.get("/instruments/sectors")
async def api_sectors_instruments():
    """Return all instruments grouped by sector."""
    return get_instruments_by_sector()


# ── Live Prices ─────────────────────────────────────────────────────

@router.post("/prices", response_model=list[PriceInfo])
async def api_get_prices(request: PriceRequest):
    """Fetch live prices for the given symbols."""
    try:
        prices = get_current_prices(request.symbols)
        changes = get_price_changes(request.symbols)

        return [
            PriceInfo(
                symbol=symbol,
                price=price,
                change_pct=changes.get(symbol),
            )
            for symbol, price in prices.items()
        ]
    except Exception as e:
        logger.error(f"Error fetching prices: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch prices: {str(e)}")


# ── Portfolio Analysis ──────────────────────────────────────────────

@router.post("/portfolio/analyze", response_model=AnalyzeResponse)
async def api_analyze_portfolio(request: AnalyzeRequest):
    """
    Full portfolio analysis:
    1. Fetch current prices → compute holding values and weights
    2. Fetch historical data → compute expected returns and covariance
    3. Optimise: max Sharpe, min volatility
    4. Generate efficient frontier
    5. Return everything
    """
    symbols = [h.symbol for h in request.holdings]
    units_map = {h.symbol: h.units for h in request.holdings}

    risk_free_rate = request.risk_free_rate if request.risk_free_rate is not None else RISK_FREE_RATE
    if risk_free_rate > 1.0:
        risk_free_rate = risk_free_rate / 100.0
    lookback = request.lookback or DEFAULT_LOOKBACK_PERIOD

    # ── Step 1: Current prices & values ─────────────────────────────
    try:
        prices = get_current_prices(symbols)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch prices: {str(e)}")

    # Check all symbols have prices
    missing = [s for s in symbols if s not in prices]
    if missing:
        raise HTTPException(
            status_code=404,
            detail=f"Could not fetch prices for: {', '.join(missing)}. "
                   "Please verify the ticker symbols.",
        )

    # Compute values and weights
    holdings_detail: list[HoldingDetail] = []
    total_value = 0.0
    for symbol in symbols:
        value = units_map[symbol] * prices[symbol]
        total_value += value
        holdings_detail.append(
            HoldingDetail(
                symbol=symbol,
                name=get_instrument_name(symbol),
                units=units_map[symbol],
                price=prices[symbol],
                value=round(value, 2),
                weight=0.0,  # will be filled after total is known
            )
        )

    if total_value <= 0:
        # If no units provided, simulate a hypothetical 1,00,000 INR equal-weighted portfolio
        simulated_total = 100000.0
        allocation_per_asset = simulated_total / len(symbols)
        total_value = 0.0
        for h in holdings_detail:
            h.value = allocation_per_asset
            h.units = round(allocation_per_asset / prices[h.symbol], 2) if prices.get(h.symbol) else 0
            total_value += h.value

    # Fill in weights
    for h in holdings_detail:
        h.weight = round(h.value / total_value, 6)

    current_weights = np.array([h.weight for h in holdings_detail])

    # ── Step 2: Historical data ─────────────────────────────────────
    try:
        expected_returns, cov_matrix, valid_symbols = get_historical_data(symbols, lookback)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch historical data: {str(e)}")

    # Reorder weights to match valid_symbols order from yfinance
    # (yfinance alphabetises columns, so we must align weights accordingly)
    if set(valid_symbols) != set(symbols):
        # Some symbols were dropped due to insufficient data
        logger.warning(
            f"Dropped symbols due to insufficient data: "
            f"{set(symbols) - set(valid_symbols)}"
        )
        # Rebuild holdings for valid symbols
        holdings_detail = [h for h in holdings_detail if h.symbol in set(valid_symbols)]
        total_value = sum(h.value for h in holdings_detail)
        for h in holdings_detail:
            h.weight = round(h.value / total_value, 6) if total_value > 0 else 0.0

    # Always build current_weights in valid_symbols order
    weight_map = {h.symbol: h.value for h in holdings_detail}
    current_weights = np.array([
        weight_map.get(s, 0.0) / total_value if total_value > 0 else 0.0
        for s in valid_symbols
    ])

    max_weight = request.max_weight if request.max_weight is not None else 1.0
    if max_weight < 1.0 / len(valid_symbols):
        max_weight = 1.0 # fallback if impossible

    # ── Step 3: Optimise ────────────────────────────────────────────
    current_metrics = compute_portfolio_metrics(
        current_weights, expected_returns, cov_matrix, risk_free_rate, valid_symbols
    )
    current_metrics["units"] = {s: units_map.get(s, 0.0) for s in valid_symbols}

    max_sharpe_weights = optimize_max_sharpe(expected_returns, cov_matrix, risk_free_rate, max_weight)
    max_sharpe_metrics = compute_portfolio_metrics(
        max_sharpe_weights, expected_returns, cov_matrix, risk_free_rate, valid_symbols
    )
    max_sharpe_metrics["units"] = {
        s: round((max_sharpe_metrics["weights"][s] * total_value) / prices[s]) if prices[s] > 0 else 0
        for s in valid_symbols
    }

    min_vol_weights = optimize_min_volatility(expected_returns, cov_matrix, max_weight)
    min_vol_metrics = compute_portfolio_metrics(
        min_vol_weights, expected_returns, cov_matrix, risk_free_rate, valid_symbols
    )
    min_vol_metrics["units"] = {
        s: round((min_vol_metrics["weights"][s] * total_value) / prices[s]) if prices[s] > 0 else 0
        for s in valid_symbols
    }

    # ── Step 4: Efficient frontier ──────────────────────────────────
    frontier = compute_efficient_frontier(
        expected_returns, cov_matrix, valid_symbols,
        n_points=50, max_weight=max_weight,
    )

    # ── Step 5: Monte Carlo simulation ──────────────────────────────
    monte_carlo = generate_monte_carlo_portfolios(
        expected_returns, cov_matrix, valid_symbols,
        risk_free_rate=risk_free_rate,
        n_portfolios=2000, max_weight=max_weight,
    )

    # ── Step 6: Return response ─────────────────────────────────────
    return AnalyzeResponse(
        holdings=holdings_detail,
        total_value=round(total_value, 2),
        current_portfolio=current_metrics,
        optimal_sharpe=max_sharpe_metrics,
        min_volatility=min_vol_metrics,
        efficient_frontier=frontier,
        monte_carlo=monte_carlo,
        lookback=lookback,
        risk_free_rate=risk_free_rate,
    )
