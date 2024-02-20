from datetime import datetime
import MetaTrader5 as mt5
import pytz

class TradingBot:
    def __init__(self):
        self.buy_stop_price = 0
        self.sell_stop_price = 0
        self.buy_stop_ticket = 0
        self.sell_stop_ticket = 0
    
    def convert_to_lagos_timezone(self, input_time):
        input_time_obj = datetime.strptime(input_time, "%H:%M:%S")

        # Set the timezone for Lagos
        lagos_timezone = pytz.timezone('Africa/Lagos')
        input_time_utc = pytz.utc.localize(input_time_obj)

        # Convert to Lagos timezone
        lagos_time = input_time_utc.astimezone(lagos_timezone)

        return lagos_time.strftime("%H:%M:%S")

    def execute_trades(self, symbol, lot, stop_loss, stop_distance, news_time) -> str:
        # wat = pytz.timezone('Africa/Lagos')

        if not mt5.initialize():
            response = "initialize error"
            return response, None, None, None, None

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

        self.point = symbol_info.point
        self.ask_price = mt5.symbol_info_tick(symbol).ask
        self.bid_price = mt5.symbol_info_tick(symbol).bid
        deviation = 200
        BUY_MAGIC = 123456
        SELL_MAGIC = 654321

        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY_STOP,
            "price": self.ask_price + stop_distance * self.point,
            "sl": self.ask_price - stop_loss * self.point,
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
            "price": self.bid_price - stop_distance * self.point,
            "sl": self.bid_price + stop_loss * self.point,
            "deviation": deviation,
            "magic": SELL_MAGIC,
            "comment": "EchelNet News EA",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }
        
        
        # start the time loop

        # start the time loop
        while True:
            # wat means West Africa Time
            current_time = datetime.now().strftime("%H:%M:%S")
            current_time_wat = self.convert_to_lagos_timezone(current_time)
            news_time_wat = self.convert_to_lagos_timezone(news_time)

            if current_time_wat == news_time_wat:
                print(f"\nSending orders...\nBuy Stop: {request['price']}\nSell Stop: {request1['price']}")
                result = mt5.order_send(request)
                self.buy_stop_price = request['price']
                self.buy_stop_sl = request['sl']
                self.buy_stop_ticket = result.order
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
                
                result1 = mt5.order_send(request1)
                self.sell_stop_price = request1['price']
                self.sell_stop_sl = request1['sl']
                self.sell_stop_ticket = result1.order
                print(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))

                if result.retcode != mt5.TRADE_RETCODE_DONE or result1.retcode != mt5.TRADE_RETCODE_DONE:
                    response = 'order sent error'
                    return response, self.ask_price, deviation, result, result1
                else:
                    response = "order sent"
                    return response, self.ask_price, deviation, result, result1

    def check_triggered_orders(self, symbol, BUY_MAGIC, SELL_MAGIC, deviation):
        # Check if there are any positions with the magic_numbers of buy stop or sell stop
        result_buy_stop = ''
        result_sell_stop = ''
        loop_variable = True

        while loop_variable:
            positions = mt5.positions_get(symbol=symbol)

            for position in positions:
                if position.magic == BUY_MAGIC:
                    # Buy stop order triggered, send another sell stop order
                    request_sell_stop = {
                        "action": mt5.TRADE_ACTION_PENDING,
                        "symbol": symbol,
                        "volume": position.volume,
                        "type": mt5.ORDER_TYPE_SELL_STOP,
                        "price": self.sell_stop_price,
                        "sl": self.sell_stop_sl,
                        "deviation": deviation,
                        "magic": SELL_MAGIC,
                        "comment": "EchelNet News EA",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_RETURN,
                    }
                    result_sell_stop = mt5.order_send(request_sell_stop)

                    print("Buy stop order triggered. Sending Sell Stop.")
                    
                    loop_variable = False
                    break
                    
                elif position.magic == SELL_MAGIC:
                    # Sell stop order triggered, send another buy stop order
                    request_buy_stop = {
                        "action": mt5.TRADE_ACTION_PENDING,
                        "symbol": symbol,
                        "volume": position.volume,
                        "type": mt5.ORDER_TYPE_BUY_STOP,
                        "price": self.buy_stop_price,
                        "sl": self.buy_stop_sl,
                        "deviation": deviation,
                        "magic": BUY_MAGIC,
                        "comment": "EchelNet News EA",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_RETURN,
                    }
                    result_buy_stop = mt5.order_send(request_buy_stop)
                    print("Sell stop order triggered. Sending Buy Stop.")
                    
                    loop_variable = False
                    break
            



    def cancel_all_pending_orders(self, symbol):
        orders = mt5.orders_get(symbol=symbol)
        
        # Check if orders is None
        if orders is None:
            print("No orders found.")
            return

        # Filter out only the pending orders
        # Assuming that a pending order is either a BUY_STOP or SELL_STOP order
        pending_orders = [order for order in orders if order.type == mt5.ORDER_TYPE_BUY_STOP or order.type == mt5.ORDER_TYPE_SELL_STOP]
        
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



# new = AutoBot()
# new.auto_trade()

# Example Usage:
# bot = TradingBot()
# bot.execute_trades("EURUSD", 0.1, 10, 50, "12:30:00")
# bot.add_extra_position("EURUSD")
# bot.check_triggered_orders("EURUSD")
# bot.cancel_all_pending_orders("EURUSD")