import time
import yfinance as yf
import pandas as pd
import threading

# Function to calculate RSI
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


def rsi_alert(stock_symbol):
    # with lock:
    #     print("Fetching data for", stock_symbol)
    while True:
        with lock:
            stock_data = yf.download(stock_symbol, period='1d', interval='1m', progress=False)

        # Ensure data was fetched
        if not stock_data.empty:
            # Calculate RSI
            stock_data['RSI'] = compute_rsi(stock_data['Close'])

            # Interpret RSI signals
            stock_data['RSI_Signal'] = interpret_rsi(stock_data['RSI'])

            # Display the latest part of the data frame

            if stock_data['RSI_Signal'][-1] == 'Hold':
                pass
            else:
                with lock:
                    print(stock_symbol[:-3], stock_data['RSI_Signal'][-1])  # Adjust as needed
        else:
            with lock:
                print(f"No data fetched for {stock_symbol}")
            return
        time.sleep(60)  # Wait for 1 minute before fetching the next data

lock = threading.Lock()
if __name__ == "__main__":
    # Create a thread for each stock
    threads = []
    top_by_volume = pd.read_csv('top_by_volume.csv')
    for stock in top_by_volume['SYMBOL \n']:
        t = threading.Thread(target=rsi_alert, args=(stock + ".NS",))
        threads.append(t)
        t.start()
        time.sleep(2)

    for t in threads:
        t.join()