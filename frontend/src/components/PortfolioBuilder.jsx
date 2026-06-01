import React, { useState, useEffect } from 'react';
import { Trash2 } from 'lucide-react';
import SectorBrowser from './SectorBrowser';
import { fetchPrices } from '../services/api';

const PortfolioBuilder = ({ holdings, setHoldings, onOptimize, loading, riskFreeRate, setRiskFreeRate }) => {
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

        <div style={{ marginBottom: '1rem', minHeight: '150px' }}>
          {holdings.length === 0 ? (
            <div style={{ color: 'var(--text-secondary)', fontStyle: 'italic' }}>
              &gt; NO POSITIONS FOUND. SELECT FROM SECTORS ABOVE.
            </div>
          ) : (
            holdings.map(h => {
              const price = prices[h.symbol] || 0;
              const units = h.units || 0;
              const value = price * units;
              const weight = totalValue > 0 ? (value / totalValue) * 100 : 0;

              return (
                <div key={h.symbol} className="asset-item">
                  <div style={{ flex: 1 }}>
                    <div style={{ color: 'var(--accent)', fontWeight: 'bold' }}>{h.symbol.replace('.NS', '')}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{h.name}</div>
                  </div>
                  
                  <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                    <div className="input-group" style={{ marginBottom: 0, width: '100px' }}>
                      <input 
                        type="number" 
                        placeholder="UNITS" 
                        value={h.units}
                        onChange={(e) => updateUnits(h.symbol, e.target.value)}
                        min="0"
                        step="1"
                        style={{ padding: '0.25rem', textAlign: 'right' }}
                      />
                    </div>
                    
                    <div style={{ width: '120px', textAlign: 'right', fontSize: '0.85rem' }}>
                      <div>{price > 0 ? `@ ${price.toFixed(2)} INR` : 'LDG...'}</div>
                      <div style={{ color: 'var(--success)' }}>
                        {value > 0 ? `Val: ${value.toLocaleString('en-IN', {maximumFractionDigits:0})}` : ''}
                      </div>
                    </div>
                    
                    <div style={{ width: '60px', textAlign: 'right', color: 'var(--accent)' }}>
                      {weight > 0 ? `${weight.toFixed(1)}%` : '0.0%'}
                    </div>

                    <button 
                      className="btn btn-danger" 
                      style={{ padding: '0.25rem 0.5rem' }}
                      onClick={() => removeHolding(h.symbol)}
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid var(--border-color)', paddingTop: '1rem' }}>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>EST. PORTFOLIO VALUE</div>
            <div style={{ fontSize: '1.25rem', color: 'var(--accent)', fontWeight: 'bold' }}>
              INR {totalValue.toLocaleString('en-IN', {maximumFractionDigits: 2})}
            </div>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem' }}>
              <span style={{ color: 'var(--text-secondary)' }}>RISK-FREE RATE:</span>
              <input 
                type="number" 
                step="0.001"
                value={riskFreeRate} 
                onChange={(e) => setRiskFreeRate(parseFloat(e.target.value) || 0)}
                style={{ width: '80px', background: 'transparent', border: '1px solid var(--border-color)', color: 'var(--accent)', padding: '0.25rem', fontFamily: 'JetBrains Mono' }}
              />
            </div>
            <button 
              className="btn" 
              onClick={() => onOptimize(holdings)}
              disabled={holdings.length < 2 || loading}
            >
              {loading ? 'RUNNING OPTIMIZER...' : 'EXECUTE [ OPTIMIZE ]'}
            </button>
          </div>
        </div>
        
        {holdings.length < 2 && holdings.length > 0 && (
          <div style={{ color: 'var(--danger)', fontSize: '0.75rem', marginTop: '0.5rem', textAlign: 'right' }}>
            WARN: MIN 2 POSITIONS REQUIRED FOR ANALYSIS
          </div>
        )}
      </div>
    </div>
  );
};

export default PortfolioBuilder;
