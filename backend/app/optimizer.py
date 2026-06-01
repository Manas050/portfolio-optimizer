"""
Mean-Variance Portfolio Optimization Engine.
Implements Markowitz efficient frontier using scipy.optimize (SLSQP).
"""

import numpy as np
from scipy.optimize import minimize

from app.config import FRONTIER_POINTS


def portfolio_return(weights: np.ndarray, expected_returns: np.ndarray) -> float:
    """Calculate the expected portfolio return."""
    return float(np.dot(weights, expected_returns))


def portfolio_volatility(weights: np.ndarray, cov_matrix: np.ndarray) -> float:
    """Calculate the portfolio volatility (standard deviation)."""
    return float(np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))))


def portfolio_sharpe(
    weights: np.ndarray,
    expected_returns: np.ndarray,
    cov_matrix: np.ndarray,
    risk_free_rate: float,
) -> float:
    """Calculate the Sharpe ratio of a portfolio."""
    ret = portfolio_return(weights, expected_returns)
    vol = portfolio_volatility(weights, cov_matrix)
    if vol == 0:
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
    sharpe = (ret - risk_free_rate) / vol if vol > 0 else 0.0

    return {
        "expected_return": round(ret, 4),
        "volatility": round(vol, 4),
        "sharpe_ratio": round(sharpe, 4),
        "weights": {sym: round(float(w), 4) for sym, w in zip(symbols, weights)},
    }


def optimize_max_sharpe(
    expected_returns: np.ndarray,
    cov_matrix: np.ndarray,
    risk_free_rate: float,
) -> np.ndarray:
    """
    Find the portfolio weights that maximize the Sharpe ratio.
    Long-only constraint (weights >= 0), weights sum to 1.
    """
    n = len(expected_returns)
    initial_weights = np.ones(n) / n

    # Minimise the negative Sharpe ratio
    def neg_sharpe(w):
        ret = np.dot(w, expected_returns)
        vol = np.sqrt(np.dot(w.T, np.dot(cov_matrix, w)))
        if vol == 0:
            return 0
        return -(ret - risk_free_rate) / vol

    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]
    bounds = tuple((0.0, 1.0) for _ in range(n))

    result = minimize(
        neg_sharpe,
        initial_weights,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 1000, "ftol": 1e-12},
    )

    if not result.success:
        # Fallback to equal weights if optimisation fails
        return initial_weights

    return result.x


def optimize_min_volatility(
    expected_returns: np.ndarray,
    cov_matrix: np.ndarray,
) -> np.ndarray:
    """
    Find the portfolio weights that minimize volatility.
    Long-only constraint, weights sum to 1.
    """
    n = len(expected_returns)
    initial_weights = np.ones(n) / n

    def port_vol(w):
        return np.sqrt(np.dot(w.T, np.dot(cov_matrix, w)))

    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]
    bounds = tuple((0.0, 1.0) for _ in range(n))

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
    risk_free_rate: float,
    symbols: list[str],
    n_points: int = FRONTIER_POINTS,
) -> list[dict]:
    """
    Generate the efficient frontier by sweeping target returns from
    the minimum-variance portfolio return to the maximum individual asset return.

    Returns a list of dicts, each with: expected_return, volatility, weights.
    """
    n = len(expected_returns)

    # Find the min-volatility portfolio return as the lower bound
    min_vol_weights = optimize_min_volatility(expected_returns, cov_matrix)
    min_ret = portfolio_return(min_vol_weights, expected_returns)
    max_ret = float(np.max(expected_returns))

    # Ensure we have a valid range
    if max_ret <= min_ret:
        max_ret = min_ret + 0.01

    target_returns = np.linspace(min_ret, max_ret, n_points)
    frontier: list[dict] = []
    
    # Warm start: use min_vol_weights as the first guess
    current_guess = min_vol_weights.copy()

    for target in target_returns:
        constraints = [
            {"type": "eq", "fun": lambda w: np.sum(w) - 1.0},
            {"type": "eq", "fun": lambda w, t=target: np.dot(w, expected_returns) - t},
        ]
        bounds = tuple((0.0, 1.0) for _ in range(n))

        result = minimize(
            lambda w: np.sqrt(np.dot(w.T, np.dot(cov_matrix, w))),
            current_guess,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 1000, "ftol": 1e-9}, # slightly looser tolerance for speed
        )

        if result.success:
            current_guess = result.x # Warm start next iteration
            vol = portfolio_volatility(result.x, cov_matrix)
            ret = portfolio_return(result.x, expected_returns)
            frontier.append({
                "expected_return": round(ret, 4),
                "volatility": round(vol, 4),
                "weights": {
                    sym: round(float(w), 4)
                    for sym, w in zip(symbols, result.x)
                },
            })

    # Sort by volatility for a clean curve
    frontier.sort(key=lambda p: p["volatility"])

    return frontier
