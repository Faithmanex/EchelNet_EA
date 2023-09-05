import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time

# connect to MetaTrader 5
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

# request initial bars of EURUSD H1
rates = mt5.copy_rates_from_pos("EURUSD", mt5.TIMEFRAME_H1, 0, 1000)

# create DataFrame out of the obtained data
rates_frame = pd.DataFrame(rates)

# calculate moving averages
rates_frame['SMA'] = rates_frame['close'].rolling(window=7).mean()
rates_frame['EMA'] = rates_frame['close'].ewm(span=50, adjust=False).mean()
weights = np.arange(1, 21)
rates_frame['LWMA'] = rates_frame['close'].rolling(window=20).apply(
    lambda prices: np.dot(prices, weights) / weights.sum(), raw=True)

# initialize position variables
position_sell = None
position_buy = None

# continuously update and print moving averages
while True:
    # get the latest bar
    latest_bar = mt5.copy_rates_from_pos("EURUSD", mt5.TIMEFRAME_H1, 0, 1)

    # append the latest bar to the DataFrame
    latest_bar_frame = pd.DataFrame(latest_bar, columns=rates_frame.columns)
    rates_frame = pd.concat([rates_frame, latest_bar_frame], ignore_index=True)

    # update moving averages
    rates_frame['SMA'] = rates_frame['close'].rolling(window=7).mean()
    rates_frame['EMA'] = rates_frame['close'].ewm(span=50, adjust=False).mean()
    rates_frame['LWMA'] = rates_frame['close'].rolling(window=20).apply(
        lambda prices: np.dot(prices, weights) / weights.sum(), raw=True)

    # check for crossover and open positions
    if not position_sell and rates_frame['LWMA'].iloc[-2] > rates_frame['SMA'].iloc[-2] and rates_frame['LWMA'].iloc[
        -1] < rates_frame['SMA'].iloc[-1]:
        # close any existing buy position
        if position_buy:
            mt5.position_close(position_buy)
            position_buy = None
        # open sell position
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": "EURUSD",
            "volume": 1.0,
            "type": mt5.ORDER_TYPE_SELL,
            "price": mt5.symbol_info_tick("EURUSD").bid,
            "deviation": 10,
            "magic": 0,
            "comment": "Sell Position"
        }
        result = mt5.order_send(request)
        if not result:
            print("Failed to send sell order")
        else:
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                position_sell = result.order
                print("Sell position opened")
            else:
                print("Failed to open sell position. Retcode:", result.retcode)

    elif not position_buy and rates_frame['SMA'].iloc[-2] > rates_frame['LWMA'].iloc[-2] and rates_frame['SMA'].iloc[
        -1] < rates_frame['LWMA'].iloc[-1]:
        # close any existing sell position
        if position_sell:
            mt5.position_close(position_sell)
            position_sell = None
        # open buy position
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": "EURUSD",
            "volume": 1.0,
            "type": mt5.ORDER_TYPE_BUY,
            "price": mt5.symbol_info_tick("EURUSD").ask,
            "deviation": 10,
            "magic": 0,
            "comment": "Buy Position"
        }
        result = mt5.order_send(request)
        if not result:
            print("Failed to send buy order")
        else:
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                position_buy = result.order
                print("Buy position opened")
            else:
                print("Failed to open buy position. Retcode:", result.retcode)

    # print the latest values
    print(rates_frame[['time', 'close', 'SMA', 'EMA', 'LWMA']].tail(1))

    # wait for 1 second before the next update
    time.sleep(1)

# shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
