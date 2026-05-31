import React from 'react';

const OptimizationResults = ({ results }) => {
  if (!results) return null;

  const { current_portfolio, optimal_sharpe, min_volatility, total_value } = results;

  return (
    <div className="glass-panel">
      <div className="panel-header">[ ANLYS: PORTFOLIO METRICS ]</div>
      
      <div className="results-grid">
        <div className="metric-card">
          <div className="metric-label">TOTAL VALUE</div>
          <div className="metric-value">
            {total_value.toLocaleString('en-IN', {maximumFractionDigits:0})}
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-label">CURRENT SHARPE</div>
          <div className={`metric-value ${current_portfolio.sharpe_ratio >= 0 ? 'positive' : 'negative'}`}>
            {current_portfolio.sharpe_ratio.toFixed(3)}
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-label">CURRENT VOLATILITY</div>
          <div className="metric-value" style={{ color: 'var(--text-primary)' }}>
            {(current_portfolio.volatility * 100).toFixed(2)}%
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-label">OPTIMAL SHARPE</div>
          <div className={`metric-value ${optimal_sharpe.sharpe_ratio >= 0 ? 'positive' : 'negative'}`}>
            {optimal_sharpe.sharpe_ratio.toFixed(3)}
          </div>
        </div>
      </div>

      <div style={{ marginTop: '1rem', borderTop: '1px solid var(--border-color)', paddingTop: '1rem' }}>
        <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
          [ TBL: WEIGHT & UNIT ALLOCATION MATRIX ]
        </div>
        <table className="comparison-table">
          <thead>
            <tr>
              <th>SYMBOL</th>
              <th>CURR WEIGHT</th>
              <th>OPT SHARPE WGT</th>
              <th>CURR UNITS</th>
              <th>OPT SHARPE UNITS</th>
            </tr>
          </thead>
          <tbody>
            {Object.keys(current_portfolio.weights).map(symbol => {
              const currW = current_portfolio.weights[symbol] * 100;
              const optW = optimal_sharpe.weights[symbol] * 100;
              
              const currU = current_portfolio.units?.[symbol] ?? '-';
              const optU = optimal_sharpe.units?.[symbol] ?? '-';
              
              return (
                <tr key={symbol}>
                  <td>{symbol.replace('.NS', '')}</td>
                  <td>{currW.toFixed(2)}%</td>
                  <td style={{ color: optW > currW ? 'var(--success)' : optW < currW ? 'var(--danger)' : 'inherit' }}>
                    {optW.toFixed(2)}%
                  </td>
                  <td>{currU}</td>
                  <td style={{ color: 'var(--accent)', fontWeight: 'bold' }}>{optU}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default OptimizationResults;
