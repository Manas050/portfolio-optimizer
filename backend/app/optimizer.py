"""
Monte Carlo Portfolio Optimization Engine.

Instead of analytical SLSQP optimization, this engine generates a large number
of random portfolio weight combinations, evaluates each for return/risk/Sharpe,
and selects the MEDIAN of the top performers as the recommended allocation.

This is more robust than gradient-based optimization because:
1. It doesn't get stuck in local minima
2. Choosing the median (not the best) avoids overfitting to noise
3. The full simulation cloud provides visual proof of optimality
"""

import numpy as np
from app.config import TRADING_DAYS_PER_YEAR


# ── Core Portfolio Math ─────────────────────────────────────────────

def portfolio_return(weights: np.ndarray, expected_returns: np.ndarray) -> float:
    """Annualised expected portfolio return."""
    return float(np.dot(weights, expected_returns))


def portfolio_volatility(weights: np.ndarray, cov_matrix: np.ndarray) -> float:
    """Annualised portfolio volatility (standard deviation)."""
    variance = np.dot(weights.T, np.dot(cov_matrix, weights))
    return float(np.sqrt(max(0.0, variance)))


def portfolio_sharpe(
    weights: np.ndarray,
    expected_returns: np.ndarray,
    cov_matrix: np.ndarray,
    risk_free_rate: float,
) -> float:
    """Portfolio Sharpe ratio = (Rp - Rf) / σp."""
    ret = portfolio_return(weights, expected_returns)
    vol = portfolio_volatility(weights, cov_matrix)
    if vol < 1e-8:
        return 0.0
    return float((ret - risk_free_rate) / vol)


def compute_portfolio_metrics(
    weights: np.ndarray,
    expected_returns: np.ndarray,
    cov_matrix: np.ndarray,
    risk_free_rate: float,
    symbols: list[str],
) -> dict:
    """Compute full metrics for a given weight allocation."""
    ret = portfolio_return(weights, expected_returns)
    vol = portfolio_volatility(weights, cov_matrix)
    sharpe = (ret - risk_free_rate) / vol if vol > 1e-8 else 0.0

    return {
        "expected_return": round(ret, 6),
        "volatility": round(vol, 6),
        "sharpe_ratio": round(sharpe, 4),
        "weights": {sym: round(float(w), 6) for sym, w in zip(symbols, weights)},
    }


# ── Monte Carlo Simulation Engine ──────────────────────────────────

def _generate_random_weights(
    n_assets: int,
    n_portfolios: int,
    max_weight: float = 1.0,
) -> np.ndarray:
    """
    Generate n_portfolios random weight vectors using Dirichlet distribution.
    Each row sums to 1.0 and respects the max_weight constraint.

    Returns: np.ndarray of shape (n_portfolios, n_assets)
    """
    capped = min(max_weight, 1.0)
    all_weights = np.zeros((n_portfolios, n_assets))

    for i in range(n_portfolios):
        w = np.random.dirichlet(np.ones(n_assets))

        # Enforce max weight via iterative redistribution
        for _ in range(15):
            excess = np.maximum(w - capped, 0.0)
            if excess.sum() < 1e-10:
                break
            w = np.minimum(w, capped)
            remaining = 1.0 - w.sum()
            uncapped = w < capped
            if uncapped.sum() > 0:
                w[uncapped] += remaining * (w[uncapped] / max(w[uncapped].sum(), 1e-10))
            w /= w.sum()

        all_weights[i] = w

    return all_weights


