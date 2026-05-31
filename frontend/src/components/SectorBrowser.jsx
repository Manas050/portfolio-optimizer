import React, { useState, useEffect } from 'react';
import { Plus } from 'lucide-react';
import { getInstrumentsBySector } from '../services/api';

const SectorBrowser = ({ onAddInstrument }) => {
  const [sectors, setSectors] = useState({});
  const [expandedSector, setExpandedSector] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSectors = async () => {
      try {
        const data = await getInstrumentsBySector();
        setSectors(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchSectors();
  }, []);

  if (loading) {
    return <div className="loading-text">LOADING SECTOR DATA...</div>;
  }

  if (error) {
    return <div style={{ color: 'var(--danger)' }}>ERROR: {error}</div>;
  }

  return (
    <div className="sector-browser">
      {Object.entries(sectors).map(([sectorName, instruments]) => (
        <div key={sectorName}>
          <div 
            className="sector-header"
            onClick={() => setExpandedSector(expandedSector === sectorName ? null : sectorName)}
          >
            <span>{sectorName}</span>
            <span>[{instruments.length}] {expandedSector === sectorName ? '-' : '+'}</span>
          </div>
          
          {expandedSector === sectorName && (
            <div className="sector-items">
              {instruments.map(inst => (
                <div 
                  key={inst.symbol} 
                  className="instrument-row"
                  onClick={() => onAddInstrument(inst)}
                >
                  <span style={{ width: '80px', color: 'var(--text-secondary)' }}>{inst.symbol.replace('.NS', '')}</span>
                  <span style={{ flex: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {inst.name}
                  </span>
                  <Plus size={14} style={{ color: 'var(--success)' }} />
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default SectorBrowser;
