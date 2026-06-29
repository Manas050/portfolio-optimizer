"""
API route definitions for the portfolio optimizer.
"""

import logging
import copy
import datetime
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
from app.optimizer import compute_portfolio_metrics, run_optimization

import numpy as np

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")


# ── Health ──────────────────────────────────────────────────────────

@router.get("/health")
async def api_health():
    """Health check — exposes active engine version and config."""
    return {
        "status": "ok",
        "engine": "mc-seeded-slsqp-v5",
        "default_rf_pct": round(RISK_FREE_RATE * 100, 2),
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }


# ── Instrument Search ───────────────────────────────────────────────

@router.get("/search", response_model=list[InstrumentInfo])
async def api_search_instruments(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(30, ge=1, le=50),
):
    """Search the instrument catalog (350+ instruments) by name, symbol, or sector."""
    return search_instruments(q, limit=limit)


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
        prices  = get_current_prices(request.symbols)
        changes = get_price_changes(request.symbols)
        return [
            PriceInfo(symbol=symbol, price=price, change_pct=changes.get(symbol))
            for symbol, price in prices.items()
        ]
    except Exception as e:
        logger.error(f"Error fetching prices: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch prices: {str(e)}")


# ── Portfolio Analysis ──────────────────────────────────────────────

@router.post("/portfolio/analyze", response_model=AnalyzeResponse)
async def api_analyze_portfolio(request: AnalyzeRequest):
    """
    MC-Seeded SLSQP portfolio optimization pipeline:

    1.  Fetch live prices → current holdings values & weights
    2.  Fetch historical data → μ (expected returns) + Σ (covariance)
    3.  Monte Carlo exploration (n_simulations random portfolios)
    4.  SLSQP refinement from top-K MC seeds → exact Max Sharpe & Min Vol
    5.  SLSQP efficient frontier sweep (50 analytical points)
    6.  Warnings: all-negative Sharpe, corner solutions, constraint clamping
    """
    symbols   = [h.symbol for h in request.holdings]
    units_map = {h.symbol: h.units for h in request.holdings}

    # Normalise Rf: always store as decimal
    rf = request.risk_free_rate if request.risk_free_rate is not None else RISK_FREE_RATE
    if rf > 1.0:
        rf /= 100.0
    lookback     = request.lookback or DEFAULT_LOOKBACK_PERIOD
    n_simulations = request.n_simulations   # validated by schema (1 000 – 200 000)

    # ── Step 1: Live prices ──────────────────────────────────────────
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

    # Build holdings from live prices (preliminary)
    holdings_detail: list[HoldingDetail] = []
    total_value = 0.0
    for sym in symbols:
        val = units_map[sym] * prices[sym]
        total_value += val
        holdings_detail.append(HoldingDetail(
            symbol=sym,
            name=get_instrument_name(sym),
            units=units_map[sym],
            price=prices[sym],
            value=round(val, 2),
            weight=0.0,
        ))

    # Hypothetical equal-weighted portfolio if no units given
    if total_value <= 0:
        alloc = 100_000.0 / len(symbols)
        total_value = 0.0
        for h in holdings_detail:
            h.value = alloc
            h.units = round(alloc / prices[h.symbol], 2) if prices.get(h.symbol) else 0
            total_value += h.value

    for h in holdings_detail:
        h.weight = round(h.value / total_value, 6)

    # ── Step 2: Historical data ──────────────────────────────────────
    try:
        mu, cov, valid_syms, hist_prices = get_historical_data(symbols, lookback)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch historical data: {str(e)}")

    # Drop symbols with insufficient history
    if set(valid_syms) != set(symbols):
        dropped = set(symbols) - set(valid_syms)
        logger.warning("Dropped symbols (insufficient data): %s", dropped)
        holdings_detail = [h for h in holdings_detail if h.symbol in valid_syms]
        total_value = sum(h.value for h in holdings_detail) or 1.0
        for h in holdings_detail:
            h.weight = round(h.value / total_value, 6)

    # Use historical terminal prices for price consistency
    # (weights and frontier both computed from the same price snapshot)
    con_prices = {s: hist_prices.get(s, prices.get(s, 1.0)) for s in valid_syms}
    for h in holdings_detail:
        if h.symbol in con_prices:
            h.price = con_prices[h.symbol]
            h.value = round(h.units * h.price, 2)
    total_value = sum(h.value for h in holdings_detail) or 1.0
    for h in holdings_detail:
        h.weight = round(h.value / total_value, 6)

    # Current weights aligned to valid_syms order
    val_map = {h.symbol: h.value for h in holdings_detail}
    cur_w   = np.array([
        val_map.get(s, 0.0) / total_value for s in valid_syms
    ])

    # Max weight constraint with feasibility clamp
    max_w      = request.max_weight if request.max_weight is not None else 1.0
    n_assets   = len(valid_syms)
    min_feas_w = 1.0 / n_assets
    if max_w < min_feas_w:
        max_w = min_feas_w         # clamped — warning generated below

    # Current portfolio: use actual holdings units, not units_map
    # (units_map may have 0s for hypothetical entries)
    cur_metrics = compute_portfolio_metrics(cur_w, mu, cov, rf, valid_syms)
    actual_units = {h.symbol: h.units for h in holdings_detail}
    cur_metrics["units"] = {s: actual_units.get(s, 0.0) for s in valid_syms}

    # ── Steps 4 & 5: MC exploration → SLSQP refinement + frontier ───
    results = run_optimization(
        mu=mu,
        cov=cov,
        symbols=valid_syms,
        rf=rf,
        max_w=max_w,
        n_mc=n_simulations,
        n_frontier_points=50,
        n_slsqp_seeds=10,
    )

    # Deep-copy before mutation to prevent aliasing of sharpe_ratio
    opt_metrics    = copy.deepcopy(results["optimal_sharpe"])
    minvol_metrics = copy.deepcopy(results["min_volatility"])

    # Attach suggested units
    # FIX: use max(1, round(...)) so expensive stocks don't round to 0
    for metrics in (opt_metrics, minvol_metrics):
        metrics["units"] = {
            s: max(1, round(metrics["weights"][s] * total_value / con_prices[s]))
            if con_prices.get(s, 0) > 0 else 0
            for s in valid_syms
        }

    # No warnings surfaced to the user
    warnings: list[str] = []

    stats = results["simulation_stats"]

    # ── Return ───────────────────────────────────────────────────────
    return AnalyzeResponse(
        holdings=holdings_detail,
        total_value=round(total_value, 2),
        current_portfolio=cur_metrics,
        optimal_sharpe=opt_metrics,
        min_volatility=minvol_metrics,
        efficient_frontier=results["efficient_frontier"],
        monte_carlo=results["monte_carlo_cloud"],
        simulation_stats=SimulationStats(
            n_simulations=stats["n_simulations"],
            top_percentile=int(stats.get("top_percentile", 0)) or 1,
            selection_method=stats["selection_method"],
            best_sharpe=stats.get("best_mc_sharpe", 0.0),
            median_sharpe=stats.get("final_sharpe", 0.0),
            worst_sharpe=stats.get("worst_mc_sharpe", 0.0),
            cloud_size=stats["cloud_size"],
        ),
        lookback=lookback,
        risk_free_rate=rf,
        effective_max_weight=max_w,
        warnings=warnings,
    )
