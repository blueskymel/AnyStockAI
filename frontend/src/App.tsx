import React, { useState } from 'react';
import { useEffect } from 'react';
// import connection from './signalr';
// Load backend URL from config
import backendConfig from './config';

function App() {
  const [symbol, setSymbol] = useState('');
  const [signal, setSignal] = useState<any>(null);
  const [realtimeSignal, setRealtimeSignal] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  // priceHistory is for Yahoo Finance historical prices, not signal history
  const [priceHistory, setPriceHistory] = useState<any[]>([]);
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

  return (
    <div>
      <h1>AnyStockAI: ASX Tracker</h1>
      <input value={symbol} onChange={e => setSymbol(e.target.value)} placeholder="ASX Symbol" />
      <button onClick={fetchSignal}>Get Signal</button>
      <button onClick={fetchHistory} style={{marginLeft: '1em'}}>Show History</button>
      {signal && (
        <div>
          <p>Buy: {signal.buy_signal ? 'Yes' : 'No'}</p>
          <p>Sell: {signal.sell_signal ? 'Yes' : 'No'}</p>
          <p>Confidence: {signal.confidence}</p>
          <p>Current Price: {signal.current_price !== undefined && signal.current_price !== null ? signal.current_price : 'N/A'}</p>
          <p>Open Price: {signal.open_price !== undefined && signal.open_price !== null ? signal.open_price : 'N/A'}</p>
          <p>High Price: {signal.high_price !== undefined && signal.high_price !== null ? signal.high_price : 'N/A'}</p>
          <p>Low Price: {signal.low_price !== undefined && signal.low_price !== null ? signal.low_price : 'N/A'}</p>
        </div>
      )}
      {realtimeSignal && (
        <div style={{background: '#e0ffe0', marginTop: '1em', padding: '1em'}}>
          <h2>Real-Time Signal Update</h2>
          <p>Symbol: {realtimeSignal.symbol}</p>
          <p>Buy: {realtimeSignal.buy_signal ? 'Yes' : 'No'}</p>
          <p>Sell: {realtimeSignal.sell_signal ? 'Yes' : 'No'}</p>
          <p>Confidence: {realtimeSignal.confidence}</p>
          <p>Current Price: {realtimeSignal.current_price !== undefined && realtimeSignal.current_price !== null ? realtimeSignal.current_price : 'N/A'}</p>
          <p>Timestamp: {realtimeSignal.timestamp}</p>
        </div>
      )}
      {priceHistory.length > 0 && (
        <div style={{marginTop: '2em'}}>
          <h2>Historical Price Data (Yahoo Finance)</h2>
          <table border={1} cellPadding={6}>
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
        <div style={{marginTop: '2em'}}>
          <h2>Signal History</h2>
          <table border={1} cellPadding={6}>
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Timestamp</th>
                <th>Buy</th>
                <th>Sell</th>
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
    </div>
  );
}

export default App;
