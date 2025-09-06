# Placeholder ML model for buy/sell signal prediction
# Replace with your actual model logic and Azure ML integration

def predict_buy_sell(symbol: str, price_data: list) -> dict:
    import numpy as np
    import pandas as pd
    from sklearn.linear_model import LogisticRegression
    import random, datetime

    # If no price data, fallback to random
    if not price_data or len(price_data) < 20:
        label = random.choice([-1, 0, 1])  # -1: sell, 0: hold, 1: buy
        buy_signal = label == 1
        sell_signal = label == -1
        hold_signal = label == 0
        confidence = None  # No real confidence available
        return {
            "symbol": symbol,
            "buy_signal": buy_signal,
            "sell_signal": sell_signal,
            "hold_signal": hold_signal,
            "confidence": confidence,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

    # Create a DataFrame from price_data
    df = pd.DataFrame(price_data)
    # Price percent change
    df['pct_change'] = df['close'].pct_change().fillna(0)
    # Moving averages
    df['ma_5'] = df['close'].rolling(window=5).mean().fillna(df['close'])
    df['ma_10'] = df['close'].rolling(window=10).mean().fillna(df['close'])
    df['ma_20'] = df['close'].rolling(window=20).mean().fillna(df['close'])
    df['ma_50'] = df['close'].rolling(window=50).mean().fillna(df['close'])
    # Bollinger Bands
    df['bb_middle'] = df['close'].rolling(window=20).mean().fillna(df['close'])
    df['bb_std'] = df['close'].rolling(window=20).std().fillna(0)
    df['bb_upper'] = df['bb_middle'] + 2 * df['bb_std']
    df['bb_lower'] = df['bb_middle'] - 2 * df['bb_std']
    # RSI (Relative Strength Index)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().fillna(0)
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().fillna(0)
    rs = gain / (loss + 1e-6)
    df['rsi'] = 100 - (100 / (1 + rs))
    # Volume percent change
    df['vol_pct_change'] = df['volume'].pct_change().fillna(0)
    # Feature: short vs long MA
    df['ma_diff'] = df['ma_5'] - df['ma_20']

    # Use trained model for prediction and confidence if available
    import joblib
    import os
    model_path = os.path.join(os.path.dirname(__file__), 'best_model.pkl')
    feature_cols = [
        'pct_change', 'ma_5', 'ma_10', 'ma_20', 'ma_50',
        'bb_upper', 'bb_lower', 'rsi', 'vol_pct_change', 'ma_diff'
    ]
    X_pred = df[feature_cols].iloc[[-1]]
    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
            proba = model.predict_proba(X_pred)[0]
            pred_label = model.predict(X_pred)[0]
            last_label = int(pred_label)
            confidence = proba[model.classes_.tolist().index(last_label)]
        except Exception:
            # fallback: use ma_diff
            if df['ma_diff'].iloc[-1] > 0.01:
                last_label = 1
            elif df['ma_diff'].iloc[-1] < -0.01:
                last_label = -1
            else:
                last_label = 0
            confidence = 0
    else:
        # fallback: use ma_diff
        if df['ma_diff'].iloc[-1] > 0.01:
            last_label = 1
        elif df['ma_diff'].iloc[-1] < -0.01:
            last_label = -1
        else:
            last_label = 0
        confidence = 0
    buy_signal = last_label == 1
    sell_signal = last_label == -1
    hold_signal = last_label == 0

    return {
        "symbol": symbol,
        "buy_signal": buy_signal,
        "sell_signal": sell_signal,
        "hold_signal": hold_signal,
        "confidence": confidence,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
