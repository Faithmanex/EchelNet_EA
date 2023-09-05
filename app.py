import tkinter as tk
import MetaTrader5 as mt5
import pandas as pd
import pandas_ta as ta
from datetime import datetime
import matplotlib.pyplot as plt

def update_data():
    global symbol, timeframe, label_open_close, label_tick_volume, label_symbol, label_timeframe, last_data
    
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 25)
    df = pd.DataFrame.from_records(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    df['SMA'] = ta.sma(df['close'], length=9)
    df['EMA'] = ta.ema(df['close'], length=21)
    
    if last_data is None or not last_data.equals(df):
        last_data = df
        
        label_open_close.config(text=df[['open', 'close', 'SMA', 'EMA']])
        label_tick_volume.config(text=df[['tick_volume']])
        
        if len(df) > 1 and df['SMA'].iloc[-2] < df['EMA'].iloc[-2] and df['SMA'].iloc[-1] > df['EMA'].iloc[-1]:
            label_signal.config(text="Buy Signal")
            write_signal_to_file("Buy Signal")
        elif len(df) > 1 and df['SMA'].iloc[-2] > df['EMA'].iloc[-2] and df['SMA'].iloc[-1] < df['EMA'].iloc[-1]:
            label_signal.config(text="Sell Signal")
            write_signal_to_file("Sell Signal")
        else:
            label_signal.config(text="No Signal")
    
    # Schedule the next update after 1 second
    window.after(1000, update_data)

def write_signal_to_file(signal):
    with open("Signals.txt", "a") as file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{timestamp} - {signal}\n")

def start_display():
    global symbol, timeframe
    symbol = symbol_var.get()
    update_data()

if not mt5.initialize():
    print("Failed to initialize MetaTrader5")
    exit()

symbols = mt5.symbols_get()
symbol_names = [symbol.name for symbol in symbols]

symbol = "EURUSD"
timeframe = mt5.TIMEFRAME_M1

window = tk.Tk()
window.title("MetaTrader5 Data")
window.geometry("800x600")
window.attributes("-topmost", True)

symbol_var = tk.StringVar(window)
symbol_var.set(symbol)
symbol_option = tk.OptionMenu(window, symbol_var, *symbol_names)
symbol_option.pack()

start_button = tk.Button(window, text="Start", command=start_display)
start_button.pack()

label_symbol = tk.Label(window, text="Symbol: " + symbol)
label_symbol.pack()

label_timeframe = tk.Label(window, text="Timeframe: " + str(timeframe))
label_timeframe.pack()

label_open_close = tk.Label(window, text="")
label_open_close.pack()

label_signal = tk.Label(window, text="")
label_signal.pack()

label_tick_volume = tk.Label(window, text="")
label_tick_volume.pack()

last_data = None

fig, ax = plt.subplots()

def plot_data():
    global symbol, timeframe, ax
    
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 25)
    
    if rates is not None:
        df = pd.DataFrame.from_records(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        df['SMA'] = ta.sma(df['close'], length=9)
        df['EMA'] = ta.ema(df['close'], length=21)
        
        ax.clear()
        ax.plot(df['time'], df['open'], label='Open')
        ax.plot(df['time'], df['high'], label='High')
        ax.plot(df['time'], df['low'], label='Low')
        ax.plot(df['time'], df['close'], label='Close')
        ax.plot(df['time'], df['SMA'], label='SMA')
        ax.plot(df['time'], df['EMA'], label='EMA')
        
        ax.set_xlabel('Time')
        ax.set_ylabel('Price')
        ax.set_title('OHLC and Moving Averages')
        ax.legend()
        
        plt.show()
    else:
        print("No data available.")
plot_data()

window.mainloop()

mt5.shutdown()