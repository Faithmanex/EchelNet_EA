# Refactored code
import datetime
import pytz
import time
import MetaTrader5 as mt5

wat = pytz.timezone('Africa/Lagos')

if not mt5.initialize():
    quit()

symbol = "Step Index"
if not (symbol_info := mt5.symbol_info(symbol)) or not mt5.symbol_select(symbol, True):
    mt5.shutdown()
    quit()

news_time = datetime.time(11, 20, 0)
lot = 0.5
stop_loss = 35
take_profit = 150
stop_distance = 35
point = symbol_info.point
price = mt5.symbol_info_tick(symbol).ask
deviation = 20
magic_number_buy = 234000
magic_number_sell = 235000
comment_buy = "EchelNet News EA"
comment_sell = "EchelNet News EA"

request_buy = {
    "action": mt5.TRADE_ACTION_PENDING,
    "symbol": symbol,
    "volume": lot,
    "type": mt5.ORDER_TYPE_BUY_STOP,
    "price": price + stop_distance * point,
    "sl": price - stop_loss * point,
    "tp": price + take_profit * point,
    "deviation": deviation,
    "magic": magic_number_buy,
    "comment": comment_buy,
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_RETURN,
}

request_sell = {
    "action": mt5.TRADE_ACTION_PENDING,
    "symbol": symbol,
    "volume": lot,
    "type": mt5.ORDER_TYPE_SELL_STOP,
    "price": price - stop_distance * point,
    "sl": price + stop_loss * point,
    "tp": price - take_profit * point,
    "deviation": deviation,
    "magic": magic_number_sell,
    "comment": comment_sell,
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_RETURN,
}

while datetime.datetime.now(wat).time() < news_time:
    time.sleep(1)

result_buy = mt5.order_send(request_buy)
result_sell = mt5.order_send(request_sell)

mt5.shutdown()
