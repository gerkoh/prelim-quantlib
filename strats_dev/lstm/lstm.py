import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Input, Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from typing import Tuple, List
import json
import os

# Load and preprocess the data from JSON file
def load_and_preprocess_data(timeframe: str, ticker: str) -> pd.DataFrame:
    file_path = f"data/etfs/{timeframe}/{ticker}.json"
    with open(file_path, 'r') as f:
        data = json.load(f)
    # Convert JSON to DataFrame and filter relevant columns
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df = df[['date', 'close', 'volume']].sort_values('date')
    print(df.head)
    return df

# Normalize data
def normalize_data(data: pd.DataFrame) -> Tuple[np.ndarray, MinMaxScaler]:
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data[['close', 'volume']])
    return scaled_data, scaler

# Generate sequences for LSTM
def create_sequences(data: np.ndarray, seq_length: int) -> Tuple[List[np.ndarray], List[float]]:
    X, y = [], []
    for i in range(seq_length, len(data)):
        X.append(data[i-seq_length:i])
        y.append(data[i, 0])  # Close price as target
    return np.array(X), np.array(y)

# Split data into train and validation sets
def split_data(X: np.ndarray, y: np.ndarray, train_size: float=0.9) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    train_size = int(len(X) * train_size)
    return X[:train_size], X[train_size:], y[:train_size], y[train_size:]

# Define the LSTM model
def create_lstm_model(input_shape: Tuple[int, int]) -> Sequential:
    model = Sequential([
        Input(shape=input_shape),
        LSTM(50, return_sequences=True),
        Dropout(0.2),
        LSTM(50, return_sequences=False),
        Dropout(0.2),
        Dense(25),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

# Main function to run the model, save it, and plot results
def run_model(timeframe: str, ticker: str):
    # Step 1: Load and preprocess data
    data = load_and_preprocess_data(timeframe, ticker)
    scaled_data, scaler = normalize_data(data)
    
    # Step 2: Create sequences for LSTM
    seq_length = 60
    X, y = create_sequences(scaled_data, seq_length)
    
    # Step 3: Split data
    X_train, X_val, y_train, y_val = split_data(X, y, train_size=0.9)
    
    # Step 4: Define and train the model
    model = create_lstm_model((X_train.shape[1], X_train.shape[2]))
    model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=50, batch_size=32)
    
    # Step 5: Save the model
    model_dir = "models"
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, f"{ticker}_{timeframe}_lstm_model.h5")
    model.save(model_path)
    print(f"Model saved to {model_path}")
    
    # Step 6: Make predictions
    predictions = model.predict(X_val)
    predictions = scaler.inverse_transform(np.hstack((predictions, np.zeros((predictions.shape[0], 1)))))[:, 0]
    actual_prices = scaler.inverse_transform(np.hstack((y_val.reshape(-1, 1), np.zeros((y_val.shape[0], 1)))))[:, 0]
    
    # Step 7: Plot predictions vs actual prices
    plt.figure(figsize=(14, 5))
    plt.plot(data['date'][-len(y_val):], actual_prices, color='blue', label='Actual Price')
    plt.plot(data['date'][-len(y_val):], predictions, color='red', label='Predicted Price')
    plt.xlabel('Date')
    plt.ylabel('Close Price')
    plt.legend()
    plt.title(f'LSTM Model - Actual vs Predicted Close Price for {ticker}')
    plt.show()

# Run the model with specific timeframe and ticker
# Example usage: run_model('daily', 'SPY')
run_model('1d', 'SPY')