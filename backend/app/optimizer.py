"""
Hybrid Portfolio Optimization Engine.

Selection  → Monte Carlo simulation (N random portfolios via Dirichlet weights).
             The MEDIAN of the top-10% by Sharpe is chosen as the robust optimal.
             The lowest-volatility simulation is the min-vol recommendation.

Frontier   → SLSQP (scipy.optimize.minimize).
             Analytical sweep from R_min to R_max in 50 steps, each step
             minimising σ subject to w·μ = target. This produces the exact,
             smooth parabolic frontier — far more precise than binning MC points.
"""

import numpy as np
from scipy.optimize import minimize

from app.config import TRADING_DAYS_PER_YEAR


# ─────────────────────────────────────────────────────────────────────
# Core Portfolio Math
# ─────────────────────────────────────────────────────────────────────

def portfolio_return(weights: np.ndarray, expected_returns: np.ndarray) -> float:
    """Annualised expected portfolio return: Rp = w · μ"""
    return float(np.dot(weights, expected_returns))


def portfolio_volatility(weights: np.ndarray, cov_matrix: np.ndarray) -> float:
    """Annualised portfolio volatility: σp = √(wᵀ Σ w)"""
    variance = np.dot(weights.T, np.dot(cov_matrix, weights))
    return float(np.sqrt(max(0.0, variance)))


def portfolio_sharpe(
    weights: np.ndarray,
    expected_returns: np.ndarray,
    cov_matrix: np.ndarray,
    risk_free_rate: float,
) -> float:
    """Sharpe ratio = (Rp - Rf) / σp."""
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
    """
    Full metrics dict for a weight vector.

    risk_free_rate MUST be a decimal (e.g. 0.068 for 6.8%).
    Values > 1.0 are clamped with a warning — they indicate a
    percentage was passed instead of a decimal, which would produce
    a wildly incorrect (and negative) Sharpe ratio.
    """
    # Guard: never let a raw-percentage Rf corrupt Sharpe
    if risk_free_rate > 1.0:
        import warnings as _w
        _w.warn(
            f"compute_portfolio_metrics received risk_free_rate={risk_free_rate} (>1.0). "
            "Expected a decimal (e.g. 0.068). Dividing by 100 automatically.",
            RuntimeWarning,
            stacklevel=2,
        )
        risk_free_rate = risk_free_rate / 100.0

    ret    = portfolio_return(weights, expected_returns)
    vol    = portfolio_volatility(weights, cov_matrix)
    sharpe = (ret - risk_free_rate) / vol if vol > 1e-8 else 0.0
    return {
        "expected_return": round(ret, 6),
        "volatility":      round(vol, 6),
        "sharpe_ratio":    round(sharpe, 4),
        "weights":         {sym: round(float(w), 6) for sym, w in zip(symbols, weights)},
    }


# ─────────────────────────────────────────────────────────────────────
# Monte Carlo Engine  (selection only)
# ─────────────────────────────────────────────────────────────────────

def _generate_random_weights(
    n_assets: int,
    n_portfolios: int,
    max_weight: float = 1.0,
) -> np.ndarray:
    """
    Generate (n_portfolios, n_assets) random weight matrix.
    Uses Dirichlet draws and enforces the max_weight cap via iterative
    proportional redistribution.
    """
    capped = min(max_weight, 1.0)
    all_w = np.zeros((n_portfolios, n_assets))

    for i in range(n_portfolios):
        w = np.random.dirichlet(np.ones(n_assets))
        for _ in range(15):
            if np.all(w <= capped + 1e-10):
                break
            w = np.minimum(w, capped)
            rem = 1.0 - w.sum()
            mask = w < capped
            if mask.any():
                w[mask] += rem * (w[mask] / max(w[mask].sum(), 1e-10))
            w /= w.sum()
        all_w[i] = w

    return all_w


