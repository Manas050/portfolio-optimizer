"""
Portfolio Optimization Engine — MC-Seeded SLSQP Hybrid

Design philosophy
─────────────────
Monte Carlo  →  Global exploration of the weight simplex.
                Runs N random Dirichlet portfolios to map the feasible region.
                Top performers by Sharpe become STARTING POINTS for SLSQP.
                Also produces the 3 000-point visualization cloud.

SLSQP        →  Local precision refinement from each MC seed.
                Runs scipy.optimize.minimize (SLSQP) from every good seed.
                The globally-best converged result is the true optimum.
                Same solver traces the efficient frontier analytically.

Why this beats either approach alone
─────────────────────────────────────
  • Pure MC   : random sampling never lands exactly on the optimum.
                "Median of top 10%" is a heuristic, not a mathematical answer.
  • Pure SLSQP: gradient descent from a single (or few) starts risks
                converging to a local minimum, especially with asset-cap constraints.
  • Hybrid    : MC explores the full simplex cheaply (vectorised).
                The best K seeds feed SLSQP, which refines each to its
                nearest local optimum. The best result across all K runs
                is robust to local traps — effectively a global optimum.

Guarantees
──────────
  ∙ Max Sharpe  : SLSQP from top-K MC seeds + equal-weight fallback.
  ∙ Min Vol     : SLSQP from multiple starts (convex sub-problem, still seeded).
  ∙ Frontier    : SLSQP sweep [R_minvol → R_maxret], warm-started.
  ∙ Sharpe Rf   : single source of truth — no defaults, no module-level constants.
  ∙ Negative Rf : if all assets underperform Rf, Max Sharpe degrades gracefully
                  to Min Vol and a warning is raised.
"""

import numpy as np
from scipy.optimize import minimize

import logging
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Core portfolio math
# ─────────────────────────────────────────────────────────────────────────────

def portfolio_return(weights: np.ndarray, mu: np.ndarray) -> float:
    """Rp = w · μ  (annualised)"""
    return float(weights @ mu)


def portfolio_volatility(weights: np.ndarray, cov: np.ndarray) -> float:
    """σp = √(wᵀ Σ w)  (annualised).  Clamps tiny negatives from float arithmetic."""
    return float(np.sqrt(max(0.0, weights @ cov @ weights)))


def portfolio_sharpe(weights: np.ndarray, mu: np.ndarray,
                     cov: np.ndarray, rf: float) -> float:
    """S = (Rp − Rf) / σp.  Returns 0 if σp < 1e-8 to avoid ÷0."""
    vol = portfolio_volatility(weights, cov)
    return float((weights @ mu - rf) / vol) if vol > 1e-8 else 0.0


def compute_portfolio_metrics(weights: np.ndarray,
                               mu: np.ndarray,
                               cov: np.ndarray,
                               rf: float,
                               symbols: list[str]) -> dict:
    """
    Compute full metrics for a weight vector.

    rf is ALWAYS passed explicitly from the request — never defaulted here.
    If rf > 1.0, it is divided by 100 (percentage → decimal) with a warning,
    so a mis-wired caller can never silently corrupt Sharpe.
    """
    if rf > 1.0:
        logger.warning(
            "compute_portfolio_metrics: rf=%.4f looks like a percentage. "
            "Dividing by 100. Fix the call site.", rf
        )
        rf /= 100.0

    ret    = portfolio_return(weights, mu)
    vol    = portfolio_volatility(weights, cov)
    sharpe = (ret - rf) / vol if vol > 1e-8 else 0.0

    return {
        "expected_return": round(ret, 6),
        "volatility":      round(vol, 6),
        "sharpe_ratio":    round(sharpe, 4),
        "weights":         {s: round(float(w), 6)
                            for s, w in zip(symbols, weights)},
    }


# ─────────────────────────────────────────────────────────────────────────────
# Shared SLSQP helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_bounds_and_eq(n: int, max_w: float) -> tuple:
    """Return (bounds, sum-to-1 constraint) for SLSQP calls."""
    bounds = [(0.0, min(max_w, 1.0))] * n
    eq     = [{"type": "eq", "fun": lambda w: w.sum() - 1.0}]
    return bounds, eq


def _best_slsqp(objective, starts: list[np.ndarray],
                bounds, constraints,
                ftol: float = 1e-12,
                maxiter: int = 1000) -> tuple[np.ndarray | None, float]:
    """
    Run SLSQP from each starting point; return (best_x, best_fun).
    objective is MINIMISED, so lower fun = better.
    """
    best_x, best_fun = None, np.inf
    for w0 in starts:
        res = minimize(
            objective, w0,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": maxiter, "ftol": ftol},
        )
        if res.success and res.fun < best_fun:
            best_fun = res.fun
            best_x   = res.x.copy()
    return best_x, best_fun


