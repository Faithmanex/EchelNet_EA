# Note: Set the time to 2 seconds before News Event

import datetime
import time
import MetaTrader5 as mt5
import threading
import subprocess
import json
from datetime import datetime, timedelta, date
import pytz


class TradingBot:

    def execute_trades(self, symbol, lot, stop_loss, stop_distance, news_time) -> str:
    # existing method implementation        # create a timezone object for WAT
        wat = pytz.timezone('Africa/Lagos')

        # establish connection to the MetaTrader 5 terminal
        if not mt5.initialize():
            response = "initialise error"
            return response, None, None, None, None

        # prepare the buy request structure
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            response = "symbol not found"
            mt5.shutdown()
            return response, None, None, None, None

        if not symbol_info.visible:
            response = "symbol not visible"
            if not mt5.symbol_select(symbol, True):
                response = "symbol not selected"
                mt5.shutdown()
                return response, None, None, None, None

        point = symbol_info.point
        ask_price = mt5.symbol_info_tick(symbol).ask
        bid_price = mt5.symbol_info_tick(symbol).bid
        deviation = 20
        BUY_MAGIC = 123456
        SELL_MAGIC = 654321


        # result = ''
        # result1 = ''

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
            now_wat = datetime.now(wat)
            formatted_time = now_wat.strftime("%H:%M:%S")
            # print("Current time:", formatted_time)
            # self.tk.output_text_box.insert(self.tk.END, "{}\n".format(formatted_time))
            
            if formatted_time == news_time:
                print("\nSending orders...\n")
                result = mt5.order_send(request)
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
                result1 = mt5.order_send(request1)
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))

                
                if result.retcode != mt5.TRADE_RETCODE_DONE or result1.retcode != mt5.TRADE_RETCODE_DONE:
                    response = 'order sent error'
                    return response, ask_price, deviation, result, result1
                else:
                    response = "order sent"
                    return response, ask_price, deviation, result, result1
         
        
    def cancel_all_pending_orders(self, symbol):
        # Get all orders
        orders = mt5.orders_get(symbol=symbol)
        
        # Check if orders is None
        if orders is None:
            print("No orders found.")
            return

        # Filter out only the pending orders
        # Assuming that a pending order is either a BUY_STOP or SELL_STOP order
        pending_orders = [order for order in orders if order.type == mt5.ORDER_TYPE_BUY_STOP or order.type == mt5.ORDER_TYPE_SELL_STOP]
        
        # Cancel each pending order
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




class AutoBot:
    def __init__(self, user_settings="./json_data/user_data.json", calendar='./json_data/forex_calendar.json'):
         # Open the JSON file
        with open(user_settings) as user_file:
            self.settings = json.load(user_file)
        
        with open(calendar) as file:
            self.calendar = json.load(file)

        self.trade = TradingBot()

    def filter_news(self):
        # Define desired currencies and impacts
        desired_currencies = ["GBP", "USD", "EUR"]
        desired_impacts = ["high"]
        previous_date = None
        new_calendar_data = []

        for calendar_data in self.calendar:
        
             # Attach a date if none present
            if calendar_data["date"] == None:
                calendar_data["date"] = previous_date
            else:
                previous_date = calendar_data["date"]

            # Skip events with undesired impact or currency
            if calendar_data["impact"] not in desired_impacts or calendar_data["currency"] not in desired_currencies:
                continue

            new_calendar_data.append(calendar_data)
        
        # Filter the data to remove news with the same time
        filtered_data = [new_calendar_data[0]]

        for data in new_calendar_data[1:]:
            if data["date"] != filtered_data[-1]["date"]:
                filtered_data.append(data)

        return filtered_data
 

       
    def auto_trade(self) -> None:
        
        # Get the news events we'll be taking
        trading_news = self.filter_news()

        for news_event in trading_news:

            news_day = news_event["date"].split(' ')[0] # News day
            news_time = news_event["date"].split(' ')[1] # News time
            time_object = datetime.strptime(news_time, '%H:%M:%S').time()

            # change the news time to take it 3 seconds before the actual time
            new_time = str((datetime.combine(datetime.min, time_object) - timedelta(seconds=3)).time())

            # Converting the currency to a readable form by the terminal
            if news_event['currency'] == "GBP":
                currency = news_event['currency'] + "USD"
            elif news_event['currency'] == "EUR" or  news_event['currency'] == "USD":
                currency = "EURUSD"
            

            if news_day == str(date.today()):
                response, _, _, _, _, = self.trade.execute_trades(currency, 
                                                        self.settings["lot"], 
                                                        self.settings["stop_loss"], 
                                                        self.settings["stop_distance"], 
                                                        new_time)
                

            #handle timeout
            if response == "order sent":
                time.sleep(self.settings["timeout"])
                self.trade.cancel_all_pending_orders(currency)      


new = AutoBot()
new.auto_trade()