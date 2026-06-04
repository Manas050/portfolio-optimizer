import React, { useMemo } from 'react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  ZAxis,
} from 'recharts';

const EfficientFrontierChart = ({ results }) => {
  if (!results || !results.efficient_frontier) return null;

  const { efficient_frontier, current_portfolio, optimal_sharpe, min_volatility, monte_carlo } = results;

  // Frontier curve data
  const frontierData = useMemo(() => {
    return efficient_frontier.map((point) => ({
      x: point.volatility * 100,
      y: point.expected_return * 100,
      weights: point.weights,
    }));
  }, [efficient_frontier]);

  // Monte Carlo random portfolios — color by Sharpe
  const mcData = useMemo(() => {
    if (!monte_carlo || monte_carlo.length === 0) return [];
    return monte_carlo.map((p) => ({
      x: p.volatility * 100,
      y: p.expected_return * 100,
      sharpe: p.sharpe_ratio,
    }));
  }, [monte_carlo]);

  // Key portfolio points
  const currentPoint = [{
    x: current_portfolio.volatility * 100,
    y: current_portfolio.expected_return * 100,
    name: 'CURRENT',
    sharpe: current_portfolio.sharpe_ratio,
  }];

  const optimalPoint = [{
    x: optimal_sharpe.volatility * 100,
    y: optimal_sharpe.expected_return * 100,
    name: 'MAX SHARPE',
    sharpe: optimal_sharpe.sharpe_ratio,
  }];

  const minVolPoint = [{
    x: min_volatility.volatility * 100,
    y: min_volatility.expected_return * 100,
    name: 'MIN VOL',
    sharpe: min_volatility.sharpe_ratio,
  }];

  // Determine Sharpe color
  const getSharpeColor = (sharpe) => {
    if (sharpe < 0) return 'rgba(255, 50, 50, 0.25)';
    if (sharpe < 0.5) return 'rgba(255, 120, 50, 0.25)';
    if (sharpe < 1.0) return 'rgba(255, 200, 50, 0.30)';
    if (sharpe < 1.5) return 'rgba(100, 255, 100, 0.30)';
    return 'rgba(50, 200, 255, 0.35)';
  };

  // Custom dot renderer for Monte Carlo
  const MCDot = (props) => {
    const { cx, cy, payload } = props;
    if (!cx || !cy) return null;
    return (
      <circle
        cx={cx}
        cy={cy}
        r={2}
        fill={getSharpeColor(payload.sharpe)}
        stroke="none"
      />
    );
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div style={{
          background: 'rgba(0,0,0,0.95)',
          border: '1px solid var(--border-color)',
          padding: '0.5rem',
          fontSize: '0.8rem',
          fontFamily: 'JetBrains Mono',
          maxWidth: '280px',
        }}>
          {data.name && <div style={{ color: 'var(--accent)', fontWeight: 'bold', marginBottom: '0.25rem' }}>[{data.name}]</div>}
          <div style={{ color: 'var(--text-secondary)' }}>RETURN: <span style={{ color: data.y >= 0 ? 'var(--success)' : 'var(--danger)' }}>{data.y.toFixed(2)}%</span></div>
          <div style={{ color: 'var(--text-secondary)' }}>VOLATILITY: <span style={{ color: 'var(--text-primary)' }}>{data.x.toFixed(2)}%</span></div>
          {data.sharpe !== undefined && (
            <div style={{ color: 'var(--text-secondary)' }}>SHARPE: <span style={{ color: data.sharpe >= 1 ? 'var(--success)' : data.sharpe >= 0 ? 'var(--text-primary)' : 'var(--danger)' }}>{data.sharpe.toFixed(3)}</span></div>
          )}

          {data.weights && (
            <div style={{ marginTop: '0.5rem', borderTop: '1px dashed var(--text-secondary)', paddingTop: '0.25rem' }}>
              {Object.entries(data.weights)
                .filter(([_, w]) => w > 0.005)
                .sort(([, a], [, b]) => b - a)
                .map(([sym, w]) => (
                  <div key={sym} style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem' }}>
                    <span>{sym.replace('.NS', '')}:</span>
                    <span>{(w * 100).toFixed(1)}%</span>
                  </div>
              ))}
            </div>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="glass-panel">
      <div className="panel-header">[ VIZ: EFFICIENT FRONTIER & MONTE CARLO ]</div>

      <div style={{ height: '450px', width: '100%', paddingRight: '1rem' }}>
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#222" />
            <XAxis
              type="number"
              dataKey="x"
              name="Volatility"
              unit="%"
              stroke="var(--text-secondary)"
              domain={['dataMin - 2', 'dataMax + 2']}
              tick={{ fill: 'var(--text-secondary)', fontSize: 11, fontFamily: 'JetBrains Mono' }}
              tickFormatter={(val) => typeof val === 'number' ? val.toFixed(1) : val}
              label={{ value: 'VOLATILITY (ANNUALISED σ)', position: 'insideBottom', offset: -10, fill: '#555', fontSize: 11, fontFamily: 'JetBrains Mono' }}
            />
            <YAxis
              type="number"
              dataKey="y"
              name="Return"
              unit="%"
              stroke="var(--text-secondary)"
              domain={['dataMin - 2', 'dataMax + 2']}
              tick={{ fill: 'var(--text-secondary)', fontSize: 11, fontFamily: 'JetBrains Mono' }}
              tickFormatter={(val) => typeof val === 'number' ? val.toFixed(1) : val}
              label={{ value: 'EXPECTED RETURN (ANNUALISED)', angle: -90, position: 'insideLeft', offset: 0, fill: '#555', fontSize: 11, fontFamily: 'JetBrains Mono' }}
            />
            <ZAxis range={[10, 10]} />
            <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />

            <ReferenceLine y={0} stroke="#333" />

            {/* Monte Carlo Cloud (render first so frontier draws on top) */}
            {mcData.length > 0 && (
              <Scatter
                name="Monte Carlo"
                data={mcData}
                shape={<MCDot />}
                isAnimationActive={false}
              />
            )}

            {/* The Efficient Frontier Curve */}
            <Scatter
              name="Frontier"
              data={frontierData}
              fill="none"
              stroke="#00e5ff"
              strokeWidth={2.5}
              line={{ strokeWidth: 2.5 }}
              shape="circle"
              legendType="line"
              r={3}
              isAnimationActive={false}
            >
            </Scatter>

            {/* Current Portfolio */}
            <Scatter name="Current" data={currentPoint} fill="#ff4444" shape="diamond" size={120} isAnimationActive={false} />

            {/* Optimal Sharpe */}
            <Scatter name="Optimal" data={optimalPoint} fill="#00ff88" shape="star" size={180} isAnimationActive={false} />

            {/* Min Volatility */}
            <Scatter name="Min Vol" data={minVolPoint} fill="#ffd700" shape="triangle" size={120} isAnimationActive={false} />

          </ScatterChart>
        </ResponsiveContainer>
      </div>

      {/* Legend */}
      <div style={{ display: 'flex', gap: '1.5rem', justifyContent: 'center', marginTop: '1rem', fontSize: '0.75rem', flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <div style={{ width: '20px', height: '3px', backgroundColor: '#00e5ff', borderRadius: '2px' }}></div>
          EFFICIENT FRONTIER
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <div style={{ width: '10px', height: '10px', backgroundColor: 'rgba(200,200,100,0.35)', borderRadius: '50%' }}></div>
          MONTE CARLO ({mcData.length.toLocaleString()})
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <div style={{ width: '10px', height: '10px', backgroundColor: '#ff4444', transform: 'rotate(45deg)' }}></div>
          CURRENT
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <div style={{ width: '12px', height: '12px', backgroundColor: '#00ff88', clipPath: 'polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%)' }}></div>
          MAX SHARPE
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <div style={{ width: '10px', height: '10px', backgroundColor: '#ffd700', clipPath: 'polygon(50% 0%, 0% 100%, 100% 100%)' }}></div>
          MIN VOL
        </div>
      </div>

      {/* Sharpe color scale */}
      <div style={{ display: 'flex', justifyContent: 'center', marginTop: '0.5rem', fontSize: '0.65rem', color: 'var(--text-secondary)', gap: '0.75rem' }}>
        <span>SHARPE SCALE:</span>
        <span style={{ color: 'rgba(255, 50, 50, 0.8)' }}>● &lt;0</span>
        <span style={{ color: 'rgba(255, 120, 50, 0.8)' }}>● 0–0.5</span>
        <span style={{ color: 'rgba(255, 200, 50, 0.8)' }}>● 0.5–1</span>
        <span style={{ color: 'rgba(100, 255, 100, 0.8)' }}>● 1–1.5</span>
        <span style={{ color: 'rgba(50, 200, 255, 0.8)' }}>● &gt;1.5</span>
      </div>
    </div>
  );
};

export default EfficientFrontierChart;
