import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

# Choose your stock symbol
stock_symbol = 'RELIANCE.NS'  # Example with Apple Inc.

# Fetch data for today
today = datetime.now().date()
print(f"Fetching data for {stock_symbol} on {today}...")
start_date = today - timedelta(days=1)  # Adjust based on market opening days
end_date = today + timedelta(days=1)  # Adjust to ensure today's data is included

# Load stock data
data = yf.download(stock_symbol, start=start_date, end=end_date, interval="1m")  # '1m' for minute-level data

# Check if data is empty (market might be closed)
if data.empty:
    print("No data available for today. The market might be closed.")
else:
    # Plot today's price
    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['Close'], label=f'{stock_symbol} Today\'s Price')
    plt.title(f'{stock_symbol} Stock Price for Today')
    plt.xlabel('Time')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)  # Rotate date labels for better readability
    plt.tight_layout()
    plt.show()


def compute_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)

    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

data['RSI'] = compute_rsi(data['Close'])

# Plot RSI
if not data.empty:
    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['RSI'], label=f'{stock_symbol} RSI')
    plt.title(f'{stock_symbol} RSI for Today')
    plt.xlabel('Time')
    plt.ylabel('RSI')
    plt.axhline(30, color='r', linestyle='--')
    plt.axhline(70, color='r', linestyle='--')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)  # Rotate date labels for better readability
    plt.tight_layout()
    plt.show()
else:
    print("No data available for today. The market might be closed.")

