import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
from time import sleep

mt5.initialize()
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()

# Step 2: Subscribe to tick data
symbol = "Step Index"
mt5.symbol_select(symbol, True)


if not mt5.symbol_select(symbol, True):
    print("Failed to select symbol ", symbol)
    mt5.shutdown()
    quit()

prices = []
ema_value = 0
sma_value = 0
candles = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 1)

# Create an empty DataFrame to store the rates
df = pd.DataFrame(columns=["Time", "Open", "High", "Low", "Close", "Tick Volume", "Ask Price", "Bid Price", "Close Price"])

while mt5.positions_total:
    ticks = mt5.symbol_info_tick(symbol)


    # Display Rates
    candles = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 1, 1)
   
    if len(candles) > 0:
        open_price = candles[0][1]
        high_price = candles[0][2]
        low_price = candles[0][3]
        close_price = candles[0][4]
        tick_volume = candles[0][5]

        # Append the rates to the DataFrame
        df = df._append({
            "Time": datetime.fromtimestamp(candles[0][0]).strftime("%Y-%m-%d %H:%M:%S"),
            "Open": open_price,
            "High": high_price,
            "Low": low_price,
            "Close": close_price,
            "Tick Volume": tick_volume,
            "Ask Price": ticks.ask,
            "Bid Price": ticks.bid,
            "Close Price": close_price
        }, ignore_index=True)


#      FVG Logic
#     Question: write algorithm for finding a fair value gap using market data "OHCL" using python
#   Reference: candles = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 1, 1),         open_price = candles[0][1]
#         high_price = candles[0][2]
#         low_price = candles[0][3]
#         close_price = candles[0][4]
#         tick_volume = candles[0][5],        df = df._append({
#             "Time": datetime.fromtimestamp(candles[0][0]).strftime("%Y-%m-%d %H:%M:%S"),
#             "Open": open_price,
#             "High": high_price,
#             "Low": low_price,
#             "Close": close_price,
#             "Tick Volume": tick_volume,
#             "Ask Price": ticks.ask,
#             "Bid Price": ticks.bid,
#             "Close Price": close_price
#         }, ignore_index=True)