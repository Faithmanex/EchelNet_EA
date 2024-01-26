import MetaTrader5 as mt5

def connect_to_mt5():
    # Connect to MetaTrader 5
    mt5.initialize()

def disconnect_from_mt5():
    # Disconnect from MetaTrader 5
    mt5.shutdown()

def get_historical_data(symbol, timeframe, num_bars):
    # Retrieve historical data
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_bars)
    return rates

def detect_spikes(rates):
    # Extract closing prices
    close_prices = [bar['close'] for bar in rates]

    # Implement your spike detection logic
    # Example: Identify a spike if the current close price is significantly higher than the previous close price
    for i in range(1, len(close_prices)):
        if close_prices[i] > 1.05 * close_prices[i - 1]:
            print(f"Spike detected at {rates[i]['time']}")

# Main program
if __name__ == "__main__":
    try:
        # Connect to MetaTrader 5
        connect_to_mt5()

        # Symbol for Range Break 100 Index (replace with the actual symbol)
        symbol = "Range Break 100 Index"

        # Specify the timeframe (e.g., M1, M5, H1, etc.)
        timeframe = mt5.TIMEFRAME_M1

        # Specify the number of bars to retrieve
        num_bars = 1000

        # Retrieve historical data
        historical_data = get_historical_data(symbol, timeframe, num_bars)

        # Detect spikes
        detect_spikes(historical_data)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Disconnect from MetaTrader 5
        disconnect_from_mt5()
