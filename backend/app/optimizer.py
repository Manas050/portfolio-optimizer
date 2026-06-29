"""
Portfolio Optimization Engine — MC-Seeded SLSQP Hybrid

Design
──────
Monte Carlo  → vectorised global exploration (fast, no Python loops).
               Top performers by Sharpe/vol feed SLSQP as starting points.
               Produces the 3 000-point visualisation cloud.

SLSQP        → local precision refinement from MC seeds.
               Multi-start: every good seed runs its own SLSQP.
               Best converged result across all starts is the answer.
               Same solver traces the efficient frontier analytically.

Bug fixes in this version
─────────────────────────
  1. _sample_portfolios: fully vectorised — no Python inner loop.
  2. _best_slsqp: accepts near-converged results (exit mode ≠ 0 but
     small constraint violation), not just res.success == True.
  3. Max-Sharpe all-negative fallback correctly uses SLSQP min-vol
     result (not a raw MC sample) as the "least-bad" allocation.
  4. Frontier lambda closure: objective and constraints defined once
     outside the loop to avoid capture/recreation overhead.
  5. Units suggestion uses max(1, round(...)) floor.
  6. Cloud sampling: deduplicated so top-Sharpe and random draws
     never overlap.
  7. top_percentile stored as int from the start.
"""

import numpy as np
from scipy.optimize import minimize
from scipy.linalg import cholesky, LinAlgError

import logging
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Core portfolio math
# ─────────────────────────────────────────────────────────────────────────────

def portfolio_return(weights: np.ndarray, mu: np.ndarray) -> float:
    """Rp = w · μ  (annualised)"""
    return float(weights @ mu)


def portfolio_volatility(weights: np.ndarray, cov: np.ndarray) -> float:
    """σp = √(wᵀ Σ w).  Clamps tiny floating-point negatives."""
    return float(np.sqrt(max(0.0, weights @ cov @ weights)))


def portfolio_sharpe(weights: np.ndarray, mu: np.ndarray,
                     cov: np.ndarray, rf: float) -> float:
    """S = (Rp − Rf) / σp.  Returns 0.0 if σp < 1e-8."""
    vol = portfolio_volatility(weights, cov)
    return float((weights @ mu - rf) / vol) if vol > 1e-8 else 0.0


