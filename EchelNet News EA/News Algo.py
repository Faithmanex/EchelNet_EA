# This version places a buy stop and sell stop order
# 1. Checks time in GMT, places the pending orders based on time input
# 2. Loops and displays current time in GMT
# 3. Created variables for some values
# Note: Set the time to 2 seconds before News Event

import datetime
import pytz
import time
import MetaTrader5 as mt5

# create a timezone object for WAT
wat = pytz.timezone('Africa/Lagos')

# establish connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

# prepare the buy request structure
symbol = "Step Index"
symbol_info = mt5.symbol_info(symbol)
if symbol_info is None:
    print(symbol, "not found, can not call order_check()")
    mt5.shutdown()
    quit()

# if the symbol is unavailable in MarketWatch, add it
if not symbol_info.visible:
    print(symbol, "is not visible, trying to switch on")
    if not mt5.symbol_select(symbol, True):
        print("symbol_select({}) failed, exit".format(symbol))
        mt5.shutdown()
        quit()
news_time = "11:00:00"
lot = 0.5
stop_loss = 35
take_profit = 150
stop_distance = 35
point = mt5.symbol_info(symbol).point
price = mt5.symbol_info_tick(symbol).ask
deviation = 20
request = {
    "action": mt5.TRADE_ACTION_PENDING,
    "symbol": symbol,
    "volume": lot,
    "type": mt5.ORDER_TYPE_BUY_STOP,
    "price": price + stop_distance * point,
    "sl": price - stop_loss * point,
    # "tp": price + take_profit * point,
    "deviation": deviation,
    "magic": 234000,
    "comment": "EchelNet News EA",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_RETURN,
}

request1 = {
    "action": mt5.TRADE_ACTION_PENDING,
    "symbol": symbol,
    "volume": lot,
    "type": mt5.ORDER_TYPE_SELL_STOP,
    "price": price - stop_distance * point,
    "sl": price + stop_loss * point,
    # "tp": price - take_profit * point,
    "deviation": deviation,
    "magic": 235000,
    "comment": "EchelNet Sniper",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_RETURN,
}

# start the time loop
while True:
    # get the current time in WAT
    now_wat = datetime.datetime.now(wat)
   
    # format the time to match the desired format
    formatted_time = now_wat.strftime("%H:%M:%S")
    print(formatted_time)
   
    # check if the time matches the desired time
    if formatted_time == news_time:
        # send a trading request
        result = mt5.order_send(request)
        result1 = mt5.order_send(request1)
        # check the execution result
        print("1. order_send(): by {} {} lots at {} with deviation={} points".format(symbol, lot, price, deviation))
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print("2. order_send failed, retcode={} ({})".format(result.retcode, "Unknown retcode"))
        break
   
    # wait for a second before checking again
    time.sleep(1)

mt5.shutdown()
quit()
