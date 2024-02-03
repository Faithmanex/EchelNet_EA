# Note: Set the time to 2 seconds before News Event

import datetime
import pytz
import time
import MetaTrader5 as mt5
import threading
import subprocess

class TradingBot:
    def __init__(self, tkInstance) -> None:
        self.tk = tkInstance

    def execute_trades(self, symbol, lot, stop_loss, take_profit, stop_distance, timeout, news_time) -> str:
    # existing method implementation        # create a timezone object for WAT
        wat = pytz.timezone('Africa/Lagos')

        # establish connection to the MetaTrader 5 terminal
        if not mt5.initialize():
            error = "initialise error"
            return error, None, None, None, None

        # prepare the buy request structure
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            error = "symbol not found"
            mt5.shutdown()
            return error, None, None, None, None

        if not symbol_info.visible:
            error = "symbol not visible"
            if not mt5.symbol_select(symbol, True):
                error = "symbol not selected"
                mt5.shutdown()
                return error, None, None, None, None

        point = symbol_info.point
        ask_price = mt5.symbol_info_tick(symbol).ask
        bid_price = mt5.symbol_info_tick(symbol).bid
        deviation = 20
        BUY_MAGIC = 123456
        SELL_MAGIC = 654321


        result = ''
        result1 = ''

        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY_STOP,
            "price": ask_price + stop_distance * point,
            "sl": ask_price - stop_loss * point,
            "deviation": deviation,
            "magic": BUY_MAGIC,
            "comment": "EchelNet News EA",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }

        request1 = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_SELL_STOP,
            "price": bid_price - stop_distance * point,
            "sl": bid_price + stop_loss * point,
            "deviation": deviation,
            "magic": SELL_MAGIC,
            "comment": "EchelNet News EA",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }

        
        # start the time loop
        while True:
            now_wat = datetime.datetime.now(wat)
            formatted_time = now_wat.strftime("%H:%M:%S")
            print("Current time:", formatted_time)
            # self.tk.output_text_box.insert(self.tk.END, "{}\n".format(formatted_time))
            
            if formatted_time == news_time:
                print("\nSending orders...\n")
                result = mt5.order_send(request)
                print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
                result1 = mt5.order_send(request1)
                print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))

                error = "order sent"
                if result.retcode != mt5.TRADE_RETCODE_DONE or result1.retcode != mt5.TRADE_RETCODE_DONE:
                    error = 'order sent error'
                orders = mt5.orders_get(symbol=symbol)
                for order in orders:
                    print(order.magic)
                    time.sleep(timeout)
                        
                    # Get all orders
                    orders = mt5.orders_get()
                    
                    # Check if orders is None
                    if orders is None:
                        print("No orders found.")
                        return

                    # Filter out only the pending orders
                    # Assuming that a pending order is either a BUY_STOP or SELL_STOP order
                    pending_orders = [order for order in orders if order.type == mt5.ORDER_TYPE_BUY_STOP or order.type == mt5.ORDER_TYPE_SELL_STOP]
                    
                    # Timeout to Cancel each pending order
                    for order in pending_orders:
                        trade_request = {
                            "action": mt5.TRADE_ACTION_REMOVE,
                            "order": order.ticket,
                        }
                        result = mt5.order_send(trade_request)
                        if result.retcode != mt5.TRADE_RETCODE_DONE:
                            print("Order delete failed, retcode={}".format(result.retcode))
                        else:
                            print("Pending order deleted")
                            return


            time.sleep(0.0)

        mt5.shutdown()

        return error, ask_price, deviation, result, result1
        