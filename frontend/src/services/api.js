/**
 * API client for the Portfolio Optimizer backend.
 */

const rawApiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_BASE = rawApiUrl.endsWith('/api') ? rawApiUrl : `${rawApiUrl}/api`;

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
 */
export async function searchInstruments(query) {
  if (!query || query.trim().length === 0) return [];
  return apiFetch(`${API_BASE}/search?q=${encodeURIComponent(query.trim())}&limit=15`);
}

/**
 * Get popular instruments for quick selection.
 */
export async function getPopularInstruments() {
  return apiFetch(`${API_BASE}/instruments/popular`);
}

/**
 * Get instruments grouped by sector.
 */
export async function getInstrumentsBySector() {
  return apiFetch(`${API_BASE}/instruments/sectors`);
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
export async function analyzePortfolio(holdings, lookback = '1y', riskFreeRate = null) {
  const body = {
    holdings: holdings.map(h => ({ symbol: h.symbol, units: parseFloat(h.units) })),
    lookback,
  };
  if (riskFreeRate !== null) {
    body.risk_free_rate = riskFreeRate;
  }
  return apiFetch(`${API_BASE}/portfolio/analyze`, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}
