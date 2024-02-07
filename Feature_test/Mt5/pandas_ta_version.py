import pandas as pd
import pandas_ta as ta
import MetaTrader5 as mt5
import time
import winsound

# Import necessary libraries
import pandas_ta as ta
import pandas as pd

# Initialize MetaTrader
mt5.initialize()



# Define variables
period = 14
fast_ma_period = 14
slow_ma_period = 28

# Select a symbol
symbol = "Step Index"

def play_error_sound():
    # Play Windows exit sound
    winsound.PlaySound("SystemExit", winsound.SND_ALIAS)

play_error_sound()
# Call the function to play the error sound

# Create an empty dataframe to store rates and moving averages
df = pd.DataFrame(columns=["Time", "Open", "High", "Low", "Close", "Fast MA", "Slow MA"])

# Loop to copy live rates for OHLC from the symbol
while True:
    # Get the latest rates
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 1, 1)
    
    # Get the latest rate
    rate = rates[0]
    
    
    # Append the rate to the dataframe
    df = df._append({
        "Time": pd.to_datetime(rate[0], unit="s"),
        "Open": rate[1],
        "High": rate[2],
        "Low": rate[3],
        "Close": rate[4]
    }, ignore_index=True)
    
    # Calculate moving averages
    if len(df) >= slow_ma_period:
        df["Fast MA"] = ta.sma(df["Close"], length=fast_ma_period)
        df["Slow MA"] = ta.sma(df["Close"], length=slow_ma_period)
    
    # Check for crossover signal
    if len(df) >= slow_ma_period + 1:
        if df["Fast MA"].iloc[-2] < df["Slow MA"].iloc[-2] and df["Fast MA"].iloc[-1] > df["Slow MA"].iloc[-1]:
            print("Buy signal")
            play_error_sound()
        elif df["Fast MA"].iloc[-2] > df["Slow MA"].iloc[-2] and df["Fast MA"].iloc[-1] < df["Slow MA"].iloc[-1]:
            print("Sell signal")
            play_error_sound()
    
    print(df)
    
    # Wait for the next tick
    time.sleep(1)
