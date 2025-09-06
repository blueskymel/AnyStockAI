
import yfinance as yf
import pandas as pd
import json
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file (if present)
load_dotenv()

# Load ASX symbols from the frontend public directory

# --- API KEYS ---
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
EODHD_API_KEY = os.getenv('EODHD_API_KEY')

SYMBOLS_PATH = os.path.join(os.path.dirname(__file__), '../frontend/public/asx_symbols.json')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'training_data.csv')

with open(SYMBOLS_PATH, 'r') as f:
    symbols = json.load(f)

all_data = []

for symbol in symbols:
    ticker = symbol if symbol.endswith('.AX') else symbol + '.AX'
    print(f"Downloading {ticker}...")
    try:
        # Try yfinance first
        data = yf.download(ticker, period="5y")
        # Flatten MultiIndex columns if present (e.g., ('Close', 'WTC.AX') -> 'Close')
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0] for col in data.columns]
            print(f"{ticker}: yfinance columns flattened: {list(data.columns)}")
        print(f"{ticker}: yfinance columns: {list(data.columns)}")
        print(f"{ticker}: yfinance head:\n{data.head()}\n")
        if data.empty:
            print(f"{ticker}: No data from yfinance. Trying Alpha Vantage...")
            # Try Alpha Vantage
            av_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&outputsize=full&apikey={ALPHA_VANTAGE_API_KEY}'
            av_resp = requests.get(av_url)
            av_json = av_resp.json()
            if 'Time Series (Daily)' in av_json:
                av_df = pd.DataFrame.from_dict(av_json['Time Series (Daily)'], orient='index').sort_index()
                av_df = av_df.rename(columns={
                    '1. open': 'Open',
                    '2. high': 'High',
                    '3. low': 'Low',
                    '4. close': 'Close',
                    '5. adjusted close': 'Adj Close',
                    '6. volume': 'Volume',
                })
                av_df = av_df[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
                av_df.index = pd.to_datetime(av_df.index)
                av_df = av_df.sort_index()
                print(f"{ticker}: Alpha Vantage columns: {list(av_df.columns)}")
                print(f"{ticker}: Alpha Vantage head:\n{av_df.head()}\n")
                df = av_df.reset_index().rename(columns={'index': 'Date'})
            else:
                print(f"{ticker}: No data from Alpha Vantage. Trying EODHD...")
                # Try EODHD
                eod_url = f'https://eodhistoricaldata.com/api/eod/{ticker}?fmt=json&api_token={EODHD_API_KEY}&period=d&from=2010-01-01'
                eod_resp = requests.get(eod_url)
                if eod_resp.status_code == 200:
                    eod_json = eod_resp.json()
                    if isinstance(eod_json, list) and len(eod_json) > 0:
                        eod_df = pd.DataFrame(eod_json)
                        eod_df = eod_df.rename(columns={
                            'open': 'Open',
                            'high': 'High',
                            'low': 'Low',
                            'close': 'Close',
                            'volume': 'Volume',
                        })
                        eod_df = eod_df[['Open', 'High', 'Low', 'Close', 'Volume', 'date']]
                        eod_df['date'] = pd.to_datetime(eod_df['date'])
                        eod_df = eod_df.sort_values('date')
                        print(f"{ticker}: EODHD columns: {list(eod_df.columns)}")
                        print(f"{ticker}: EODHD head:\n{eod_df.head()}\n")
                        df = eod_df.rename(columns={'date': 'Date'}).reset_index(drop=True)
                    else:
                        print(f"{ticker}: No data from EODHD.")
                        continue
                else:
                    print(f"{ticker}: No data from EODHD (HTTP {eod_resp.status_code}).")
                    continue
        else:
            df = data.reset_index()
        # Check for required raw columns
        required_raw_cols = ['Close', 'Volume']
        if not all(col in df.columns for col in required_raw_cols):
            print(f"{ticker}: Missing required raw columns: {[col for col in required_raw_cols if col not in df.columns]}")
            continue
        # Check for minimum length (largest rolling window is 50)
        if len(df) < 55:
            print(f"{ticker}: Not enough data points ({len(df)}) for feature engineering. Skipping.")
            continue
        df['pct_change'] = df['Close'].pct_change().fillna(0)
        df['ma_5'] = df['Close'].rolling(window=5).mean().fillna(df['Close'])
        df['ma_10'] = df['Close'].rolling(window=10).mean().fillna(df['Close'])
        df['ma_20'] = df['Close'].rolling(window=20).mean().fillna(df['Close'])
        df['ma_50'] = df['Close'].rolling(window=50).mean().fillna(df['Close'])
        df['bb_middle'] = df['Close'].rolling(window=20).mean().fillna(df['Close'])
        df['bb_std'] = df['Close'].rolling(window=20).std().fillna(0)
        df['bb_upper'] = df['bb_middle'] + 2 * df['bb_std']
        df['bb_lower'] = df['bb_middle'] - 2 * df['bb_std']
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().fillna(0)
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().fillna(0)
        rs = gain / (loss + 1e-6)
        df['rsi'] = 100 - (100 / (1 + rs))
        df['vol_pct_change'] = df['Volume'].pct_change().fillna(0)
        df['ma_diff'] = df['ma_5'] - df['ma_20']
        # Smart labeling: future returns and simulated trades
        N = 5  # lookahead days
        PROFIT_THRESHOLD = 0.03  # +3%
        LOSS_THRESHOLD = -0.03   # -3%
        future_close = df['Close'].shift(-N)
        future_return = (future_close - df['Close']) / df['Close']
        # Drop NaNs from features before labeling
        feature_cols_no_label = [
            'pct_change', 'ma_5', 'ma_10', 'ma_20', 'ma_50',
            'bb_upper', 'bb_lower', 'rsi', 'vol_pct_change', 'ma_diff'
        ]
        df = df.dropna(subset=feature_cols_no_label)
        def smart_label(ret):
            try:
                # If ret is a Series, take the first value or return 0
                if isinstance(ret, pd.Series):
                    print(f"Label error for {ticker}: ret is a Series, using first value.")
                    ret = ret.iloc[0] if not ret.empty else 0
                if ret > PROFIT_THRESHOLD:
                    return 1  # buy
                elif ret < LOSS_THRESHOLD:
                    return -1  # sell
                else:
                    return 0  # hold
            except Exception as e:
                print(f"Label error for {ticker}: ret={ret}, error={e}")
                return 0
        df['label'] = future_return.apply(smart_label)
        df['symbol'] = symbol
        feature_cols = [
            'symbol', 'pct_change', 'ma_5', 'ma_10', 'ma_20', 'ma_50',
            'bb_upper', 'bb_lower', 'rsi', 'vol_pct_change', 'ma_diff', 'label'
        ]
        # Check for missing columns
        missing_cols = [col for col in feature_cols if col not in df.columns]
        if missing_cols:
            print(f"Error downloading {ticker}: {missing_cols}")
            continue
        # Drop NaNs from label after labeling
        clean_df = df[feature_cols].dropna(subset=['label'])
        print(f"{ticker}: clean_df shape: {clean_df.shape}")
        if clean_df.empty:
            print(f"{ticker}: No usable data after feature engineering and labeling.")
        else:
            all_data.append(clean_df)
    except Exception as e:
        print(f"Error downloading {ticker}: {e}")

if all_data:
    result = pd.concat(all_data, ignore_index=True)
    # Final safeguard: drop any rows with NaN in features or label
    result = result.dropna()
    if result.empty:
        print("No usable data after concatenation and NaN removal.")
    else:
        result.to_csv(OUTPUT_PATH, index=False)
        print(f"Saved training data to {OUTPUT_PATH}")
else:
    print("No data downloaded.")