def run_monte_carlo_simulation(
    expected_returns: np.ndarray,
    cov_matrix: np.ndarray,
    symbols: list[str],
    risk_free_rate: float,
    n_simulations: int = 50000,
    max_weight: float = 1.0,
) -> dict:
    """
    Run the full Monte Carlo optimization pipeline.

    1. Generate n_simulations random portfolios
    2. Compute return, volatility, Sharpe for each
    3. Sort by Sharpe ratio
    4. Select the MEDIAN of the top 10% as the optimal portfolio
    5. Select the minimum volatility portfolio
    6. Derive the efficient frontier empirically from the cloud

    Returns a dict with:
        - optimal_sharpe: metrics for the median-of-top-10% portfolio
        - min_volatility: metrics for the lowest-volatility portfolio
        - efficient_frontier: list of frontier points
        - monte_carlo_cloud: list of all simulation points (for visualization)
        - simulation_stats: metadata about the run
    """
    n = len(expected_returns)

    # ── Step 1: Generate random portfolios ──────────────────────────
    all_weights = _generate_random_weights(n, n_simulations, max_weight)

    # ── Step 2: Vectorised metric computation ───────────────────────
    # Portfolio returns: (n_sim,) = (n_sim, n) @ (n,)
    returns = all_weights @ expected_returns

    # Portfolio volatilities: σ = sqrt(wᵀΣw) for each row
    # Efficient: (n_sim, n) @ (n, n) → (n_sim, n), then row-wise dot with weights
    cov_products = all_weights @ cov_matrix  # (n_sim, n)
    variances = np.sum(cov_products * all_weights, axis=1)  # (n_sim,)
    variances = np.maximum(variances, 0.0)  # Guard against tiny negatives
    volatilities = np.sqrt(variances)

    # Sharpe ratios
    sharpes = np.where(
        volatilities > 1e-8,
        (returns - risk_free_rate) / volatilities,
        0.0,
    )

    # ── Step 3: Find optimal portfolio (median of top 10%) ──────────
    sharpe_sorted_indices = np.argsort(sharpes)[::-1]  # Descending
    top_10_pct_count = max(1, n_simulations // 10)
    top_indices = sharpe_sorted_indices[:top_10_pct_count]

    # Median index within the top 10%
    median_idx_in_top = top_indices[len(top_indices) // 2]
    optimal_weights = all_weights[median_idx_in_top]

    optimal_metrics = compute_portfolio_metrics(
        optimal_weights, expected_returns, cov_matrix, risk_free_rate, symbols
    )

    # ── Step 4: Find minimum volatility portfolio ───────────────────
    min_vol_idx = np.argmin(volatilities)
    min_vol_weights = all_weights[min_vol_idx]

    min_vol_metrics = compute_portfolio_metrics(
        min_vol_weights, expected_returns, cov_matrix, risk_free_rate, symbols
    )

    # ── Step 5: Derive efficient frontier from MC cloud ─────────────
    frontier = _derive_frontier_from_cloud(
        returns, volatilities, all_weights, symbols, n_bins=50
    )

    # ── Step 6: Build cloud for visualization ───────────────────────
    # Downsample to 3000 points for frontend performance
    downsample_n = min(3000, n_simulations)
    sample_indices = np.random.choice(n_simulations, downsample_n, replace=False)

    cloud = []
    for idx in sample_indices:
        cloud.append({
            "expected_return": round(float(returns[idx]), 6),
            "volatility": round(float(volatilities[idx]), 6),
            "sharpe_ratio": round(float(sharpes[idx]), 4),
        })

    # ── Step 7: Simulation stats ────────────────────────────────────
    stats = {
        "n_simulations": n_simulations,
        "top_percentile": 10,
        "selection_method": "median_of_top_10pct",
        "best_sharpe": round(float(sharpes[sharpe_sorted_indices[0]]), 4),
        "median_sharpe": round(float(sharpes[median_idx_in_top]), 4),
        "worst_sharpe": round(float(sharpes[sharpe_sorted_indices[-1]]), 4),
        "cloud_size": downsample_n,
    }

    return {
        "optimal_sharpe": optimal_metrics,
        "min_volatility": min_vol_metrics,
        "efficient_frontier": frontier,
        "monte_carlo_cloud": cloud,
        "simulation_stats": stats,
    }


def _derive_frontier_from_cloud(
    returns: np.ndarray,
    volatilities: np.ndarray,
    all_weights: np.ndarray,
    symbols: list[str],
    n_bins: int = 50,
) -> list[dict]:
    """
    Derive the efficient frontier empirically from the Monte Carlo cloud.

    Method: bin portfolios by volatility, take the highest-return portfolio
    in each bin, then filter for monotonically increasing returns (efficient only).
    """
    vol_min, vol_max = volatilities.min(), volatilities.max()
    if vol_max - vol_min < 1e-10:
        return []

    bin_edges = np.linspace(vol_min, vol_max, n_bins + 1)
    raw_frontier: list[dict] = []

    for i in range(n_bins):
        lo, hi = bin_edges[i], bin_edges[i + 1]
        mask = (volatilities >= lo) & (volatilities < hi)
        if not mask.any():
            continue

        # Best return in this volatility bin
        bin_returns = returns[mask]
        best_in_bin = np.argmax(bin_returns)

        # Map back to original index
        bin_indices = np.where(mask)[0]
        orig_idx = bin_indices[best_in_bin]

        raw_frontier.append({
            "expected_return": round(float(returns[orig_idx]), 6),
            "volatility": round(float(volatilities[orig_idx]), 6),
            "weights": {
                sym: round(float(w), 6)
                for sym, w in zip(symbols, all_weights[orig_idx])
            },
        })

    # Sort by volatility
    raw_frontier.sort(key=lambda p: p["volatility"])

    # Filter inefficient points (keep monotonically increasing returns only)
    efficient: list[dict] = []
    if raw_frontier:
        efficient.append(raw_frontier[0])
        for p in raw_frontier[1:]:
            if p["expected_return"] >= efficient[-1]["expected_return"]:
                efficient.append(p)

    return efficient
