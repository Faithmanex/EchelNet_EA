# This version places a buy stop and sell stop order
# 1. Checks time in GMT, places the pending orders based on time input
# 2. Loops and displays current time in GMT
# 3. Created variables for some values
# Note: Set the time to 2 seconds before News Event

import datetime
import pytz
import time
import MetaTrader5 as mt5
import threading

class TradingBot:
    def __init__(self, tkInstance) -> None:
        self.tk = tkInstance

    def execute_trades(self, symbol, lot, stop_loss, take_profit, stop_distance, news_time) -> str:
        # create a timezone object for WAT
        wat = pytz.timezone('Africa/Lagos')

        # establish connection to the MetaTrader 5 terminal
        if not mt5.initialize():
            error = "initialise error"
            return

        # prepare the buy request structure
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            error = "symbol not found"
            mt5.shutdown()
            return

        if not symbol_info.visible:
            error = "symbol not visible"
            if not mt5.symbol_select(symbol, True):
                error = "symbol not selected"
                mt5.shutdown()
                return

        point = symbol_info.point
        price = mt5.symbol_info_tick(symbol).ask
        deviation = 20
        result = None
        result1 = None

        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY_STOP,
            "price": price + stop_distance * point,
            "sl": price - stop_loss * point,
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
            "deviation": deviation,
            "magic": 235000,
            "comment": "EchelNet Sniper",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }

        # start the time loop
        while True:
            now_wat = datetime.datetime.now(wat)
            formatted_time = now_wat.strftime("%H:%M:%S")
            # self.tk.output_text_box.insert(self.tk.END, "{}\n".format(formatted_time))

            if formatted_time == news_time:
                result = mt5.order_send(request)
                result1 = mt5.order_send(request1)
                error = "order sent"
                if result.retcode != mt5.TRADE_RETCODE_DONE or result1.retcode != mt5.TRADE_RETCODE_DONE:
                    error = 'order sent error'
                break

            time.sleep(0.1)

        mt5.shutdown()

        return error, price, deviation, result, result1