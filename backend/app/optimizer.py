"""
Mean-Variance Portfolio Optimization Engine.
Implements Markowitz efficient frontier using scipy.optimize (SLSQP),
plus Monte Carlo random portfolio simulation for visualization.
"""

import numpy as np
from scipy.optimize import minimize

from app.config import FRONTIER_POINTS


def portfolio_return(weights: np.ndarray, expected_returns: np.ndarray) -> float:
    """Calculate the expected portfolio return."""
    return float(np.dot(weights, expected_returns))


def portfolio_volatility(weights: np.ndarray, cov_matrix: np.ndarray) -> float:
    """Calculate the portfolio volatility (standard deviation)."""
    variance = np.dot(weights.T, np.dot(cov_matrix, weights))
    # Guard against tiny negative values from floating point
    return float(np.sqrt(max(0.0, variance)))


def portfolio_sharpe(
    weights: np.ndarray,
    expected_returns: np.ndarray,
    cov_matrix: np.ndarray,
    risk_free_rate: float,
) -> float:
    """Calculate the Sharpe ratio of a portfolio."""
    ret = portfolio_return(weights, expected_returns)
    vol = portfolio_volatility(weights, cov_matrix)
    if vol < 1e-10:
        return 0.0
    return float((ret - risk_free_rate) / vol)


def compute_portfolio_metrics(
    weights: np.ndarray,
    expected_returns: np.ndarray,
    cov_matrix: np.ndarray,
    risk_free_rate: float,
    symbols: list[str],
) -> dict:
    """
    Compute full metrics for a given weight allocation.

    Returns dict with: expected_return, volatility, sharpe_ratio, weights
    """
    ret = portfolio_return(weights, expected_returns)
    vol = portfolio_volatility(weights, cov_matrix)
    sharpe = (ret - risk_free_rate) / vol if vol > 1e-10 else 0.0

    return {
        "expected_return": round(ret, 6),
        "volatility": round(vol, 6),
        "sharpe_ratio": round(sharpe, 4),
        "weights": {sym: round(float(w), 6) for sym, w in zip(symbols, weights)},
    }


def optimize_max_sharpe(
    expected_returns: np.ndarray,
    cov_matrix: np.ndarray,
    risk_free_rate: float,
    max_weight: float = 1.0,
) -> np.ndarray:
    """
    Find the portfolio weights that maximize the Sharpe ratio.
    Long-only constraint (weights >= 0), weights sum to 1.
    Uses multiple random starting points to avoid local minima.
    """
    n = len(expected_returns)
    bounds = tuple((0.0, min(max_weight, 1.0)) for _ in range(n))
    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]

    def neg_sharpe(w):
        ret = np.dot(w, expected_returns)
        vol = np.sqrt(max(0.0, np.dot(w.T, np.dot(cov_matrix, w))))
        if vol < 1e-10:
            return 0.0
        return -(ret - risk_free_rate) / vol

    best_result = None
    best_val = np.inf

    # Try multiple starting points
    starting_points = [np.ones(n) / n]  # Equal weight
    for _ in range(5):
        rw = np.random.dirichlet(np.ones(n))
        rw = np.clip(rw, 0.0, max_weight)
        rw /= rw.sum()
        starting_points.append(rw)

    for init_w in starting_points:
        result = minimize(
            neg_sharpe,
            init_w,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 1000, "ftol": 1e-12},
        )
        if result.success and result.fun < best_val:
            best_val = result.fun
            best_result = result

    if best_result is None or not best_result.success:
        return np.ones(n) / n

    return best_result.x


def optimize_min_volatility(
    expected_returns: np.ndarray,
    cov_matrix: np.ndarray,
    max_weight: float = 1.0,
) -> np.ndarray:
    """
    Find the portfolio weights that minimize volatility.
    Long-only constraint, weights sum to 1.
    """
    n = len(expected_returns)
    initial_weights = np.ones(n) / n

    def port_vol(w):
        return np.sqrt(max(0.0, np.dot(w.T, np.dot(cov_matrix, w))))

    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]
    bounds = tuple((0.0, min(max_weight, 1.0)) for _ in range(n))

    result = minimize(
        port_vol,
        initial_weights,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 1000, "ftol": 1e-12},
    )

    if not result.success:
        return initial_weights

    return result.x