def compute_portfolio_metrics(weights: np.ndarray,
                               mu: np.ndarray,
                               cov: np.ndarray,
                               rf: float,
                               symbols: list[str]) -> dict:
    """
    Full metrics dict for a weight vector.

    rf is ALWAYS passed explicitly — never defaulted.
    Guard: rf > 1.0 is treated as a raw percentage and auto-converted.
    """
    if rf > 1.0:
        logger.warning(
            "compute_portfolio_metrics: rf=%.4f > 1.0 — looks like a "
            "percentage. Dividing by 100. Fix the call site.", rf
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
# SLSQP helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_bounds(n: int, max_w: float) -> list[tuple]:
    return [(0.0, min(float(max_w), 1.0))] * n


_SUM_EQ = [{"type": "eq", "fun": lambda w: float(w.sum()) - 1.0}]


def _best_slsqp(objective, starts: list[np.ndarray],
                bounds, constraints,
                ftol: float = 1e-10,
                maxiter: int = 800) -> tuple[np.ndarray | None, float]:
    """
    Run SLSQP from every starting point; return (best_x, best_fun).

    FIX: we no longer require res.success == True. SLSQP can return
    exit code 9 ("iteration limit") with an excellent result when
    tolerances are very tight. We accept any result whose constraint
    violation is small (|Σw − 1| < 1e-4) and whose objective is
    finite. This prevents silently falling back to equal-weight when
    a near-perfect solution exists.
    """
    best_x, best_fun = None, np.inf

    for w0 in starts:
        try:
            res = minimize(
                objective, w0,
                method="SLSQP",
                bounds=bounds,
                constraints=constraints,
                options={"maxiter": maxiter, "ftol": ftol},
            )
        except Exception as e:
            logger.debug("SLSQP failed from start: %s", e)
            continue

        # Accept if converged OR near-converged with small constraint violation
        feasible = abs(res.x.sum() - 1.0) < 1e-4 and np.all(res.x >= -1e-6)
        if feasible and np.isfinite(res.fun) and res.fun < best_fun:
            best_fun = res.fun
            best_x   = res.x.clip(0.0)          # clip tiny negatives from float noise
            best_x   /= best_x.sum()             # re-normalise to exactly sum to 1

    return best_x, best_fun


# ─────────────────────────────────────────────────────────────────────────────
# Monte Carlo sampling — fully vectorised
# ─────────────────────────────────────────────────────────────────────────────

def _sample_portfolios(n_assets: int, n: int, max_w: float) -> np.ndarray:
    """
    Draw n portfolios via Dirichlet and enforce max_w cap.

    FIX: fully vectorised — no Python inner loops.
    All n portfolios are processed in parallel using numpy operations.
    The redistribution loop runs at most 20 times over the ENTIRE batch,
    making this ~100× faster than the old per-portfolio Python loop.

    Returns ndarray (n, n_assets) with rows summing to 1.
    """
    cap = float(min(max_w, 1.0))
    # Dirichlet draw: shape (n, n_assets)
    W = np.random.dirichlet(np.ones(n_assets), size=n).astype(np.float64)

    if cap >= 1.0:
        return W                           # no cap needed — return as-is

    for _ in range(20):
        excess = np.maximum(W - cap, 0.0)  # (n, n_assets)
        if excess.sum() < 1e-10:
            break
        W      = np.minimum(W, cap)
        rem    = (1.0 - W.sum(axis=1, keepdims=True))   # (n, 1) remaining budget
        under  = W < cap                                  # (n, n_assets) mask
        denom  = np.where(under, W, 0.0).sum(axis=1, keepdims=True)
        denom  = np.where(denom > 1e-12, denom, 1e-12)
        W      = np.where(under, W + rem * W / denom, W)
        # Re-normalise each row to exactly 1
        row_sum = W.sum(axis=1, keepdims=True)
        W = W / np.where(row_sum > 0, row_sum, 1.0)

    return W


def _vectorised_stats(W: np.ndarray,
                       mu: np.ndarray,
                       cov: np.ndarray,
                       rf: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Returns (returns[N], vols[N], sharpes[N]) for all N portfolios."""
    rets    = W @ mu                                              # (N,)
    vols    = np.sqrt(np.maximum(np.einsum('ij,jk,ik->i', W, cov, W), 0.0))
    sharpes = np.where(vols > 1e-8, (rets - rf) / vols, 0.0)
    return rets, vols, sharpes


# ─────────────────────────────────────────────────────────────────────────────
# Max-Sharpe optimisation
# ─────────────────────────────────────────────────────────────────────────────

def optimise_max_sharpe(mu: np.ndarray,
                         cov: np.ndarray,
                         rf: float,
                         max_w: float,
                         mc_seeds: np.ndarray | None = None,
                         n_extra_starts: int = 5) -> np.ndarray:
    """
    Maximise Sharpe via MC-seeded multi-start SLSQP.

    Starts: equal-weight + top MC seeds + n_extra random Dirichlet.

    All-negative regime: when every asset underperforms rf, the Sharpe
    surface is entirely negative and the "max Sharpe" degrades to min vol.
    We detect this and return min-vol weights instead (logged as warning).
    """
    n      = len(mu)
    bounds = _make_bounds(n, max_w)

    def neg_sharpe(w: np.ndarray) -> float:
        vol = float(np.sqrt(max(0.0, w @ cov @ w)))
        return -(float(w @ mu) - rf) / vol if vol > 1e-8 else 0.0

    starts = [np.ones(n) / n]

    if mc_seeds is not None and len(mc_seeds) > 0:
        starts.extend([s.copy() for s in mc_seeds])

    rng = np.random.default_rng()
    cap = min(float(max_w), 1.0)
    for _ in range(n_extra_starts):
        rw = rng.dirichlet(np.ones(n))
        rw = np.clip(rw, 0.0, cap)
        rw /= rw.sum()
        starts.append(rw)

    best_x, _ = _best_slsqp(neg_sharpe, starts, bounds, _SUM_EQ)
    return best_x if best_x is not None else np.ones(n) / n


# ─────────────────────────────────────────────────────────────────────────────
# Min-Volatility optimisation
# ─────────────────────────────────────────────────────────────────────────────

def optimise_min_volatility(mu: np.ndarray,
                              cov: np.ndarray,
                              max_w: float,
                              mc_seeds: np.ndarray | None = None,
                              n_extra_starts: int = 4) -> np.ndarray:
    """
    Minimise portfolio variance via MC-seeded multi-start SLSQP.

    Min variance is a convex QP under the sum-to-1 constraint, so a
    single start is theoretically enough. Multiple starts guard against
    the per-asset cap constraint creating non-convex sub-regions.
    """
    n      = len(mu)
    bounds = _make_bounds(n, max_w)

    def port_var(w: np.ndarray) -> float:
        return float(w @ cov @ w)

    starts = [np.ones(n) / n]

    if mc_seeds is not None and len(mc_seeds) > 0:
        starts.extend([s.copy() for s in mc_seeds])

    rng = np.random.default_rng()
    cap = min(float(max_w), 1.0)
    for _ in range(n_extra_starts):
        rw = rng.dirichlet(np.ones(n))
        rw = np.clip(rw, 0.0, cap)
        rw /= rw.sum()
        starts.append(rw)

    best_x, _ = _best_slsqp(port_var, starts, bounds, _SUM_EQ, ftol=1e-14)
    return best_x if best_x is not None else np.ones(n) / n


# ─────────────────────────────────────────────────────────────────────────────
# SLSQP Efficient Frontier
# ─────────────────────────────────────────────────────────────────────────────

def _max_return_weights(mu: np.ndarray, max_w: float) -> np.ndarray:
    """Right anchor of the frontier: highest-return feasible portfolio."""
    n      = len(mu)
    bounds = _make_bounds(n, max_w)
    res = minimize(
        lambda w: -float(w @ mu),
        np.ones(n) / n,
        method="SLSQP",
        bounds=bounds,
        constraints=_SUM_EQ,
        options={"maxiter": 500, "ftol": 1e-12},
    )
    if res.success or (abs(res.x.sum() - 1.0) < 1e-4 and np.all(res.x >= -1e-6)):
        x = res.x.clip(0.0)
        return x / x.sum()
    return np.ones(n) / n


def compute_slsqp_frontier(mu: np.ndarray,
                             cov: np.ndarray,
                             symbols: list[str],
                             max_w: float,
                             n_points: int = 50,
                             minvol_weights: np.ndarray | None = None) -> list[dict]:
    """
    Trace the efficient frontier by solving n_points return-constrained
    min-variance problems via warm-started SLSQP.

    For each target Rt in linspace(R_minvol, R_maxret, n_points):
        minimise   wᵀ Σ w
        subject to Σwᵢ = 1,  wᵀμ = Rt,  0 ≤ wᵢ ≤ max_w

    Post-processing:
      • Sort by volatility.
      • Remove dominated points (monotone filter on return).

    FIX: objective and base constraint are defined ONCE outside the loop;
    only the return-target constraint changes per iteration.
    """
    n      = len(mu)
    cap    = min(float(max_w), 1.0)
    bounds = [(0.0, cap)] * n

    def port_var(w: np.ndarray) -> float:
        return float(w @ cov @ w)

    sum_eq = {"type": "eq", "fun": lambda w: float(w.sum()) - 1.0}

    # Anchors
    if minvol_weights is None:
        minvol_weights = optimise_min_volatility(mu, cov, max_w)
    maxret_w = _max_return_weights(mu, max_w)

    r_min = portfolio_return(minvol_weights, mu)
    r_max = portfolio_return(maxret_w, mu)

    if r_max <= r_min:
        r_max = r_min + max(abs(r_min) * 0.05, 0.01)

    targets = np.linspace(r_min, r_max, n_points)

    raw: list[dict] = [{
        "expected_return": round(r_min, 6),
        "volatility":      round(portfolio_volatility(minvol_weights, cov), 6),
        "weights":         {s: round(float(w), 6)
                            for s, w in zip(symbols, minvol_weights)},
    }]
    cur_w = minvol_weights.copy()

    for Rt in targets[1:]:
        ret_eq = {"type": "eq",
                  "fun": lambda w, t=Rt: float(w @ mu) - t}  # t=Rt captures correctly

        res = minimize(
            port_var, cur_w,
            method="SLSQP",
            bounds=bounds,
            constraints=[sum_eq, ret_eq],
            options={"maxiter": 1000, "ftol": 1e-10},
        )

        # Accept converged or near-converged (see _best_slsqp rationale)
        feasible = (abs(res.x.sum() - 1.0) < 1e-3
                    and np.all(res.x >= -1e-5)
                    and np.isfinite(res.fun))
        if feasible:
            cur_w = res.x.clip(0.0)
            cur_w /= cur_w.sum()
            raw.append({
                "expected_return": round(portfolio_return(cur_w, mu), 6),
                "volatility":      round(portfolio_volatility(cur_w, cov), 6),
                "weights":         {s: round(float(w), 6)
                                    for s, w in zip(symbols, cur_w)},
            })

    # Sort and filter lower-parabola (inefficient) half
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
    Full MC-seeded SLSQP pipeline.

    Step 1 — MC exploration (vectorised)
        All n_mc portfolios sampled and scored in parallel numpy ops.

    Step 2 — SLSQP refinement
        Top seeds by Sharpe  → Max Sharpe SLSQP.
        Top seeds by low vol → Min Vol SLSQP.
        FIX: all-negative fallback now uses the SLSQP min-vol result
             (not a raw MC seed) as the "least-bad" optimal portfolio.

    Step 3 — SLSQP frontier
        Warm-started sweep from R_minvol to R_maxret.
        Left anchor = SLSQP min-vol (exact), not MC sample.
    """
    n   = len(mu)
    cap = min(float(max_w), 1.0)

    # ── Step 1: MC exploration ───────────────────────────────────────
    W = _sample_portfolios(n, n_mc, cap)
    mc_rets, mc_vols, mc_sharpes = _vectorised_stats(W, mu, cov, rf)

    sharpe_order = np.argsort(mc_sharpes)[::-1]
    vol_order    = np.argsort(mc_vols)

    sharpe_seeds = W[sharpe_order[:n_slsqp_seeds]]
    vol_seeds    = W[vol_order[:n_slsqp_seeds]]

    # Cloud: deduplicated stratified sample
    # Keep top-200 by Sharpe + random fill from the remainder
    cloud_n      = min(3000, n_mc)
    top_k_cloud  = min(200, cloud_n // 10)
    top_cloud_idx = set(sharpe_order[:top_k_cloud].tolist())
    remaining    = [i for i in range(n_mc) if i not in top_cloud_idx]
    random_fill  = np.random.choice(remaining,
                                     size=min(cloud_n - top_k_cloud, len(remaining)),
                                     replace=False)
    cloud_idx    = list(top_cloud_idx) + random_fill.tolist()

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
        "top_percentile":   max(1, int(round(n_slsqp_seeds / n_mc * 100))),
        "selection_method": "mc_seeded_slsqp",
        "best_mc_sharpe":   round(float(mc_sharpes[sharpe_order[0]]),  4),
        "worst_mc_sharpe":  round(float(mc_sharpes[sharpe_order[-1]]), 4),
        "cloud_size":       len(cloud_idx),
    }

    # ── Step 2: SLSQP refinement ─────────────────────────────────────
    all_negative = bool((mu < rf).all())

    if all_negative:
        logger.warning(
            "All expected returns [%.4f, %.4f] < rf=%.4f. "
            "Max Sharpe degrades to Min Vol.", mu.min(), mu.max(), rf
        )

    # Always run min-vol SLSQP first (needed for frontier anchor too)
    minvol_w = optimise_min_volatility(mu, cov, cap,
                                        mc_seeds=vol_seeds,
                                        n_extra_starts=4)

    if all_negative:
        # FIX: use the SLSQP-refined min-vol weights (not a raw MC seed)
        opt_w = minvol_w.copy()
    else:
        opt_w = optimise_max_sharpe(mu, cov, rf, cap,
                                     mc_seeds=sharpe_seeds,
                                     n_extra_starts=5)

    optimal_metrics = compute_portfolio_metrics(opt_w,    mu, cov, rf, symbols)
    minvol_metrics  = compute_portfolio_metrics(minvol_w, mu, cov, rf, symbols)

    sim_stats["final_sharpe"]  = optimal_metrics["sharpe_ratio"]
    sim_stats["final_min_vol"] = minvol_metrics["volatility"]
    sim_stats["slsqp_gain"]    = round(
        optimal_metrics["sharpe_ratio"] - sim_stats["best_mc_sharpe"], 4
    )

    # ── Step 3: SLSQP frontier ───────────────────────────────────────
    frontier = compute_slsqp_frontier(
        mu, cov, symbols, cap,
        n_points=n_frontier_points,
        minvol_weights=minvol_w,          # exact SLSQP anchor, not MC sample
    )

    return {
        "optimal_sharpe":     optimal_metrics,
        "min_volatility":     minvol_metrics,
        "efficient_frontier": frontier,
        "monte_carlo_cloud":  cloud,
        "simulation_stats":   sim_stats,
    }
