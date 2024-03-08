from flask import Flask, render_template, jsonify
import time
import yfinance as yf
import pandas as pd
import threading



# Functions to calculate RSI
import pandas as pd

def compute_sma(data, window=14):
    """Compute the Simple Moving Average."""
    return data.rolling(window=window, min_periods=1).mean()

def compute_rsi_with_sma(data, rsi_window=14, sma_window=14):
    """Compute the RSI and its SMA."""
    delta = data.diff()
    gain = (delta.clip(lower=0)).fillna(0)
    loss = (-delta.clip(upper=0)).fillna(0)

    avg_gain = gain.rolling(window=rsi_window, min_periods=1).mean()
    avg_loss = loss.rolling(window=rsi_window, min_periods=1).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    # Compute SMA of RSI
    rsi_sma = compute_sma(rsi, window=sma_window)

    return rsi_sma

def compute_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.clip(lower=0)).fillna(0)
    loss = (-delta.clip(upper=0)).fillna(0)

    avg_gain = gain.rolling(window, min_periods=1).mean()
    avg_loss = loss.rolling(window, min_periods=1).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


# Function to interpret RSI for buy or sell signals
def interpret_rsi(rsi_series):
    signals = []
    for value in rsi_series:
        if value > 70:
            signals.append('Sell')  # Overbought condition
        elif value < 30:
            signals.append('Buy')  # Oversold condition
        else:
            signals.append('Hold')
    return signals

app = Flask(__name__)

# Initialize a global dictionary to store stock signals
stock_signals = {}


# Modify your rsi_alert function or create a new one to update stock_signals
def rsi_alert(stock_symbol):
    global stock_signals  # Access the global dictionary
    while True:
        with lock:
            stock_data = yf.download(stock_symbol, period='1d', interval='1m', progress=False)
        # Update the stock_signals dictionary instead of printing
        if not stock_data.empty:
            stock_data['RSI'] = compute_rsi_with_sma(stock_data['Close'])

            # Interpret RSI signals
            stock_data['RSI_Signal'] = interpret_rsi(stock_data['RSI'])

            last_price = stock_data['Close'].iloc[-1]  # Get the latest closing price
            last_rsi = stock_data['RSI'].iloc[-1]
            signal = stock_data['RSI_Signal'][-1]
            with lock:
                print(stock_symbol[:-3], last_price, signal, last_rsi)
            # Update the stock_signals dictionary
            with lock:
                stock_signals[stock_symbol[:-3]] = {
                    'price': round(last_price, 2),
                    'rsi': round(last_rsi, 2),
                    'signal': signal
                }
        else:
            return
        time.sleep(60)  # Check the interval based on your requirements


@app.route('/')
def index():
    # Here, instead of just jsonify, you render the template which will use AJAX to fetch the data
    return render_template('index.html')

@app.route('/signals')
def signals():
    # This new endpoint is used to fetch the signals as JSON for the AJAX call in your HTML
    return jsonify(stock_signals)



lock = threading.Lock()

if __name__ == "__main__":
    threads = []
    top_by_volume = pd.read_csv('static/nifty100.csv')
    for stock in top_by_volume['Symbol']:
        t = threading.Thread(target=rsi_alert, args=(stock + ".NS",))
        threads.append(t)
        t.start()
        print(f"Thread Started for for {stock}")
        time.sleep((60-1)/len(top_by_volume['Symbol']))

    # Start the Flask application
    app.run(host='0.0.0.0', port=5460, debug=True, use_reloader=False)

    for t in threads:
        t.join()