import React, { useState } from 'react';
import PortfolioBuilder from './components/PortfolioBuilder';
import OptimizationResults from './components/OptimizationResults';
import EfficientFrontierChart from './components/EfficientFrontierChart';
import ResearchPanel from './components/ResearchPanel';
import { analyzePortfolio } from './services/api';

// ── Tab bar for the right panel ─────────────────────────────────────
const TABS = ['METRICS', 'CHART', 'AI RESEARCH'];

function TabBar({ active, onChange, hasResults }) {
  return (
    <div style={{
      display: 'flex',
      gap: '0',
      marginBottom: '1rem',
      borderBottom: '1px solid var(--border-color)',
    }}>
      {TABS.map(tab => {
        const isActive   = tab === active;
        const isDisabled = tab !== 'AI RESEARCH' && !hasResults;
        return (
          <button
            key={tab}
            onClick={() => !isDisabled && onChange(tab)}
            style={{
              background: isActive ? 'var(--accent)' : 'transparent',
              border: 'none',
              borderBottom: isActive ? '2px solid var(--accent)' : '2px solid transparent',
              color: isActive ? '#000' : isDisabled ? 'var(--text-secondary)' : 'var(--text-primary)',
              cursor: isDisabled ? 'default' : 'pointer',
              fontFamily: 'inherit',
              fontWeight: 700,
              fontSize: '0.7rem',
              letterSpacing: '2px',
              padding: '0.45rem 1rem',
              transition: 'all 0.15s',
              opacity: isDisabled ? 0.4 : 1,
            }}
          >
            {tab}
          </button>
        );
      })}
    </div>
  );
}

function App() {
  const [holdings, setHoldings]       = useState([]);
  const [results, setResults]         = useState(null);
  const [loading, setLoading]         = useState(false);
  const [error, setError]             = useState(null);
  const [riskFreeRate, setRiskFreeRate] = useState(0.068);
  const [maxWeight, setMaxWeight]     = useState(0.40);
  const [activeTab, setActiveTab]     = useState('METRICS');

  const handleOptimize = async (currentHoldings) => {
    setLoading(true);
    setError(null);
    try {
      const data = await analyzePortfolio(currentHoldings, '1y', riskFreeRate, maxWeight, 50000);
      setResults(data);
      setActiveTab('METRICS');   // jump to results on fresh run
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
          <h1>PORTFOLIO OPTIMIZER <span style={{fontSize:'0.8rem', color:'var(--success)'}}>[ ONLINE ]</span></h1>
          <p>EFFICIENT FRONTIER MODEL // INDIAN EQUITIES // AI-ASSISTED</p>
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

        {/* Right Column: Tabbed Results */}
        <div className="right-panel">
          {error && (
            <div className="glass-panel" style={{ borderColor: 'var(--danger)', marginBottom: '0.8rem' }}>
              <div style={{ color: 'var(--danger)', fontWeight: 'bold' }}>[ SYSTEM ERROR ]</div>
              <div style={{ color: 'var(--danger)', fontSize: '0.9rem', marginTop: '0.5rem' }}>{error}</div>
            </div>
          )}

          {/* Always show tab bar once results exist OR on AI tab */}
          {(results || activeTab === 'AI RESEARCH') && (
            <TabBar
              active={activeTab}
              onChange={setActiveTab}
              hasResults={!!results}
            />
          )}

          {/* Tab content */}
          {activeTab === 'AI RESEARCH' ? (
            <div className="glass-panel" style={{ marginBottom: 0 }}>
              <ResearchPanel portfolioContext={results} />
            </div>
          ) : results ? (
            <>
              {activeTab === 'METRICS' && <OptimizationResults results={results} />}
              {activeTab === 'CHART'   && <EfficientFrontierChart results={results} />}
              {loading && (
                <div style={{ color: 'var(--accent)', marginTop: '1rem' }} className="loading-text">
                  RECALCULATING MATRIX...
                </div>
              )}
            </>
          ) : (
            /* Empty state */
            <div className="glass-panel" style={{ height: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center', borderStyle: 'dashed' }}>
              {loading ? (
                <div className="loading-text">OPTIMIZING PORTFOLIO...</div>
              ) : (
                <div style={{ color: 'var(--text-secondary)', textAlign: 'center' }}>
                  <div>[ AWAITING INPUT ]</div>
                  <div style={{ fontSize: '0.8rem', marginTop: '1rem' }}>
                    1. SELECT SECTORS &gt; INSTRUMENTS<br/>
                    2. INPUT ALLOCATION UNITS<br/>
                    3. EXECUTE [ OPTIMIZE ]<br/>
                    <br/>
                    <span style={{ color: 'var(--accent)' }}>
                      ◈ AI RESEARCH TAB →
                    </span>{' '}ask questions<br/>
                    about any stock anytime
                  </div>
                </div>
              )}
            </div>
          )}

          {/* AI Research tab always accessible from empty state */}
          {!results && !loading && (
            <div style={{ marginTop: '0.8rem', textAlign: 'center' }}>
              <button
                onClick={() => setActiveTab('AI RESEARCH')}
                style={{
                  background: 'transparent',
                  border: '1px solid var(--accent)',
                  color: 'var(--accent)',
                  cursor: 'pointer',
                  fontFamily: 'inherit',
                  fontWeight: 700,
                  fontSize: '0.7rem',
                  letterSpacing: '2px',
                  padding: '0.5rem 1.5rem',
                }}
              >
                ◈ OPEN AI RESEARCH
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
