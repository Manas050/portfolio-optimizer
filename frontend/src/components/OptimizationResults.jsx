import React from 'react';

const OptimizationResults = ({ results }) => {
  if (!results) return null;

  const {
    current_portfolio,
    optimal_sharpe,
    min_volatility,
    total_value,
    warnings,
    effective_max_weight,
    risk_free_rate,
    simulation_stats,
  } = results;

  const fmtPct = (v) => `${(v * 100).toFixed(2)}%`;
  const fmtSharpe = (v) => v?.toFixed(3) ?? '—';

  return (
    <div className="glass-panel">
      <div className="panel-header">[ ANLYS: PORTFOLIO METRICS ]</div>

      {/* Simulation Stats Banner */}
      {simulation_stats && (
        <div style={{
          display: 'flex',
          gap: '1rem',
          flexWrap: 'wrap',
          marginBottom: '1rem',
          padding: '0.5rem 0.75rem',
          border: '1px solid #1a3a1a',
          background: 'rgba(0,255,0,0.03)',
          fontSize: '0.7rem',
          color: 'var(--text-secondary)',
        }}>
          <span>⚙ MC ENGINE</span>
          <span style={{ color: 'var(--accent)' }}>{simulation_stats.n_simulations.toLocaleString()} SIMULATIONS</span>
          <span>·</span>
          <span>TOP {simulation_stats.top_percentile}% → MEDIAN SELECTION</span>
          <span>·</span>
          <span>BEST SHARPE: <span style={{ color: 'var(--success)' }}>{fmtSharpe(simulation_stats.best_sharpe)}</span></span>
          <span>·</span>
          <span>SELECTED: <span style={{ color: 'var(--accent)' }}>{fmtSharpe(simulation_stats.median_sharpe)}</span></span>
          <span>·</span>
          <span>WORST: <span style={{ color: 'var(--danger)' }}>{fmtSharpe(simulation_stats.worst_sharpe)}</span></span>
        </div>
      )}

      {/* Warnings */}
      {warnings && warnings.length > 0 && (
        <div style={{ marginBottom: '1rem' }}>
          {warnings.map((w, i) => (
            <div key={i} style={{
              padding: '0.5rem 0.75rem',
              border: '1px solid var(--danger)',
              background: 'rgba(255,0,0,0.08)',
              color: 'var(--danger)',
              fontSize: '0.75rem',
              marginBottom: '0.25rem',
              lineHeight: 1.4,
            }}>
              {w}
            </div>
          ))}
        </div>
      )}

      {/* Metrics Grid */}
      <div className="results-grid">
        <div className="metric-card">
          <div className="metric-label">TOTAL VALUE</div>
          <div className="metric-value">
            {total_value.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-label">CURRENT SHARPE</div>
          <div className={`metric-value ${current_portfolio.sharpe_ratio >= 0 ? 'positive' : 'negative'}`}>
            {fmtSharpe(current_portfolio.sharpe_ratio)}
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-label">CURRENT VOLATILITY</div>
          <div className="metric-value" style={{ color: 'var(--text-primary)' }}>
            {fmtPct(current_portfolio.volatility)}
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-label">OPTIMAL SHARPE</div>
          <div className={`metric-value ${optimal_sharpe.sharpe_ratio >= 0 ? 'positive' : 'negative'}`}>
            {fmtSharpe(optimal_sharpe.sharpe_ratio)}
          </div>
        </div>
      </div>

      {/* Config */}
      <div style={{ fontSize: '0.65rem', color: 'var(--text-secondary)', marginTop: '0.5rem', display: 'flex', gap: '1rem' }}>
        <span>Rf: {((risk_free_rate || 0) * 100).toFixed(1)}%</span>
        <span>MAX ALLOC: {((effective_max_weight || 1) * 100).toFixed(0)}%</span>
        <span>LOOKBACK: {results.lookback}</span>
      </div>

      {/* Three-way comparison table */}
      <div style={{ marginTop: '1rem', borderTop: '1px solid var(--border-color)', paddingTop: '1rem' }}>
        <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
          [ TBL: WEIGHT & UNIT ALLOCATION MATRIX ]
        </div>

        {/* Column headers */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr 1fr 1fr',
          gap: '0.25rem',
          fontSize: '0.7rem',
          color: 'var(--text-secondary)',
          borderBottom: '1px solid var(--border-color)',
          paddingBottom: '0.25rem',
          marginBottom: '0.25rem',
          textAlign: 'right',
        }}>
          <span style={{ textAlign: 'left' }}>SYMBOL</span>
          <span>CURRENT</span>
          <span style={{ color: '#00ff88' }}>OPTIMAL ★</span>
          <span style={{ color: '#ffd700' }}>MIN VOL ▲</span>
        </div>

        {Object.keys(current_portfolio.weights).map(symbol => {
          const currW = current_portfolio.weights[symbol] * 100;
          const optW = (optimal_sharpe.weights[symbol] ?? 0) * 100;
          const minW = (min_volatility.weights[symbol] ?? 0) * 100;
          const optU = optimal_sharpe.units?.[symbol] ?? '—';
          const minU = min_volatility.units?.[symbol] ?? '—';

          return (
            <div key={symbol} style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr 1fr 1fr',
              gap: '0.25rem',
              fontSize: '0.8rem',
              padding: '0.25rem 0',
              borderBottom: '1px dashed #111',
              textAlign: 'right',
            }}>
              <span style={{ textAlign: 'left', color: 'var(--accent)' }}>{symbol.replace('.NS', '')}</span>
              <span>{currW.toFixed(1)}%</span>
              <span style={{ color: optW > currW ? 'var(--success)' : optW < currW ? 'var(--danger)' : 'inherit' }}>
                {optW.toFixed(1)}% <span style={{ fontSize: '0.65rem', color: 'var(--text-secondary)' }}>({optU}u)</span>
              </span>
              <span style={{ color: '#ffd700' }}>
                {minW.toFixed(1)}% <span style={{ fontSize: '0.65rem', color: 'var(--text-secondary)' }}>({minU}u)</span>
              </span>
            </div>
          );
        })}

        {/* Summary row */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr 1fr 1fr',
          gap: '0.25rem',
          fontSize: '0.75rem',
          marginTop: '0.5rem',
          paddingTop: '0.5rem',
          borderTop: '1px solid var(--border-color)',
          textAlign: 'right',
        }}>
          <span style={{ textAlign: 'left', color: 'var(--text-secondary)' }}>METRICS</span>
          <div>
            <div style={{ color: current_portfolio.expected_return >= 0 ? 'var(--success)' : 'var(--danger)', fontSize: '0.7rem' }}>
              R: {fmtPct(current_portfolio.expected_return)}
            </div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.7rem' }}>σ: {fmtPct(current_portfolio.volatility)}</div>
            <div style={{ color: current_portfolio.sharpe_ratio >= 0 ? 'var(--success)' : 'var(--danger)', fontSize: '0.7rem' }}>
              S: {fmtSharpe(current_portfolio.sharpe_ratio)}
            </div>
          </div>
          <div>
            <div style={{ color: optimal_sharpe.expected_return >= 0 ? '#00ff88' : 'var(--danger)', fontSize: '0.7rem' }}>
              R: {fmtPct(optimal_sharpe.expected_return)}
            </div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.7rem' }}>σ: {fmtPct(optimal_sharpe.volatility)}</div>
            <div style={{ color: optimal_sharpe.sharpe_ratio >= 0 ? '#00ff88' : 'var(--danger)', fontSize: '0.7rem' }}>
              S: {fmtSharpe(optimal_sharpe.sharpe_ratio)}
            </div>
          </div>
          <div>
            <div style={{ color: min_volatility.expected_return >= 0 ? '#ffd700' : 'var(--danger)', fontSize: '0.7rem' }}>
              R: {fmtPct(min_volatility.expected_return)}
            </div>
            <div style={{ color: '#ffd700', fontSize: '0.7rem' }}>σ: {fmtPct(min_volatility.volatility)}</div>
            <div style={{ color: min_volatility.sharpe_ratio >= 0 ? '#ffd700' : 'var(--danger)', fontSize: '0.7rem' }}>
              S: {fmtSharpe(min_volatility.sharpe_ratio)}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OptimizationResults;
