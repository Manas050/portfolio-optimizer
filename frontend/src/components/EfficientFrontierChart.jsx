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
  Cell
} from 'recharts';

const EfficientFrontierChart = ({ results }) => {
  if (!results || !results.efficient_frontier) return null;

  const { efficient_frontier, current_portfolio, optimal_sharpe, min_volatility } = results;

  const data = useMemo(() => {
    return efficient_frontier.map((point) => ({
      x: point.volatility * 100,
      y: point.expected_return * 100,
      weights: point.weights
    }));
  }, [efficient_frontier]);

  const currentPoint = [{
    x: current_portfolio.volatility * 100,
    y: current_portfolio.expected_return * 100,
    name: 'CURRENT'
  }];

  const optimalPoint = [{
    x: optimal_sharpe.volatility * 100,
    y: optimal_sharpe.expected_return * 100,
    name: 'MAX SHARPE'
  }];
  
  const minVolPoint = [{
    x: min_volatility.volatility * 100,
    y: min_volatility.expected_return * 100,
    name: 'MIN VOL'
  }];

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div style={{ 
          background: '#000', 
          border: '1px solid var(--border-color)', 
          padding: '0.5rem', 
          fontSize: '0.8rem',
          fontFamily: 'JetBrains Mono'
        }}>
          {data.name && <div style={{ color: 'var(--accent)', fontWeight: 'bold', marginBottom: '0.25rem' }}>[{data.name}]</div>}
          <div style={{ color: 'var(--text-secondary)' }}>RETURN: <span style={{ color: data.y >= 0 ? 'var(--success)' : 'var(--danger)' }}>{data.y.toFixed(2)}%</span></div>
          <div style={{ color: 'var(--text-secondary)' }}>VOLATILITY: <span style={{ color: 'var(--text-primary)' }}>{data.x.toFixed(2)}%</span></div>
          
          {data.weights && (
            <div style={{ marginTop: '0.5rem', borderTop: '1px dashed var(--text-secondary)', paddingTop: '0.25rem' }}>
              {Object.entries(data.weights)
                .filter(([_, w]) => w > 0.01)
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
      <div className="panel-header">[ VIZ: EFFICIENT FRONTIER MATRIX ]</div>
      
      <div style={{ height: '400px', width: '100%', paddingRight: '1rem' }}>
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis 
              type="number" 
              dataKey="x" 
              name="Volatility" 
              unit="%" 
              stroke="var(--text-secondary)"
              domain={['dataMin - 1', 'dataMax + 1']}
              tick={{ fill: 'var(--text-secondary)', fontSize: 12, fontFamily: 'JetBrains Mono' }}
              tickFormatter={(val) => val.toFixed(2)}
              label={{ value: 'VOLATILITY (RISK)', position: 'insideBottom', offset: -10, fill: 'var(--border-color)', fontSize: 12, fontFamily: 'JetBrains Mono' }}
            />
            <YAxis 
              type="number" 
              dataKey="y" 
              name="Return" 
              unit="%" 
              stroke="var(--text-secondary)"
              domain={['dataMin - 1', 'dataMax + 1']}
              tick={{ fill: 'var(--text-secondary)', fontSize: 12, fontFamily: 'JetBrains Mono' }}
              tickFormatter={(val) => val.toFixed(2)}
              label={{ value: 'EXPECTED RETURN', angle: -90, position: 'insideLeft', offset: 0, fill: 'var(--border-color)', fontSize: 12, fontFamily: 'JetBrains Mono' }}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />
            
            <ReferenceLine y={0} stroke="#333" />
            
            {/* The Frontier Curve */}
            <Scatter name="Frontier" data={data} fill="var(--text-secondary)" line shape="circle" size={10} />
            
            {/* Current Portfolio */}
            <Scatter name="Current" data={currentPoint} fill="var(--danger)" shape="diamond" size={100} />
            
            {/* Optimal Sharpe */}
            <Scatter name="Optimal" data={optimalPoint} fill="var(--success)" shape="star" size={150} />
            
            {/* Min Volatility */}
            <Scatter name="Min Vol" data={minVolPoint} fill="var(--accent)" shape="triangle" size={100} />

          </ScatterChart>
        </ResponsiveContainer>
      </div>
      
      <div style={{ display: 'flex', gap: '1.5rem', justifyContent: 'center', marginTop: '1rem', fontSize: '0.8rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div style={{ width: '12px', height: '12px', backgroundColor: 'var(--text-secondary)', borderRadius: '50%' }}></div>
          FRONTIER (COMBINATIONS)
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div style={{ width: '12px', height: '12px', backgroundColor: 'var(--danger)', transform: 'rotate(45deg)' }}></div>
          CURRENT
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div style={{ width: '12px', height: '12px', backgroundColor: 'var(--success)', clipPath: 'polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%)' }}></div>
          MAX SHARPE
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div style={{ width: '12px', height: '12px', backgroundColor: 'var(--accent)', clipPath: 'polygon(50% 0%, 0% 100%, 100% 100%)' }}></div>
          MIN VOL
        </div>
      </div>
    </div>
  );
};

export default EfficientFrontierChart;
