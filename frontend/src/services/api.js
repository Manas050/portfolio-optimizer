/**
 * API client for the Portfolio Optimizer backend.
 */

const rawApiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_BASE = rawApiUrl.endsWith('/api') ? rawApiUrl : `${rawApiUrl}/api`;

// ── Module-level in-memory caches ────────────────────────────────────
// Sectors never change during a session — cache indefinitely
let _sectorsCache = null;

// Search results: cache per query for 60 s
const _searchCache = new Map(); // query -> { ts, data }
const SEARCH_TTL = 60_000;

/**
 * Generic fetch wrapper with error handling.
 */
async function apiFetch(url, options = {}) {
  try {
    const response = await fetch(url, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
      throw new Error('Cannot connect to the backend server. Make sure it is running on port 8000.');
    }
    throw error;
  }
}

/**
 * Search instruments by name, symbol, or sector.
 * Results are cached per query for 60 s to avoid hammering on every keystroke.
 */
export async function searchInstruments(query) {
  if (!query || query.trim().length === 0) return [];
  const key = query.trim().toLowerCase();
  const cached = _searchCache.get(key);
  if (cached && Date.now() - cached.ts < SEARCH_TTL) return cached.data;
  const data = await apiFetch(`${API_BASE}/search?q=${encodeURIComponent(key)}&limit=20`);
  _searchCache.set(key, { ts: Date.now(), data });
  return data;
}

/**
 * Get popular instruments for quick selection.
 */
export async function getPopularInstruments() {
  return apiFetch(`${API_BASE}/instruments/popular`);
}

/**
 * Get instruments grouped by sector.
 * Cached indefinitely for the session — the catalog is static.
 */
export async function getInstrumentsBySector() {
  if (_sectorsCache) return _sectorsCache;
  _sectorsCache = await apiFetch(`${API_BASE}/instruments/sectors`);
  return _sectorsCache;
}

/**
 * Fetch live prices for a list of symbols.
 */
export async function fetchPrices(symbols) {
  return apiFetch(`${API_BASE}/prices`, {
    method: 'POST',
    body: JSON.stringify({ symbols }),
  });
}

/**
 * Run full portfolio analysis.
 * @param {Array<{symbol: string, units: number}>} holdings
 * @param {string} lookback - Period string (e.g., "1y", "6mo")
 * @param {number|null} riskFreeRate - Override risk-free rate
 */
export async function analyzePortfolio(holdings, lookback = '1y', riskFreeRate = null, maxWeight = 0.40, nSimulations = 50000) {
  const body = {
    holdings: holdings.map(h => {
      const parsed = parseFloat(h.units);
      return { symbol: h.symbol, units: isNaN(parsed) ? 0 : parsed };
    }),
    lookback,
    n_simulations: nSimulations,
  };
  if (riskFreeRate !== null) {
    body.risk_free_rate = riskFreeRate;
  }
  if (maxWeight !== null) {
    body.max_weight = maxWeight;
  }
  return apiFetch(`${API_BASE}/portfolio/analyze`, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}
