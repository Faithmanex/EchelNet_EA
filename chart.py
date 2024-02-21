import datetime as dt
import pandas as pd
import MetaTrader5 as mt5
import time

def preprocess_mt5_live(symbol, mt5, time_frame=mt5.TIMEFRAME_H1):
    """Fetches the latest available data and continues updating as new data arrives."""

    df_rates = pd.DataFrame()

    while True:
        ticks = mt5.copy_ticks_from(symbol, dt.datetime.now() - dt.timedelta(minutes=30), 1000, mt5.COPY_TICKS_ALL)
        ticks_frame = pd.DataFrame(ticks)
        ticks_frame['time'] = pd.to_datetime(ticks_frame['time'], unit='s')     

        df_rates = df_rates.append(ticks_frame, ignore_index=True) 
        df_rates["symbol"] = symbol

        # Basic analysis example: Calculate rolling mean 
        df_rates['rolling_mean'] = df_rates['close'].rolling(window=10).mean()
        print("Latest Rolling Mean:", df_rates['rolling_mean'].iloc[-1])

        time.sleep(5)  

# Initialize MetaTrader5 connection
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

sym = "EURUSD"
preprocess_mt5_live(symbol=sym, mt5=mt5) 
