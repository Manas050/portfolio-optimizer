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
    units: float = Field(..., gt=0, description="Number of units/shares held")


# ── Analysis Request ────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    """Request body for portfolio analysis."""
    holdings: list[PortfolioHolding] = Field(
        ..., min_length=2,
        description="At least 2 holdings required for diversification analysis"
    )
    lookback: str = Field(
        default="1y",
        description="Historical lookback period (yfinance format: 1mo, 3mo, 6mo, 1y, 2y, 5y)"
    )
    risk_free_rate: Optional[float] = Field(
        default=None,
        description="Annual risk-free rate override (default: India 10Y yield ~0.07)"
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

    # Efficient frontier curve
    efficient_frontier: list[EfficientFrontierPoint]

    # Config used
    lookback: str
    risk_free_rate: float


# ── Price Request ───────────────────────────────────────────────────

class PriceRequest(BaseModel):
    """Request body for fetching live prices."""
    symbols: list[str] = Field(..., min_length=1)