def compute_efficient_frontier(
    expected_returns: np.ndarray,
    cov_matrix: np.ndarray,
    symbols: list[str],
    n_points: int = 50,
    max_weight: float = 1.0,
) -> list[dict]:
    """
    Generate points on the efficient frontier by sweeping target returns
    from the minimum-variance portfolio return to the maximum achievable return.

    Args:
        expected_returns: Annualised expected returns vector
        cov_matrix: Annualised covariance matrix
        symbols: List of ticker symbols (for labelling weights)
        n_points: Number of frontier points to generate
        max_weight: Maximum weight for any single asset

    Returns a list of dicts, each with: expected_return, volatility, weights.
    """
    n = len(expected_returns)
    capped_max = min(max_weight, 1.0)
    bounds = tuple((0.0, capped_max) for _ in range(n))

    # Find the min-volatility portfolio return as the lower bound
    min_vol_weights = optimize_min_volatility(expected_returns, cov_matrix, max_weight)
    min_ret = portfolio_return(min_vol_weights, expected_returns)
    min_vol = portfolio_volatility(min_vol_weights, cov_matrix)

    # Upper bound: the max return achievable under the weight constraint
    # With max_weight < 1, we can't just put everything in the best asset
    max_ret_weights = _optimize_max_return(expected_returns, n, capped_max)
    max_ret = portfolio_return(max_ret_weights, expected_returns)

    # Ensure we have a valid range
    if max_ret <= min_ret:
        max_ret = min_ret + 0.01

    target_returns = np.linspace(min_ret, max_ret, n_points)
    frontier: list[dict] = []

    # Always include the min-vol point first
    frontier.append({
        "expected_return": round(float(min_ret), 6),
        "volatility": round(float(min_vol), 6),
        "weights": {
            sym: round(float(w), 6)
            for sym, w in zip(symbols, min_vol_weights)
        },
    })

    # Warm start: use min_vol_weights as the first guess
    current_guess = min_vol_weights.copy()

    for target in target_returns[1:]:  # Skip the first (min_vol already added)
        constraints = [
            {"type": "eq", "fun": lambda w: np.sum(w) - 1.0},
            {"type": "eq", "fun": lambda w, t=target: np.dot(w, expected_returns) - t},
        ]

        result = minimize(
            lambda w: np.sqrt(max(0.0, np.dot(w.T, np.dot(cov_matrix, w)))),
            current_guess,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 1000, "ftol": 1e-10},
        )

        if result.success:
            current_guess = result.x  # Warm start next iteration
            vol = portfolio_volatility(result.x, cov_matrix)
            ret = portfolio_return(result.x, expected_returns)
            frontier.append({
                "expected_return": round(ret, 6),
                "volatility": round(vol, 6),
                "weights": {
                    sym: round(float(w), 6)
                    for sym, w in zip(symbols, result.x)
                },
            })

    # Sort by volatility for a clean curve
    frontier.sort(key=lambda p: p["volatility"])

    return frontier


def _optimize_max_return(
    expected_returns: np.ndarray,
    n: int,
    max_weight: float,
) -> np.ndarray:
    """Find the portfolio weights that maximize expected return under constraints."""
    initial_weights = np.ones(n) / n
    bounds = tuple((0.0, max_weight) for _ in range(n))
    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]

    result = minimize(
        lambda w: -np.dot(w, expected_returns),
        initial_weights,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 500},
    )

    if result.success:
        return result.x
    return initial_weights


def generate_monte_carlo_portfolios(
    expected_returns: np.ndarray,
    cov_matrix: np.ndarray,
    symbols: list[str],
    risk_free_rate: float,
    n_portfolios: int = 2000,
    max_weight: float = 1.0,
) -> list[dict]:
    """
    Generate random portfolios via Monte Carlo simulation.
    Each portfolio has random weights (drawn from a Dirichlet distribution),
    respecting the max_weight constraint.

    Returns a list of dicts with: expected_return, volatility, sharpe_ratio.
    """
    n = len(expected_returns)
    capped_max = min(max_weight, 1.0)
    portfolios: list[dict] = []

    for _ in range(n_portfolios):
        # Generate random weights using Dirichlet distribution
        weights = np.random.dirichlet(np.ones(n))

        # Enforce max weight constraint by redistributing excess
        for _ in range(10):  # Iterate a few times to converge
            excess = np.maximum(weights - capped_max, 0.0)
            if excess.sum() < 1e-10:
                break
            weights = np.minimum(weights, capped_max)
            # Redistribute excess proportionally among non-capped assets
            remaining = 1.0 - weights.sum()
            uncapped_mask = weights < capped_max
            if uncapped_mask.sum() > 0:
                weights[uncapped_mask] += remaining * (
                    weights[uncapped_mask] / max(weights[uncapped_mask].sum(), 1e-10)
                )
            weights /= weights.sum()  # Normalize

        ret = portfolio_return(weights, expected_returns)
        vol = portfolio_volatility(weights, cov_matrix)
        sharpe = (ret - risk_free_rate) / vol if vol > 1e-10 else 0.0

        portfolios.append({
            "expected_return": round(ret, 6),
            "volatility": round(vol, 6),
            "sharpe_ratio": round(sharpe, 4),
        })

    return portfolios
