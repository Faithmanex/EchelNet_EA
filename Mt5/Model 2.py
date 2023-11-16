import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
from time import sleep
import subprocess
import pytz

# Step 1: Connect to the MetaTrader terminal
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

# Step 3: Calculate and print EMA on every tick
ema_period = 20
sma_period = 7
prices = []
ema_value = 0
sma_value = 0
candles = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 1)
# Create an empty DataFrame to store the rates
df = pd.DataFrame(columns=["Time", "Open", "High", "Low", "Close", "Tick Volume", "EMA", "SMA", "Ask Price", "Bid Price", "Close Price"])

while mt5.positions_total:
    ticks = mt5.symbol_info_tick(symbol)
    
    if ticks is not None:
        prices.append(ticks.bid)

        if len(prices) >= ema_period:
            ema = pd.Series(prices).ewm(span=ema_period, adjust=False).mean()
            ema_value = ema.iloc[-1]

        # Remove the oldest price if the list exceeds the EMA period
        if len(prices) > ema_period:
            prices.pop(0)
    
    # Calculate the simple moving average
    if ticks is not None:
        prices.append(ticks.bid)

        if len(prices) >= sma_period:
            sma = pd.Series(prices).rolling(window=sma_period, min_periods=sma_period).mean()
            sma_value = sma.iloc[-1]

        # Remove the oldest price if the list exceeds the SMA period
        if len(prices) > sma_period:
            prices.pop(0)
        
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
                "EMA": ema_value,
                "SMA": sma_value,
                "Ask Price": ticks.ask,
                "Bid Price": ticks.bid,
                "Close Price": close_price
            }, ignore_index=True)
            
            # Print the DataFrame
            print(df)
            # print()

    # Print EMA, SMA, and price
    # print(f'EMA: {ema_value}\tSMA: {sma_value}\tPrice: {ticks.bid}, {ticks.ask}\tClose Price: {close_price}')
    # print()
    sleep(0)
                # positions = mt5.positions_get(symbol=symbol)
                # if positions is not None and len(positions) > 0:
                #     for position in positions:
                #         if position.type == mt5.ORDER_TYPE_SELL:
    # Trading logic
    if mt5.positions_total() < 3:
        if ema_value > sma_value: # and close_price < ema_value:
            if close_price < ema_value and close_price < sma_value:
                
                if mt5.ORDER_TYPE_SELL:
                    # subprocess.Popen(["python", "close_positions.py"])
                    lot_size = 0.2
                    take_profit = 1
                    stop_loss = take_profit * 2
                    request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": symbol,
                        "volume": lot_size,
                        "type": mt5.ORDER_TYPE_SELL,
                        "price": mt5.symbol_info_tick(symbol).bid,
                        "sl": mt5.symbol_info_tick(symbol).bid + stop_loss,  # Set stop loss level
                        "tp": mt5.symbol_info_tick(symbol).bid - take_profit,  # Set take profit level
                        "type_filling": mt5.ORDER_FILLING_FOK,
                        "magic": 123456,
                        "comment": "Sell"
                    }


                    result = mt5.order_send(request)
                    if result.retcode != mt5.TRADE_RETCODE_DONE:
                        print("Failed to open Sell position:", result.comment)

    if ema_value < sma_value:
        if close_price > ema_value and close_price > sma_value:
            if mt5.ORDER_TYPE_BUY:
                # subprocess.Popen(["python", "close_positions.py"])
                lot_size = 0.2
                take_profit = 1
                stop_loss = take_profit * 2
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": lot_size,
                    "type": mt5.ORDER_TYPE_BUY,
                    "price": mt5.symbol_info_tick(symbol).ask,
                    "sl": mt5.symbol_info_tick(symbol).ask - stop_loss,  # Set stop loss level
                    "tp": mt5.symbol_info_tick(symbol).ask + take_profit,  # Set take profit level
                    "type_filling": mt5.ORDER_FILLING_FOK,
                    "magic": 123456,
                    "comment": "Buy"
                }


                result = mt5.order_send(request)
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    print("Failed to open Buy position:", result.comment)

                


# Step 4: Disconnect from the MetaTrader terminal
mt5.shutdown()