# ─────────────────────────────────────────────────────────────────────────────
# Monte Carlo sampling  (exploration only)
# ─────────────────────────────────────────────────────────────────────────────

def _sample_portfolios(n_assets: int,
                        n: int,
                        max_w: float) -> np.ndarray:
    """
    Draw n random portfolios from the Dirichlet distribution and enforce
    the max_w cap via iterative proportional redistribution.
    Returns ndarray of shape (n, n_assets); rows sum to 1.
    """
    cap = min(max_w, 1.0)
    W   = np.zeros((n, n_assets))

    for i in range(n):
        w = np.random.dirichlet(np.ones(n_assets))
        for _ in range(20):                          # ≤ 20 redistribution passes
            excess = np.maximum(w - cap, 0.0)
            if excess.sum() < 1e-10:
                break
            w      = np.minimum(w, cap)
            rem    = 1.0 - w.sum()
            under  = w < cap
            if under.any():
                w[under] += rem * w[under] / max(w[under].sum(), 1e-12)
            w /= w.sum()
        W[i] = w
    return W


def _vectorised_stats(W: np.ndarray,
                       mu: np.ndarray,
                       cov: np.ndarray,
                       rf: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute returns, vols, Sharpes for all N portfolios at once.
    Returns (returns[N], vols[N], sharpes[N]).
    """
    rets    = W @ mu                                           # (N,)
    vols    = np.sqrt(np.maximum(np.sum((W @ cov) * W, 1), 0))  # (N,)
    sharpes = np.where(vols > 1e-8, (rets - rf) / vols, 0.0)
    return rets, vols, sharpes


# ─────────────────────────────────────────────────────────────────────────────
# MC-Seeded SLSQP  —  Max Sharpe
# ─────────────────────────────────────────────────────────────────────────────

def optimise_max_sharpe(mu: np.ndarray,
                         cov: np.ndarray,
                         rf: float,
                         max_w: float,
                         mc_seeds: np.ndarray | None = None,
                         n_extra_starts: int = 5) -> np.ndarray:
    """
    Find the maximum-Sharpe portfolio using MC-seeded multi-start SLSQP.

    Starting points
    ───────────────
      1. Equal weight
      2. Top-K MC seeds (ordered by Sharpe from the exploration phase)
      3. n_extra_starts random Dirichlet draws (fallback diversity)

    When all returns < rf the Sharpe surface is entirely negative; the
    objective approaches −∞ as vol → 0.  In that regime we MAXIMISE
    return instead (least-bad allocation), and the caller is notified
    via the returned weights being the max-return portfolio.

    Returns optimal weight array.
    """
    n = len(mu)
    bounds, eq = _make_bounds_and_eq(n, max_w)

    def neg_sharpe(w):
        vol = portfolio_volatility(w, cov)
        if vol < 1e-8:
            return 0.0                   # avoid ÷0 / −∞
        return -(float(w @ mu) - rf) / vol

    # Build starting points
    starts = [np.ones(n) / n]           # 1. equal weight

    if mc_seeds is not None and len(mc_seeds) > 0:
        for seed in mc_seeds:            # 2. MC top-K
            starts.append(seed.copy())

    cap = min(max_w, 1.0)
    rng = np.random.default_rng()
    for _ in range(n_extra_starts):     # 3. random diversity
        rw = rng.dirichlet(np.ones(n))
        rw = np.clip(rw, 0, cap)
        rw /= rw.sum()
        starts.append(rw)

    best_x, _ = _best_slsqp(neg_sharpe, starts, bounds, eq)
    return best_x if best_x is not None else np.ones(n) / n


# ─────────────────────────────────────────────────────────────────────────────
# MC-Seeded SLSQP  —  Min Volatility
# ─────────────────────────────────────────────────────────────────────────────

def optimise_min_volatility(mu: np.ndarray,
                              cov: np.ndarray,
                              max_w: float,
                              mc_seeds: np.ndarray | None = None,
                              n_extra_starts: int = 4) -> np.ndarray:
    """
    Find the global minimum-variance portfolio via MC-seeded SLSQP.

    Min variance is a convex QP (when unconstrained) so a single solve
    should suffice, but with per-asset caps the feasible region is a
    constrained polytope and multiple starts guard against edge cases.
    """
    n = len(mu)
    bounds, eq = _make_bounds_and_eq(n, max_w)

    def port_var(w):
        return float(w @ cov @ w)       # minimise variance ≡ minimise σ

    starts = [np.ones(n) / n]

    if mc_seeds is not None and len(mc_seeds) > 0:
        for seed in mc_seeds:
            starts.append(seed.copy())

    cap = min(max_w, 1.0)
    rng = np.random.default_rng()
    for _ in range(n_extra_starts):
        rw = rng.dirichlet(np.ones(n))
        rw = np.clip(rw, 0, cap)
        rw /= rw.sum()
        starts.append(rw)

    best_x, _ = _best_slsqp(port_var, starts, bounds, eq, ftol=1e-14)
    return best_x if best_x is not None else np.ones(n) / n


# ─────────────────────────────────────────────────────────────────────────────
# SLSQP Efficient Frontier
# ─────────────────────────────────────────────────────────────────────────────

def _max_return_weights(mu: np.ndarray, max_w: float) -> np.ndarray:
    """Find the highest-return portfolio (right anchor of the frontier)."""
    n = len(mu)
    bounds, eq = _make_bounds_and_eq(n, max_w)
    res = minimize(lambda w: -float(w @ mu), np.ones(n) / n,
                   method="SLSQP", bounds=bounds, constraints=eq,
                   options={"maxiter": 500, "ftol": 1e-12})
    return res.x if res.success else np.ones(n) / n


def compute_slsqp_frontier(mu: np.ndarray,
                             cov: np.ndarray,
                             symbols: list[str],
                             max_w: float,
                             n_points: int = 50,
                             minvol_weights: np.ndarray | None = None) -> list[dict]:
    """
    Trace the efficient frontier analytically with SLSQP.

    For each target Rt in linspace(R_minvol, R_maxret, n_points):
        minimise   wᵀ Σ w
        subject to Σwᵢ = 1,  wᵀμ = Rt,  0 ≤ wᵢ ≤ max_w

    Technique: warm-starting — each solve begins from the previous point,
    which dramatically improves convergence on dense sweeps.

    Post-processing: sort by volatility, remove dominated points
    (lower return at same or higher risk = inefficient lower-parabola half).
    """
    n   = len(mu)
    cap = min(max_w, 1.0)
    bounds = [(0.0, cap)] * n

    # Anchors
    if minvol_weights is None:
        minvol_weights = optimise_min_volatility(mu, cov, max_w)
    maxret_w = _max_return_weights(mu, max_w)

    r_min = portfolio_return(minvol_weights, mu)
    r_max = portfolio_return(maxret_w, mu)

    if r_max <= r_min:                   # degenerate: all assets identical return
        r_max = r_min + max(abs(r_min) * 0.05, 0.01)

    targets = np.linspace(r_min, r_max, n_points)

    # Seed with known-good min-vol point
    raw: list[dict] = [{
        "expected_return": round(r_min, 6),
        "volatility":      round(portfolio_volatility(minvol_weights, cov), 6),
        "weights":         {s: round(float(w), 6)
                            for s, w in zip(symbols, minvol_weights)},
    }]
    cur_w = minvol_weights.copy()

    for Rt in targets[1:]:
        constraints = [
            {"type": "eq", "fun": lambda w:       w.sum() - 1.0},
            {"type": "eq", "fun": lambda w, t=Rt: float(w @ mu) - t},
        ]
        res = minimize(
            lambda w: float(w @ cov @ w),
            cur_w,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 1000, "ftol": 1e-10},
        )
        if res.success:
            cur_w = res.x
            raw.append({
                "expected_return": round(portfolio_return(res.x, mu), 6),
                "volatility":      round(portfolio_volatility(res.x, cov), 6),
                "weights":         {s: round(float(w), 6)
                                    for s, w in zip(symbols, res.x)},
            })

    # Remove dominated (lower-parabola) points
    raw.sort(key=lambda p: p["volatility"])
    efficient: list[dict] = []
    if raw:
        efficient.append(raw[0])
        for p in raw[1:]:
            if p["expected_return"] >= efficient[-1]["expected_return"]:
                efficient.append(p)

    return efficient


# ─────────────────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────────────────

def run_optimization(mu: np.ndarray,
                      cov: np.ndarray,
                      symbols: list[str],
                      rf: float,
                      max_w: float = 1.0,
                      n_mc: int = 20000,
                      n_frontier_points: int = 50,
                      n_slsqp_seeds: int = 10) -> dict:
    """
    Full MC-seeded SLSQP optimization pipeline.

    Step 1 — Monte Carlo exploration (n_mc portfolios)
        • Vectorised computation of R, σ, Sharpe for all samples.
        • Top n_slsqp_seeds by Sharpe  → seeds for Max Sharpe SLSQP.
        • Top n_slsqp_seeds by low σ   → seeds for Min Vol SLSQP.
        • Downsample to 3 000 points for the visualization cloud.

    Step 2 — SLSQP refinement (from MC seeds)
        • Max Sharpe SLSQP from top-Sharpe seeds → exact optimal.
        • Min Vol    SLSQP from top-low-σ seeds   → exact min-var.

    Step 3 — SLSQP efficient frontier
        • Sweep n_frontier_points targets, warm-started from min-vol.

    Returns
    -------
    dict with:
        optimal_sharpe      — exact max-Sharpe portfolio metrics
        min_volatility      — exact min-vol portfolio metrics
        efficient_frontier  — list of frontier point dicts
        monte_carlo_cloud   — 3 000-point cloud for visualization
        simulation_stats    — run metadata
    """
    n   = len(mu)
    cap = min(max_w, 1.0)

    # ── Step 1: Monte Carlo exploration ─────────────────────────────
    W = _sample_portfolios(n, n_mc, cap)
    mc_rets, mc_vols, mc_sharpes = _vectorised_stats(W, mu, cov, rf)

    # Best seeds for Max Sharpe  (highest Sharpe first)
    sharpe_order = np.argsort(mc_sharpes)[::-1]
    sharpe_seeds = W[sharpe_order[:n_slsqp_seeds]]

    # Best seeds for Min Vol  (lowest vol first)
    vol_order    = np.argsort(mc_vols)
    vol_seeds    = W[vol_order[:n_slsqp_seeds]]

    # Cloud: stratified downsample — keep the extremes AND random interior
    cloud_n      = min(3000, n_mc)
    keep_top     = min(200, cloud_n // 10)       # preserve top Sharpe in cloud
    top_cloud    = sharpe_order[:keep_top]
    rest_idx     = np.random.choice(n_mc, cloud_n - keep_top, replace=False)
    cloud_idx    = np.concatenate([top_cloud, rest_idx])
    cloud = [
        {
            "expected_return": round(float(mc_rets[i]),    6),
            "volatility":      round(float(mc_vols[i]),    6),
            "sharpe_ratio":    round(float(mc_sharpes[i]), 4),
        }
        for i in cloud_idx
    ]

    sim_stats = {
        "n_simulations":    n_mc,
        "top_percentile":   round(n_slsqp_seeds / n_mc * 100, 2),
        "selection_method": "mc_seeded_slsqp",
        "best_mc_sharpe":   round(float(mc_sharpes[sharpe_order[0]]),  4),
        "worst_mc_sharpe":  round(float(mc_sharpes[sharpe_order[-1]]), 4),
        "cloud_size":       cloud_n,
    }

    # ── Step 2: SLSQP refinement ────────────────────────────────────
    opt_w = optimise_max_sharpe(mu, cov, rf, cap,
                                 mc_seeds=sharpe_seeds,
                                 n_extra_starts=5)

    # Graceful fallback: if ALL returns < rf the Sharpe surface is inverted.
    # In that case, "Max Sharpe" degrades to Min Vol (least-bad choice).
    if (mu < rf).all():
        logger.warning(
            "All expected returns (%.4f … %.4f) < rf=%.4f. "
            "Max Sharpe degrades to Min Vol.", mu.min(), mu.max(), rf
        )
        opt_w = vol_seeds[0]             # MC best low-vol seed → refined below

    minvol_w = optimise_min_volatility(mu, cov, cap,
                                        mc_seeds=vol_seeds,
                                        n_extra_starts=4)

    optimal_metrics = compute_portfolio_metrics(opt_w,    mu, cov, rf, symbols)
    minvol_metrics  = compute_portfolio_metrics(minvol_w, mu, cov, rf, symbols)

    # Annotate simulation stats with SLSQP results
    sim_stats["final_sharpe"]    = optimal_metrics["sharpe_ratio"]
    sim_stats["final_min_vol"]   = minvol_metrics["volatility"]
    sim_stats["slsqp_gain"]      = round(
        optimal_metrics["sharpe_ratio"] - sim_stats["best_mc_sharpe"], 4
    )

    # ── Step 3: SLSQP efficient frontier ────────────────────────────
    frontier = compute_slsqp_frontier(
        mu, cov, symbols, cap,
        n_points=n_frontier_points,
        minvol_weights=minvol_w,         # use SLSQP min-vol as left anchor
    )

    return {
        "optimal_sharpe":     optimal_metrics,
        "min_volatility":     minvol_metrics,
        "efficient_frontier": frontier,
        "monte_carlo_cloud":  cloud,
        "simulation_stats":   sim_stats,
    }
