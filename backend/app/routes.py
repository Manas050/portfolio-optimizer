"""
API route definitions for the portfolio optimizer.
"""

import logging
import copy
from fastapi import APIRouter, HTTPException, Query

from app.config import RISK_FREE_RATE, DEFAULT_LOOKBACK_PERIOD
from app.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    HoldingDetail,
    InstrumentInfo,
    PriceInfo,
    PriceRequest,
    SimulationStats,
)
from app.instruments import search_instruments, get_popular_instruments, get_instrument_name, get_instruments_by_sector
from app.data_service import get_current_prices, get_price_changes, get_historical_data
from app.optimizer import compute_portfolio_metrics, run_monte_carlo_simulation

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


@router.get("/health")
async def api_health():
    """Health check — also exposes active config so you can confirm the deployed version."""
    import datetime
    return {
        "status": "ok",
        "engine": "hybrid-mc-slsqp-v3",
        "default_rf_pct": round(RISK_FREE_RATE * 100, 2),
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }


# ── Portfolio Analysis ──────────────────────────────────────────────

@router.post("/portfolio/analyze", response_model=AnalyzeResponse)
async def api_analyze_portfolio(request: AnalyzeRequest):
    """
    Monte Carlo portfolio optimization pipeline:
    1. Fetch current prices → compute holding values and current weights
    2. Fetch historical data → compute expected returns and covariance
    3. Run N Monte Carlo simulations (random weight combinations)
    4. Select median of top 10% by Sharpe as optimal allocation
    5. Select minimum volatility portfolio
    6. Derive efficient frontier from the simulation cloud
    7. Return results with warnings
    """
    symbols = [h.symbol for h in request.holdings]
    units_map = {h.symbol: h.units for h in request.holdings}

    risk_free_rate = request.risk_free_rate if request.risk_free_rate is not None else RISK_FREE_RATE
    if risk_free_rate > 1.0:
        risk_free_rate = risk_free_rate / 100.0
    lookback = request.lookback or DEFAULT_LOOKBACK_PERIOD
    n_simulations = request.n_simulations

    # ── Step 1: Current prices & values ─────────────────────────────
    try:
        prices = get_current_prices(symbols)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch prices: {str(e)}")

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
                weight=0.0,
            )
        )

    if total_value <= 0:
        simulated_total = 100000.0
        allocation_per_asset = simulated_total / len(symbols)
        total_value = 0.0
        for h in holdings_detail:
            h.value = allocation_per_asset
            h.units = round(allocation_per_asset / prices[h.symbol], 2) if prices.get(h.symbol) else 0
            total_value += h.value

    for h in holdings_detail:
        h.weight = round(h.value / total_value, 6)

    # ── Step 2: Historical data ─────────────────────────────────────
    try:
        expected_returns, cov_matrix, valid_symbols, hist_prices = get_historical_data(symbols, lookback)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch historical data: {str(e)}")

    # Handle dropped symbols
    if set(valid_symbols) != set(symbols):
        logger.warning(
            f"Dropped symbols due to insufficient data: "
            f"{set(symbols) - set(valid_symbols)}"
        )
        holdings_detail = [h for h in holdings_detail if h.symbol in set(valid_symbols)]
        total_value = sum(h.value for h in holdings_detail)
        for h in holdings_detail:
            h.weight = round(h.value / total_value, 6) if total_value > 0 else 0.0

    # Use consistent prices from historical data
    consistent_prices = {s: hist_prices.get(s, prices.get(s, 1.0)) for s in valid_symbols}
    for h in holdings_detail:
        if h.symbol in consistent_prices:
            h.price = consistent_prices[h.symbol]
            h.value = round(h.units * h.price, 2)
    total_value = sum(h.value for h in holdings_detail)
    if total_value <= 0:
        total_value = 1.0
    for h in holdings_detail:
        h.weight = round(h.value / total_value, 6)

    # Current weights in valid_symbols order
    weight_map = {h.symbol: h.value for h in holdings_detail}
    current_weights = np.array([
        weight_map.get(s, 0.0) / total_value if total_value > 0 else 0.0
        for s in valid_symbols
    ])

    # Max weight constraint
    max_weight = request.max_weight if request.max_weight is not None else 1.0
    n_assets = len(valid_symbols)
    min_feasible_weight = 1.0 / n_assets
    if max_weight < min_feasible_weight:
        max_weight = min_feasible_weight

    # ── Step 3: Current portfolio metrics ───────────────────────────
    current_metrics = compute_portfolio_metrics(
        current_weights, expected_returns, cov_matrix, risk_free_rate, valid_symbols
    )
    current_metrics["units"] = {s: units_map.get(s, 0.0) for s in valid_symbols}

    # ── Step 4: Run Monte Carlo simulation ──────────────────────────
    mc_results = run_monte_carlo_simulation(
        expected_returns=expected_returns,
        cov_matrix=cov_matrix,
        symbols=valid_symbols,
        risk_free_rate=risk_free_rate,
        n_simulations=n_simulations,
        max_weight=max_weight,
        n_frontier_points=50,
    )

    # Deep-copy before mutation so the original dicts inside mc_results
    # are never aliased — prevents sharpe_ratio corruption.
    optimal_metrics  = copy.deepcopy(mc_results["optimal_sharpe"])
    min_vol_metrics  = copy.deepcopy(mc_results["min_volatility"])

    # Compute suggested units for optimized portfolios
    optimal_metrics["units"] = {
        s: round((optimal_metrics["weights"][s] * total_value) / consistent_prices[s])
        if consistent_prices.get(s, 0) > 0 else 0
        for s in valid_symbols
    }
    min_vol_metrics["units"] = {
        s: round((min_vol_metrics["weights"][s] * total_value) / consistent_prices[s])
        if consistent_prices.get(s, 0) > 0 else 0
        for s in valid_symbols
    }

    # ── Step 5: Generate warnings ───────────────────────────────────
    warnings: list[str] = []

    all_negative = all(
        (er - risk_free_rate) / np.sqrt(cov_matrix[i][i]) < 0
        for i, er in enumerate(expected_returns)
        if np.sqrt(cov_matrix[i][i]) > 1e-10
    )
    if all_negative:
        warnings.append(
            f"⚠ ALL {n_assets} ASSETS UNDERPERFORM THE RISK-FREE RATE ({risk_free_rate*100:.1f}%). "
            "No portfolio combination can achieve a positive Sharpe ratio. "
            "The simulator picks the 'least bad' allocation. Consider diversifying "
            "into other sectors or adjusting the lookback period."
        )

    if optimal_metrics["sharpe_ratio"] < 0:
        warnings.append(
            f"⚠ OPTIMAL SHARPE IS NEGATIVE ({optimal_metrics['sharpe_ratio']:.3f}). "
            "The recommended portfolio still underperforms the risk-free rate. "
            "This is the median of the top 10% simulations — the best robust allocation "
            "given these assets' recent performance."
        )

    max_single_weight = max(optimal_metrics["weights"].values())
    if max_single_weight > 0.95 and n_assets >= 3:
        dominant = max(optimal_metrics["weights"], key=optimal_metrics["weights"].get)
        warnings.append(
            f"⚠ CORNER SOLUTION: {dominant.replace('.NS','')} at {max_single_weight*100:.0f}% allocation. "
            f"Lower the MAX ALLOC constraint (currently {max_weight*100:.0f}%) to force diversification."
        )

    requested_max = request.max_weight if request.max_weight is not None else 1.0
    if requested_max < min_feasible_weight:
        warnings.append(
            f"⚠ MAX ALLOC {requested_max*100:.0f}% is infeasible with {n_assets} assets "
            f"(minimum is {min_feasible_weight*100:.1f}%). Clamped to {max_weight*100:.1f}%."
        )

    stats = mc_results["simulation_stats"]

    # ── Step 6: Return response ─────────────────────────────────────
    return AnalyzeResponse(
        holdings=holdings_detail,
        total_value=round(total_value, 2),
        current_portfolio=current_metrics,
        optimal_sharpe=optimal_metrics,
        min_volatility=min_vol_metrics,
        efficient_frontier=mc_results["efficient_frontier"],
        monte_carlo=mc_results["monte_carlo_cloud"],
        simulation_stats=SimulationStats(**stats),
        lookback=lookback,
        risk_free_rate=risk_free_rate,
        effective_max_weight=max_weight,
        warnings=warnings,
    )
