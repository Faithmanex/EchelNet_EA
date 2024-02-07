# Import necessary libraries
import pandas as pd
import numpy as np
import MetaTrader5 as mt5

# Initialize MetaTrader 5
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()

# Define the symbol and fetch the OHLC data
symbol = "Step Index"
rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 30)

# Create a pandas DataFrame from the fetched data
df = pd.DataFrame(rates)
df['time']=pd.to_datetime(df['time'], unit='s')

# Function to calculate Fair Value Gaps (FVG)
def calculate_fvg(df, min_gap):
    df['fvg_bull'] = df['low'] - df['high'].shift(2)
    df['fvg_bull_pct'] = ((df['fvg_bull'] / df['close']) * 100)
    
    df['fvg_bear'] =  df['low'].shift(2) - df['high']
    df['fvg_bear_pct'] = ((df['fvg_bear'] / df['close']) * -100)
    
    df['fvg_bull'] = df['fvg_bull'].where(df['fvg_bull'] > min_gap, None)
    df['fvg_bear'] = df['fvg_bear'].where(df['fvg_bear'] > min_gap, None)
    
    df['fvg'] = df['fvg_bull'].fillna(df['fvg_bear'])
    df['fvg_pct'] = df['fvg_bull_pct'].fillna(df['fvg_bear_pct'])
    
    return df

# Set the minimum gap size (1% in this case)
min_gap = 0.01 

# Calculate the FVG
df = calculate_fvg(df, min_gap)

# Shut down the connection to the MetaTrader 5 terminal
mt5.shutdown()
