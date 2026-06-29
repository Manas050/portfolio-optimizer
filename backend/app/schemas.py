"""
Pydantic models for API request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional


# ── Instrument Catalog ──────────────────────────────────────────────

class InstrumentInfo(BaseModel):
    """A single instrument from the curated catalog."""
    symbol: str = Field(..., description="Yahoo Finance ticker (e.g. RELIANCE.NS)")
    name: str = Field(..., description="Full instrument name")
    exchange: str = Field(..., description="Exchange: NSE or BSE")
    instrument_type: str = Field(..., description="Type: Stock, ETF, Index")
    sector: Optional[str] = Field(None, description="Sector classification")


# ── Portfolio Holdings ──────────────────────────────────────────────

class PortfolioHolding(BaseModel):
    """A user's holding: the instrument and how many units they own."""
    symbol: str = Field(..., description="Yahoo Finance ticker symbol")
    units: float = Field(..., ge=0, description="Number of units/shares held (0 for hypothetical)")


# ── Analysis Request ────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    """Request body for portfolio analysis."""
    holdings: list[PortfolioHolding] = Field(
        ...,
        min_length=2,
        max_length=30,
        description="2–30 holdings required. Optimizer accuracy degrades beyond 30 assets."
    )
    lookback: str = Field(
        default="1y",
        description="Historical lookback period (yfinance format: 1mo, 3mo, 6mo, 1y, 2y, 5y)"
    )
    risk_free_rate: Optional[float] = Field(
        default=None,
        description="Override default risk-free rate (decimal, e.g., 0.068 for 6.8%)"
    )
    max_weight: Optional[float] = Field(
        default=1.0,
        description="Maximum allowed weight for any single asset (e.g. 0.4 for 40%)"
    )
    n_simulations: int = Field(
        default=50000,
        ge=1000, le=200000,
        description="Number of Monte Carlo simulations to run"
    )


# ── Portfolio Metrics ───────────────────────────────────────────────

class PortfolioMetrics(BaseModel):
    """Metrics for a single portfolio allocation."""
    expected_return: float = Field(..., description="Annualised expected return")
    volatility: float = Field(..., description="Annualised volatility (std dev)")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    weights: dict[str, float] = Field(..., description="Symbol → weight mapping")
    units: Optional[dict[str, float]] = Field(None, description="Symbol → suggested number of units (rounded)")


# ── Efficient Frontier Point ────────────────────────────────────────

class EfficientFrontierPoint(BaseModel):
    """A single point on the efficient frontier."""
    expected_return: float
    volatility: float
    weights: dict[str, float]


class MonteCarloPoint(BaseModel):
    """A single random portfolio from Monte Carlo simulation."""
    expected_return: float
    volatility: float
    sharpe_ratio: float


# ── Simulation Stats ───────────────────────────────────────────────

class SimulationStats(BaseModel):
    """Metadata about the MC-seeded SLSQP optimization run."""
    n_simulations: int = Field(..., description="Number of MC samples generated")
    top_percentile: int = Field(..., description="Fraction of top MC samples used as SLSQP seeds (as %)") 
    selection_method: str = Field(..., description="Selection method: mc_seeded_slsqp")
    best_sharpe: float = Field(..., description="Best Sharpe ratio found by Monte Carlo sampling")
    median_sharpe: float = Field(..., description="Final Sharpe ratio after SLSQP refinement (the true optimal)")
    worst_sharpe: float = Field(..., description="Worst Sharpe ratio across MC cloud")
    cloud_size: int = Field(..., description="Number of MC points returned for visualization")


# ── Price Info ──────────────────────────────────────────────────────

class PriceInfo(BaseModel):
    """Live price data for a single instrument."""
    symbol: str
    price: float
    change_pct: Optional[float] = None
    currency: str = "INR"


# ── Analysis Response ───────────────────────────────────────────────

class HoldingDetail(BaseModel):
    """Detailed info about a single holding in the analysis response."""
    symbol: str
    name: str
    units: float
    price: float
    value: float
    weight: float


class AnalyzeResponse(BaseModel):
    """Full portfolio analysis response."""
    # Holding details
    holdings: list[HoldingDetail]
    total_value: float

    # Portfolio metrics
    current_portfolio: PortfolioMetrics
    optimal_sharpe: PortfolioMetrics
    min_volatility: PortfolioMetrics

    # Efficient frontier curve (derived from MC cloud)
    efficient_frontier: list[EfficientFrontierPoint]

    # Monte Carlo cloud (downsampled for viz)
    monte_carlo: list[MonteCarloPoint] = []

    # Simulation metadata
    simulation_stats: Optional[SimulationStats] = None

    # Config used
    lookback: str
    risk_free_rate: float
    effective_max_weight: float = 1.0

    # Warnings
    warnings: list[str] = []


# ── Price Request ───────────────────────────────────────────────────

class PriceRequest(BaseModel):
    """Request body for fetching live prices."""
    symbols: list[str] = Field(..., min_length=1)
