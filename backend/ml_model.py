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
    # Example features: percent change, rolling mean, etc.
    df['pct_change'] = df['close'].pct_change().fillna(0)
    df['ma_5'] = df['close'].rolling(window=5).mean().fillna(df['close'])
    df['ma_20'] = df['close'].rolling(window=20).mean().fillna(df['close'])
    df['feature'] = df['ma_5'] - df['ma_20']

    # Generate synthetic labels: buy if feature > 0, sell otherwise
    df['label'] = (df['feature'] > 0).astype(int)

    # Train/test split
    X = df[['pct_change', 'feature']][:-1]
    y = df['label'][:-1]
    X_pred = df[['pct_change', 'feature']].iloc[[-1]]

    # Train simple logistic regression
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
