import React, { useState, useEffect } from 'react';
import { Trash2 } from 'lucide-react';
import SectorBrowser from './SectorBrowser';
import { fetchPrices } from '../services/api';

const PortfolioBuilder = ({ holdings, setHoldings, onOptimize, loading, riskFreeRate, setRiskFreeRate, maxWeight, setMaxWeight, nSimulations, setNSimulations }) => {
  const [prices, setPrices] = useState({});

  useEffect(() => {
    const getPrices = async () => {
      if (holdings.length === 0) return;
      const symbols = holdings.map(h => h.symbol);
      try {
        const data = await fetchPrices(symbols);
        const priceMap = {};
        data.forEach(p => { priceMap[p.symbol] = p.price; });
        setPrices(prev => ({ ...prev, ...priceMap }));
      } catch (err) {
        console.error('Failed to fetch prices', err);
      }
    };

    getPrices();
    const interval = setInterval(getPrices, 30000); // 30s refresh
    return () => clearInterval(interval);
  }, [holdings]);

  const handleAddInstrument = (inst) => {
    if (holdings.some(h => h.symbol === inst.symbol)) return;
    setHoldings([...holdings, { symbol: inst.symbol, name: inst.name, units: '' }]);
  };

  const removeHolding = (symbol) => {
    setHoldings(holdings.filter(h => h.symbol !== symbol));
  };

  const updateUnits = (symbol, units) => {
    const val = units === '' ? '' : Math.max(0, parseFloat(units) || 0);
    setHoldings(holdings.map(h => h.symbol === symbol ? { ...h, units: val } : h));
  };

  const totalValue = holdings.reduce((sum, h) => {
    const price = prices[h.symbol] || 0;
    const units = h.units || 0;
    return sum + (units * price);
  }, 0);

  return (
    <div>
      <div className="glass-panel">
        <div className="panel-header">
          [ CMD: BROWSE SECTORS ]
        </div>
        <SectorBrowser onAddInstrument={handleAddInstrument} />
      </div>

      <div className="glass-panel" style={{ marginTop: '1rem' }}>
        <div className="panel-header" style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span>[ PRTFL: CURRENT HOLDINGS ]</span>
          <span>{holdings.length} POSITIONS</span>
        </div>

        <div style={{ marginBottom: '1rem', minHeight: '100px' }}>
          {holdings.length === 0 ? (
            <div style={{ color: 'var(--text-secondary)', fontStyle: 'italic', fontSize: '0.8rem' }}>
              &gt; NO POSITIONS FOUND. SELECT FROM SECTORS ABOVE.
            </div>
          ) : (
            holdings.map(h => {
              const price = prices[h.symbol] || 0;
              const units = h.units || 0;
              const value = price * units;
              const weight = totalValue > 0 ? (value / totalValue) * 100 : 0;

              return (
                <div key={h.symbol} style={{ 
                  borderBottom: '1px dashed var(--text-secondary)', 
                  padding: '0.4rem 0',
                }}>
                  {/* Row 1: Symbol + Units Input + Weight + Delete */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <div style={{ color: 'var(--accent)', fontWeight: 'bold', fontSize: '0.85rem', minWidth: '90px' }}>
                      {h.symbol.replace('.NS', '')}
                    </div>
                    <input 
                      type="number" 
                      placeholder="QTY" 
                      value={h.units}
                      onChange={(e) => updateUnits(h.symbol, e.target.value)}
                      min="0"
                      step="1"
                      style={{ 
                        width: '60px', padding: '0.2rem 0.3rem', textAlign: 'right', 
                        fontSize: '0.8rem', border: '1px solid var(--border-color)',
                        background: '#000', color: 'var(--text-primary)',
                        fontFamily: 'JetBrains Mono',
                      }}
                    />
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', flex: 1, textAlign: 'right' }}>
                      {price > 0 ? `@ ${price.toFixed(2)} INR` : 'LDG...'}
                      {value > 0 && <span style={{ color: 'var(--success)', marginLeft: '0.5rem' }}>
                        Val: {value.toLocaleString('en-IN', {maximumFractionDigits:0})}
                      </span>}
                    </div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--accent)', fontWeight: 'bold', minWidth: '45px', textAlign: 'right' }}>
                      {weight.toFixed(1)}%
                    </div>
                    <button 
                      className="btn btn-danger" 
                      style={{ padding: '0.15rem 0.3rem', fontSize: '0.7rem', lineHeight: 1 }}
                      onClick={() => removeHolding(h.symbol)}
                    >
                      <Trash2 size={12} />
                    </button>
                  </div>
                  {/* Row 2: Full name */}
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-secondary)', marginTop: '0.15rem', paddingLeft: '0' }}>
                    {h.name}
                  </div>
                </div>
              );
            })
          )}
        </div>

        <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '0.75rem' }}>
          {/* Portfolio Value */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>EST. PORTFOLIO VALUE</span>
            <span style={{ fontSize: '1.1rem', color: 'var(--accent)', fontWeight: 'bold' }}>
              INR {totalValue.toLocaleString('en-IN', {maximumFractionDigits: 2})}
            </span>
          </div>

          {/* Params Row */}
          <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '0.5rem', fontSize: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              <span style={{ color: 'var(--text-secondary)' }}>MAX ALLOC:</span>
              <div style={{ display: 'flex', alignItems: 'center', border: '1px solid var(--border-color)', paddingRight: '0.2rem' }}>
                <input 
                  type="number" step="5"
                  value={maxWeight * 100} 
                  onChange={(e) => setMaxWeight((parseFloat(e.target.value) || 0) / 100)}
                  style={{ width: '36px', background: 'transparent', border: 'none', color: 'var(--accent)', padding: '0.2rem', fontFamily: 'JetBrains Mono', outline: 'none', fontSize: '0.75rem' }}
                />
                <span style={{ color: 'var(--text-secondary)' }}>%</span>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              <span style={{ color: 'var(--text-secondary)' }}>RISK-FREE:</span>
              <div style={{ display: 'flex', alignItems: 'center', border: '1px solid var(--border-color)', paddingRight: '0.2rem' }}>
                <input 
                  type="number" step="0.1"
                  value={riskFreeRate * 100} 
                  onChange={(e) => setRiskFreeRate((parseFloat(e.target.value) || 0) / 100)}
                  style={{ width: '36px', background: 'transparent', border: 'none', color: 'var(--accent)', padding: '0.2rem', fontFamily: 'JetBrains Mono', outline: 'none', fontSize: '0.75rem' }}
                />
                <span style={{ color: 'var(--text-secondary)' }}>%</span>
              </div>
            </div>
          </div>

          {/* Simulations Row */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.5rem', fontSize: '0.7rem' }}>
            <span style={{ color: 'var(--text-secondary)' }}>SIMULATIONS:</span>
            {[10000, 25000, 50000, 100000].map(n => (
              <button
                key={n}
                onClick={() => setNSimulations(n)}
                style={{
                  padding: '0.15rem 0.4rem',
                  fontSize: '0.65rem',
                  fontFamily: 'JetBrains Mono',
                  background: nSimulations === n ? 'var(--accent)' : 'transparent',
                  color: nSimulations === n ? '#000' : 'var(--text-secondary)',
                  border: '1px solid ' + (nSimulations === n ? 'var(--accent)' : 'var(--border-color)'),
                  cursor: 'pointer',
                }}
              >
                {n >= 1000 ? `${n/1000}K` : n}
              </button>
            ))}
          </div>
          <button 
            className="btn" 
            style={{ width: '100%' }}
            onClick={() => onOptimize(holdings)}
            disabled={holdings.length < 2 || loading}
          >
            {loading ? `RUNNING ${nSimulations.toLocaleString()} SIMULATIONS...` : `RUN MONTE CARLO [${(nSimulations/1000).toFixed(0)}K]`}
          </button>
        </div>
        
        {holdings.length < 2 && holdings.length > 0 && (
          <div style={{ color: 'var(--danger)', fontSize: '0.7rem', marginTop: '0.5rem' }}>
            WARN: MIN 2 POSITIONS REQUIRED FOR ANALYSIS
          </div>
        )}
      </div>
    </div>
  );
};

export default PortfolioBuilder;
