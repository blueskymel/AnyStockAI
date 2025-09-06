import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os
import subprocess

# Load your historical price data here (CSV, DB, or API)
# For demo, we'll expect a CSV file with all features already computed
DATA_PATH = 'training_data.csv'  # You must generate this file with your feature engineering pipeline
MODEL_PATH = 'best_model.pkl'

# Always fetch new data before training
subprocess.run(['python', 'generate_training_data.py'], check=True)

# Load data
df = pd.read_csv(DATA_PATH)

# Replace infinity values with NA and drop rows with NA
df.replace([float('inf'), float('-inf')], pd.NA, inplace=True)
df = df.dropna()

# Features and label
feature_cols = [
    'pct_change', 'ma_5', 'ma_10', 'ma_20', 'ma_50',
    'bb_upper', 'bb_lower', 'rsi', 'vol_pct_change', 'ma_diff'
]
y = df['label']
# Ensure all features are float
X = df[feature_cols].astype(float)
y = df['label']
# For XGBoost, map labels: -1 -> 0, 0 -> 1, 1 -> 2
y_xgb = y.map({-1: 0, 0: 1, 1: 2})

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define models and parameter grids
models = {
    'RandomForest': (RandomForestClassifier(), {
        'n_estimators': [50, 100],
        'max_depth': [3, 5, 10],
        'min_samples_split': [2, 5]
    }),
    'XGBoost': (XGBClassifier(eval_metric='logloss', use_label_encoder=False), {
        'n_estimators': [50, 100],
        'max_depth': [3, 5, 10],
        'learning_rate': [0.01, 0.1]
    })
}

best_score = 0
best_model = None
best_name = ''

for name, (model, params) in models.items():
    print(f'Training {name}...')
    # Use mapped labels for XGBoost, original for RandomForest
    if name == 'XGBoost':
        grid = GridSearchCV(model, params, cv=3, scoring='accuracy', n_jobs=-1)
        grid.fit(X_train, y_xgb.loc[X_train.index])
    else:
        grid = GridSearchCV(model, params, cv=3, scoring='accuracy', n_jobs=-1)
        grid.fit(X_train, y_train)
    score = grid.best_score_
    print(f'{name} best CV score: {score:.4f}')
    if score > best_score:
        best_score = score
        best_model = grid.best_estimator_
        best_name = name

# Evaluate on test set
if best_model is not None:
    # For XGBoost, map test labels as well
    if best_name == 'XGBoost':
        y_test_eval = y_xgb.loc[X_test.index]
    else:
        y_test_eval = y_test
    y_pred = best_model.predict(X_test)
    acc = accuracy_score(y_test_eval, y_pred)
    print(f'Best model: {best_name} | Test accuracy: {acc:.4f}')
    joblib.dump(best_model, MODEL_PATH)
    print(f'Model saved to {MODEL_PATH}')
else:
    print('No model trained.')