def run_monte_carlo_simulation(
    expected_returns: np.ndarray,
    cov_matrix: np.ndarray,
    symbols: list[str],
    risk_free_rate: float,
    n_simulations: int = 50000,
    max_weight: float = 1.0,
    n_frontier_points: int = 50,
) -> dict:
    """
    Full hybrid optimization pipeline.

    Stage 1 — Monte Carlo (selection):
        • Generate n_simulations random portfolios.
        • Vectorised computation of return, σ, Sharpe for all.
        • Optimal  = median of top-10% by Sharpe  (robust, not overfit).
        • Min-vol  = lowest σ across all simulations.

    Stage 2 — SLSQP (frontier):
        • Solve min σ s.t. w·μ = target, Σw=1, 0≤w≤max_weight for
          n_frontier_points target returns spanning [R_minvol, R_maxret].
        • Warm-starts each solve from the previous frontier point.
        • Filters the lower (inefficient) half of the parabola.

    Returns
    -------
    dict with keys:
        optimal_sharpe, min_volatility  – PortfolioMetrics dicts
        efficient_frontier              – list of frontier point dicts
        monte_carlo_cloud               – 3 000-point downsample for chart
        simulation_stats                – run metadata
    """
    n = len(expected_returns)
    capped = min(max_weight, 1.0)

    # ── Stage 1: Monte Carlo ─────────────────────────────────────────

    all_w = _generate_random_weights(n, n_simulations, capped)

    # Vectorised portfolio stats
    mc_returns = all_w @ expected_returns                          # (N,)
    cov_prod   = all_w @ cov_matrix                               # (N, n)
    variances  = np.maximum(np.sum(cov_prod * all_w, axis=1), 0)  # (N,)
    mc_vols    = np.sqrt(variances)                                # (N,)
    mc_sharpes = np.where(
        mc_vols > 1e-8,
        (mc_returns - risk_free_rate) / mc_vols,
        0.0,
    )

    # Optimal: median of top-10% by Sharpe
    top_k = max(1, n_simulations // 10)
    top_idx = np.argsort(mc_sharpes)[::-1][:top_k]
    median_idx = top_idx[len(top_idx) // 2]
    optimal_weights = all_w[median_idx]
    optimal_metrics = compute_portfolio_metrics(
        optimal_weights, expected_returns, cov_matrix, risk_free_rate, symbols
    )

    # Min-vol: lowest σ in simulation
    minvol_idx     = np.argmin(mc_vols)
    minvol_weights = all_w[minvol_idx]
    min_vol_metrics = compute_portfolio_metrics(
        minvol_weights, expected_returns, cov_matrix, risk_free_rate, symbols
    )

    # Cloud: downsample for frontend
    cloud_n = min(3000, n_simulations)
    cloud_idx = np.random.choice(n_simulations, cloud_n, replace=False)
    cloud = [
        {
            "expected_return": round(float(mc_returns[i]), 6),
            "volatility":      round(float(mc_vols[i]), 6),
            "sharpe_ratio":    round(float(mc_sharpes[i]), 4),
        }
        for i in cloud_idx
    ]

    stats = {
        "n_simulations":    n_simulations,
        "top_percentile":   10,
        "selection_method": "median_of_top_10pct",
        "best_sharpe":      round(float(mc_sharpes[top_idx[0]]), 4),
        "median_sharpe":    round(float(mc_sharpes[median_idx]), 4),
        "worst_sharpe":     round(float(mc_sharpes[np.argsort(mc_sharpes)[0]]), 4),
        "cloud_size":       cloud_n,
    }

    # ── Stage 2: SLSQP Efficient Frontier ───────────────────────────

    frontier = compute_slsqp_frontier(
        expected_returns=expected_returns,
        cov_matrix=cov_matrix,
        symbols=symbols,
        max_weight=capped,
        n_points=n_frontier_points,
        # Use MC min-vol weights as the warm-start seed — they're already
        # a good low-risk starting point in the feasible region.
        seed_weights=minvol_weights,
    )

    return {
        "optimal_sharpe":    optimal_metrics,
        "min_volatility":    min_vol_metrics,
        "efficient_frontier": frontier,
        "monte_carlo_cloud": cloud,
        "simulation_stats":  stats,
    }


# ─────────────────────────────────────────────────────────────────────
# SLSQP Efficient Frontier
# ─────────────────────────────────────────────────────────────────────

def _slsqp_min_vol_weights(
    expected_returns: np.ndarray,
    cov_matrix: np.ndarray,
    max_weight: float,
) -> np.ndarray:
    """
    SLSQP: find the global minimum-variance portfolio.
    Used to anchor the left end of the frontier.
    """
    n = len(expected_returns)
    bounds = [(0.0, max_weight)] * n
    constraints = [{"type": "eq", "fun": lambda w: w.sum() - 1.0}]

    def port_var(w):
        return float(w @ cov_matrix @ w)

    best = None
    best_val = np.inf

    # Multiple starts: equal-weight + 3 Dirichlet draws
    starts = [np.ones(n) / n]
    for _ in range(3):
        rw = np.random.dirichlet(np.ones(n))
        rw = np.clip(rw, 0.0, max_weight)
        rw /= rw.sum()
        starts.append(rw)

    for w0 in starts:
        res = minimize(port_var, w0, method="SLSQP",
                       bounds=bounds, constraints=constraints,
                       options={"maxiter": 1000, "ftol": 1e-12})
        if res.success and res.fun < best_val:
            best_val = res.fun
            best = res.x

    return best if best is not None else np.ones(n) / n


def _slsqp_max_return_weights(
    expected_returns: np.ndarray,
    max_weight: float,
) -> np.ndarray:
    """
    SLSQP: find the maximum-return portfolio (right end of frontier).
    With max_weight < 1 this is not simply 100 % in the best asset.
    """
    n = len(expected_returns)
    bounds = [(0.0, max_weight)] * n
    constraints = [{"type": "eq", "fun": lambda w: w.sum() - 1.0}]
    w0 = np.ones(n) / n

    res = minimize(lambda w: -float(w @ expected_returns), w0,
                   method="SLSQP", bounds=bounds, constraints=constraints,
                   options={"maxiter": 500, "ftol": 1e-12})
    return res.x if res.success else w0


def compute_slsqp_frontier(
    expected_returns: np.ndarray,
    cov_matrix: np.ndarray,
    symbols: list[str],
    max_weight: float = 1.0,
    n_points: int = 50,
    seed_weights: np.ndarray | None = None,
) -> list[dict]:
    """
    Trace the efficient frontier analytically using SLSQP.

    For each target return Rt in linspace(R_minvol, R_maxret, n_points):
        minimise   wᵀ Σ w
        subject to Σwᵢ = 1
                   wᵀ μ = Rt
                   0 ≤ wᵢ ≤ max_weight

    Uses warm-starting: each solve begins from the previous solution,
    which dramatically improves convergence on dense sweeps.

    After collecting all points the function filters the lower (inefficient)
    half of the mean-variance parabola: only points where return increases
    monotonically with volatility are retained.
    """
    n = len(expected_returns)
    capped = min(max_weight, 1.0)
    bounds = [(0.0, capped)] * n

    # ── Anchor points ────────────────────────────────────────────────
    minvol_w = _slsqp_min_vol_weights(expected_returns, cov_matrix, capped)
    maxret_w = _slsqp_max_return_weights(expected_returns, capped)

    r_min = portfolio_return(minvol_w, expected_returns)
    r_max = portfolio_return(maxret_w, expected_returns)

    if r_max <= r_min:
        r_max = r_min + max(abs(r_min) * 0.1, 0.01)

    targets = np.linspace(r_min, r_max, n_points)

    # ── Sweep ────────────────────────────────────────────────────────
    # Always include the SLSQP min-vol point as the first frontier entry
    raw: list[dict] = [{
        "expected_return": round(float(r_min), 6),
        "volatility":      round(portfolio_volatility(minvol_w, cov_matrix), 6),
        "weights":         {sym: round(float(w), 6) for sym, w in zip(symbols, minvol_w)},
    }]

    # Warm-start from seed (MC min-vol) if provided, else SLSQP min-vol
    current_w = seed_weights.copy() if seed_weights is not None else minvol_w.copy()

    for target in targets[1:]:
        constraints = [
            {"type": "eq", "fun": lambda w:      w.sum() - 1.0},
            {"type": "eq", "fun": lambda w, t=target: float(w @ expected_returns) - t},
        ]

        res = minimize(
            lambda w: float(w @ cov_matrix @ w),   # minimise variance (≡ min σ)
            current_w,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 1000, "ftol": 1e-10},
        )

        if res.success:
            current_w = res.x          # warm-start for next step
            ret = portfolio_return(res.x, expected_returns)
            vol = portfolio_volatility(res.x, cov_matrix)
            raw.append({
                "expected_return": round(ret, 6),
                "volatility":      round(vol, 6),
                "weights":         {sym: round(float(w), 6) for sym, w in zip(symbols, res.x)},
            })

    # ── Filter inefficient (lower-parabola) points ──────────────────
    raw.sort(key=lambda p: p["volatility"])

    efficient: list[dict] = []
    if raw:
        efficient.append(raw[0])
        for p in raw[1:]:
            if p["expected_return"] >= efficient[-1]["expected_return"]:
                efficient.append(p)

    return efficient
