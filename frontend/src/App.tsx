import React, { useState } from 'react';
import { useEffect } from 'react';
// import connection from './signalr';
// Load backend URL from config
import backendConfig from './config';
import './App.css';

function App() {
  const [symbol, setSymbol] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [allSymbols, setAllSymbols] = useState<string[]>([]);
  const [signal, setSignal] = useState<any>(null);
  const [realtimeSignal, setRealtimeSignal] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  // priceHistory is for Yahoo Finance historical prices, not signal history
  const [priceHistory, setPriceHistory] = useState<any[]>([]);
  const [berkshireHoldings, setBerkshireHoldings] = useState<any[]>([]);
  const fetchHistory = async () => {
    // Fetch signal history from backend DB
    const res = await fetch(`${backendConfig.BACKEND_URL}/signal_history?symbol=${symbol}`);
    const data = await res.json();
    setHistory(Array.isArray(data.history) ? data.history : []);
  };

  const fetchSignal = async () => {
    const res = await fetch(`${backendConfig.BACKEND_URL}/predict?symbol=${symbol}`);
    setSignal(await res.json());
  };

  useEffect(() => {
    // Fetch ASX symbols from public JSON file
    fetch('/asx_symbols.json')
      .then(res => res.json())
      .then(data => setAllSymbols(data));
    // Fetch Berkshire 13F holdings
    fetch('/berkshire_13f.json')
      .then(res => res.json())
      .then(data => setBerkshireHoldings(data));
    // Connect to FastAPI WebSocket for real-time signals
    const ws = new WebSocket(`${backendConfig.BACKEND_URL.replace(/^http/, 'ws')}/ws/signals`);
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setRealtimeSignal(data);
      } catch (e) {
        // Ignore parse errors
      }
    };
    ws.onerror = () => {
      // Optionally handle errors
    };
    return () => {
      ws.close();
    };
  }, []);

  const handleSymbolChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.toUpperCase();
    setSymbol(value);
    if (value.length > 0) {
      // Substring match, but prioritize prefix matches
      const filtered = allSymbols.filter(s => s.includes(value) && s !== value);
      // Sort: prefix matches first, then others
      filtered.sort((a, b) => {
        const aStarts = a.startsWith(value) ? -1 : 0;
        const bStarts = b.startsWith(value) ? -1 : 0;
        return aStarts - bStarts || a.localeCompare(b);
      });
      setSuggestions(filtered.slice(0, 8));
    } else {
      setSuggestions([]);
    }
  };

  const handleSuggestionClick = (s: string) => {
    setSymbol(s);
    setSuggestions([]);
  };

  return (
    <div className="app-container">
      <h1 className="app-title">AnyStockAI: ASX Tracker</h1>
      <div className="input-row">
        <div style={{ position: 'relative', width: 200 }}>
          <input className="symbol-input" value={symbol} onChange={handleSymbolChange} placeholder="ASX Symbol" autoComplete="off" />
          {suggestions.length > 0 && (
            <ul className="autocomplete-list">
              {suggestions.map(s => (
                <li key={s} onClick={() => handleSuggestionClick(s)}>{s}</li>
              ))}
            </ul>
          )}
        </div>
        <button className="action-btn" onClick={fetchSignal}>Get Signal</button>
        <button className="action-btn" onClick={fetchHistory} style={{marginLeft: '1em'}}>Show History</button>
      </div>
      {signal && (
        <div className="signal-card">
          <h2>Latest Signal</h2>
          <div className="signal-details">
            <span><strong>Buy:</strong> {signal.buy_signal ? 'Yes' : 'No'}</span>
            <span><strong>Sell:</strong> {signal.sell_signal ? 'Yes' : 'No'}</span>
            <span><strong>Hold:</strong> {signal.hold_signal ? 'Yes' : 'No'}</span>
            <span><strong>Confidence:</strong> {signal.confidence}</span>
            <span><strong>Current Price:</strong> {signal.current_price !== undefined && signal.current_price !== null ? signal.current_price : 'N/A'}</span>
            <span><strong>Open Price:</strong> {signal.open_price !== undefined && signal.open_price !== null ? signal.open_price : 'N/A'}</span>
            <span><strong>High Price:</strong> {signal.high_price !== undefined && signal.high_price !== null ? signal.high_price : 'N/A'}</span>
            <span><strong>Low Price:</strong> {signal.low_price !== undefined && signal.low_price !== null ? signal.low_price : 'N/A'}</span>
          </div>
        </div>
      )}
      {realtimeSignal && (
        <div className="realtime-card">
          <h2>Real-Time Signal Update</h2>
          <div className="signal-details">
            <span><strong>Symbol:</strong> {realtimeSignal.symbol}</span>
            <span><strong>Buy:</strong> {realtimeSignal.buy_signal ? 'Yes' : 'No'}</span>
            <span><strong>Sell:</strong> {realtimeSignal.sell_signal ? 'Yes' : 'No'}</span>
            <span><strong>Hold:</strong> {realtimeSignal.hold_signal ? 'Yes' : 'No'}</span>
            <span><strong>Confidence:</strong> {realtimeSignal.confidence}</span>
            <span><strong>Current Price:</strong> {realtimeSignal.current_price !== undefined && realtimeSignal.current_price !== null ? realtimeSignal.current_price : 'N/A'}</span>
            <span><strong>Timestamp:</strong> {realtimeSignal.timestamp}</span>
          </div>
        </div>
      )}
      {priceHistory.length > 0 && (
        <div className="history-section">
          <h2>Historical Price Data (Yahoo Finance)</h2>
          <table className="styled-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Open</th>
                <th>High</th>
                <th>Low</th>
                <th>Close</th>
                <th>Volume</th>
              </tr>
            </thead>
            <tbody>
              {priceHistory.map((h, i) => (
                <tr key={i}>
                  <td>{h.timestamp}</td>
                  <td>{h.open}</td>
                  <td>{h.high}</td>
                  <td>{h.low}</td>
                  <td>{h.close}</td>
                  <td>{h.volume}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {history.length > 0 && (
        <div className="history-section">
          <h2>Signal History</h2>
          <table className="styled-table">
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Timestamp</th>
                <th>Buy</th>
                <th>Sell</th>
                <th>Hold</th>
                <th>Confidence</th>
                <th>Price</th>
                <th>Open</th>
                <th>High</th>
                <th>Low</th>
              </tr>
            </thead>
            <tbody>
              {history.map((h, i) => (
                <tr key={i}>
                  <td>{h.symbol}</td>
                  <td>{h.timestamp}</td>
                  <td>{h.buy_signal ? 'Yes' : 'No'}</td>
                  <td>{h.sell_signal ? 'Yes' : 'No'}</td>
                  <td>{h.hold_signal ? 'Yes' : 'No'}</td>
                  <td>{h.confidence}</td>
                  <td>{h.current_price !== undefined && h.current_price !== null ? h.current_price : 'N/A'}</td>
                  <td>{h.open_price !== undefined && h.open_price !== null ? h.open_price : 'N/A'}</td>
                  <td>{h.high_price !== undefined && h.high_price !== null ? h.high_price : 'N/A'}</td>
                  <td>{h.low_price !== undefined && h.low_price !== null ? h.low_price : 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <div className="berkshire-section">
        <h2>Berkshire Hathaway Latest 13F Holdings</h2>
        <table className="styled-table">
          <thead>
            <tr>
              <th>Symbol</th>
              <th>Name</th>
              <th>Shares</th>
              <th>% of Portfolio</th>
            </tr>
          </thead>
          <tbody>
            {berkshireHoldings.map((h, i) => (
              <tr key={i}>
                <td>{h.symbol}</td>
                <td>{h.name}</td>
                <td>{h.shares.toLocaleString()}</td>
                <td>{h.percent_portfolio}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default App;
