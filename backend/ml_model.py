# Placeholder ML model for buy/sell signal prediction
# Replace with your actual model logic and Azure ML integration

def predict_buy_sell(symbol: str, price_data: list) -> dict:
    import numpy as np
    import pandas as pd
    from sklearn.linear_model import LogisticRegression
    import random, datetime

    # If no price data, fallback to random
    if not price_data or len(price_data) < 20:
        buy_signal = random.choice([True, False])
        sell_signal = not buy_signal
        confidence = random.uniform(0.7, 0.99)
        return {
            "symbol": symbol,
            "buy_signal": buy_signal,
            "sell_signal": sell_signal,
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

    # Generate synthetic labels: buy if ma_diff > 0, sell otherwise
    df['label'] = (df['ma_diff'] > 0).astype(int)

    # Features to use
    feature_cols = [
        'pct_change', 'ma_5', 'ma_10', 'ma_20', 'ma_50',
        'bb_upper', 'bb_lower', 'rsi', 'vol_pct_change', 'ma_diff'
    ]
    # Train/test split
    X = df[feature_cols][:-1]
    y = df['label'][:-1]
    X_pred = df[feature_cols].iloc[[-1]]


    # Try to load a pre-trained model (RandomForest/XGBoost)
    import joblib
    import os
    model_path = os.path.join(os.path.dirname(__file__), 'best_model.pkl')
    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
            prob = model.predict_proba(X_pred)[0][1]
            buy_signal = prob > 0.5
            sell_signal = not buy_signal
            confidence = float(prob) if buy_signal else 1.0 - float(prob)
        except Exception:
            buy_signal = random.choice([True, False])
            sell_signal = not buy_signal
            confidence = random.uniform(0.7, 0.99)
    else:
        # Fallback: train simple logistic regression on the fly
        model = LogisticRegression()
        try:
            model.fit(X, y)
            prob = model.predict_proba(X_pred)[0][1]
            buy_signal = prob > 0.5
            sell_signal = not buy_signal
            confidence = float(prob) if buy_signal else 1.0 - float(prob)
        except Exception:
            buy_signal = random.choice([True, False])
            sell_signal = not buy_signal
            confidence = random.uniform(0.7, 0.99)

    return {
        "symbol": symbol,
        "buy_signal": buy_signal,
        "sell_signal": sell_signal,
        "confidence": confidence,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
