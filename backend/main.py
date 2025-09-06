


# --- Imports ---
from fastapi import FastAPI, Query, Depends, WebSocket, WebSocketDisconnect, Body
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from db import SessionLocal, StockSignal
from pydantic import BaseModel
from typing import List, Optional
import smtplib
import requests

# --- App Initialization ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Models ---
class SignalResponse(BaseModel):
    symbol: str
    buy_signal: bool
    sell_signal: bool
    hold_signal: bool
    confidence: Optional[float] = None
    timestamp: str
    current_price: float = None
    open_price: float = None
    high_price: float = None
    low_price: float = None

# --- DB Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- WebSocket manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

# --- Endpoints ---
@app.get("/predict", response_model=SignalResponse)
def predict_signal(symbol: str = Query(..., description="ASX stock symbol")):
    from ml_model import predict_buy_sell
    import yfinance as yf
    ticker = symbol if symbol.endswith('.AX') else symbol + '.AX'
    data = yf.Ticker(ticker)
    price = None
    open_price = None
    high_price = None
    low_price = None
    try:
        hist = data.history(period="1d")
        if hist.empty:
            raise ValueError("No data found for symbol")
        price = hist['Close'].iloc[-1]
        open_price = hist['Open'].iloc[-1]
        high_price = hist['High'].iloc[-1]
        low_price = hist['Low'].iloc[-1]
    except Exception:
        raise HTTPException(status_code=404, detail=f"Stock symbol '{symbol}' not found or has no data.")
    # Fetch last 1 year of price data for ML model
    price_data = []
    try:
        hist_long = data.history(period="1y")
        for idx, row in hist_long.iterrows():
            price_data.append({
                "timestamp": idx.isoformat(),
                "open": row["Open"],
                "high": row["High"],
                "low": row["Low"],
                "close": row["Close"],
                "volume": row["Volume"]
            })
    except Exception:
        price_data = []
    result = predict_buy_sell(symbol, price_data)
    response = SignalResponse(**result, current_price=price, open_price=open_price, high_price=high_price, low_price=low_price)
    # Store in DB
    db = next(get_db())
    import datetime
    signal = StockSignal(
        symbol=symbol,
        buy_signal=int(response.buy_signal),
        sell_signal=int(response.sell_signal),
        hold_signal=int(response.hold_signal),
        confidence=response.confidence,
        timestamp=datetime.datetime.fromisoformat(response.timestamp),
        current_price=price,
        open_price=open_price,
        high_price=high_price,
        low_price=low_price
    )
    db.add(signal)
    db.commit()
    db.refresh(signal)
    # Broadcast to WebSocket clients
    import asyncio
    try:
        asyncio.create_task(manager.broadcast(response.dict()))
    except Exception:
        pass
    return response

# --- Signal History Endpoint ---
@app.get("/signal_history")
def get_signal_history(symbol: str):
    db = next(get_db())
    signals = db.query(StockSignal).filter(StockSignal.symbol == symbol).order_by(StockSignal.timestamp.desc()).all()
    history = []
    for s in signals:
        history.append({
            "symbol": s.symbol,
            "timestamp": s.timestamp.isoformat() if s.timestamp else None,
            "buy_signal": bool(s.buy_signal),
            "sell_signal": bool(s.sell_signal),
            "hold_signal": bool(s.hold_signal) if hasattr(s, 'hold_signal') else False,
            "confidence": s.confidence,
            "current_price": s.current_price,
            "open_price": s.open_price,
            "high_price": s.high_price,
            "low_price": s.low_price
        })
    return {"symbol": symbol, "history": history}

@app.get("/history")
def get_history(symbol: str):
    import yfinance as yf
    ticker = symbol if symbol.endswith('.AX') else symbol + '.AX'
    data = yf.download(ticker, period="1y")
    history = []
    for idx, row in data.iterrows():
        history.append({
            "timestamp": idx.isoformat(),
            "open": row["Open"],
            "high": row["High"],
            "low": row["Low"],
            "close": row["Close"],
            "volume": row["Volume"]
        })
    return {"symbol": symbol, "history": history}

@app.websocket("/ws/signals")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    from db import Base, engine
    Base.metadata.create_all(bind=engine)
