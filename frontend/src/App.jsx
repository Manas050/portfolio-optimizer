import React, { useState } from 'react';
import PortfolioBuilder from './components/PortfolioBuilder';
import OptimizationResults from './components/OptimizationResults';
import EfficientFrontierChart from './components/EfficientFrontierChart';
import { analyzePortfolio } from './services/api';

function App() {
  const [holdings, setHoldings] = useState([]);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [riskFreeRate, setRiskFreeRate] = useState(0.068);
  const [maxWeight, setMaxWeight] = useState(0.40);

  const handleOptimize = async (currentHoldings) => {
    setLoading(true);
    setError(null);
    try {
      const data = await analyzePortfolio(currentHoldings, '1y', riskFreeRate, maxWeight, 50000);
      setResults(data);
    } catch (err) {
      console.error(err);
      setError(err.message || 'An error occurred during optimization.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header>
        <div>
          <h1>PORTFOLIO OPTIMIZER <span style={{fontSize:'0.8rem', color:'var(--success)'}}>[ONLINE]</span></h1>
          <p>EFFICIENT FRONTIER MODEL // INDIAN EQUITIES</p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>SYS.TIME</div>
          <div style={{ color: 'var(--accent)' }}>{new Date().toLocaleTimeString('en-IN')}</div>
        </div>
      </header>

      <div className="dashboard-grid">
        {/* Left Column: Build Portfolio */}
        <div className="left-panel">
          <PortfolioBuilder 
            holdings={holdings} 
            setHoldings={setHoldings} 
            onOptimize={handleOptimize} 
            loading={loading} 
            riskFreeRate={riskFreeRate}
            setRiskFreeRate={setRiskFreeRate}
            maxWeight={maxWeight}
            setMaxWeight={setMaxWeight}
          />
        </div>
        
        {/* Right Column: Results */}
        <div className="right-panel">
          {error && (
            <div className="glass-panel" style={{ borderColor: 'var(--danger)' }}>
              <div style={{ color: 'var(--danger)', fontWeight: 'bold' }}>[ SYSTEM ERROR ]</div>
              <div style={{ color: 'var(--danger)', fontSize: '0.9rem', marginTop: '0.5rem' }}>{error}</div>
            </div>
          )}

          {results ? (
            <>
              <OptimizationResults results={results} />
              <EfficientFrontierChart results={results} />
              
              {loading && (
                <div style={{ color: 'var(--accent)', marginTop: '1rem' }} className="loading-text">
                  RECALCULATING MATRIX...
                </div>
              )}
            </>
          ) : (
            <div className="glass-panel" style={{ height: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center', borderStyle: 'dashed' }}>
              {loading ? (
              <div className="loading-text">OPTIMIZING PORTFOLIO...</div>
              ) : (
                <div style={{ color: 'var(--text-secondary)', textAlign: 'center' }}>
                  <div>[ AWAITING INPUT ]</div>
                  <div style={{ fontSize: '0.8rem', marginTop: '1rem' }}>
                    1. SELECT SECTORS &gt; INSTRUMENTS<br/>
                    2. INPUT ALLOCATION UNITS<br/>
                    3. EXECUTE [ OPTIMIZE ]
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
