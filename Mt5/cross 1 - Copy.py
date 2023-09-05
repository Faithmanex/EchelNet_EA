# Import the necessary modules
import MetaTrader5 as mt5
import pandas as pd
import numpy as np

# Initialize connection to MetaTrader 5 terminal
if not mt5.initialize():
    print("Failed to connect to MetaTrader 5 terminal")
    quit()

# Define the asset symbol
symbol = 'XAUUSD'

# Get the last 100 bars of daily data for the asset
bars = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 999)

# Check if bars is None
if bars is None:
    print(f"Failed to get bars for symbol {symbol}")
    mt5.shutdown()
    quit()

# Convert the bars to a pandas DataFrame
data = pd.DataFrame(bars)

# Convert the time seconds to a datetime object
data['time'] = pd.to_datetime(data['time'], unit='s')

# Set time as index
data.set_index('time', inplace=True)

# Calculate the EMA
data['9_EMA'] = data['close'].ewm(span=9).mean()
data['21_EMA'] = data['close'].ewm(span=21).mean()
data['55_EMA'] = data['close'].ewm(span=55).mean()

# Implement the strategy logic
data['Buy_Signal'] = (data['9_EMA'] > data['21_EMA']) & (data['21_EMA'] > data['55_EMA'])
data['Sell_Signal'] = (data['9_EMA'] < data['21_EMA']) & (data['21_EMA'] < data['55_EMA'])

# Calculate profit or loss for each trade
data['Profit_or_Loss'] = np.where(data['Buy_Signal'], data['close'].shift(-1) - data['close'], 0)
data['Profit_or_Loss'] = np.where(data['Sell_Signal'], data['close'] - data['close'].shift(-1), data['Profit_or_Loss'])

# Calculate net profit
net_profit = data['Profit_or_Loss'].sum()

# Calculate number of wins and losses
num_wins = (data['Profit_or_Loss'] > 0).sum()
num_losses = (data['Profit_or_Loss'] < 0).sum()

# Print the results
print(f"Net Profit: {net_profit}")
print(f"Number of Wins: {num_wins}")
print(f"Number of Losses: {num_losses}")

# Shut down the connection to the MetaTrader 5 terminal
mt5.shutdown()
