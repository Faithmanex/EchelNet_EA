
from datetime import datetime
import MetaTrader5 as mt5
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

        self.point = symbol_info.point
        self.ask_price = mt5.symbol_info_tick(symbol).ask
        self.bid_price = mt5.symbol_info_tick(symbol).bid
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
                    return response, self.ask_price, deviation, result, result1
                else:
                    response = "order sent"
                    return response, self.ask_price, deviation, result, result1

    def add_extra_position(self, symbol):

        while True:
            # Get the currently open orders for the specified symbol
            orders = mt5.OrdersGet(symbol=symbol)

            # Loop through the open orders to check their status
            for order in orders:
                ticket = order['ticket']
                status = order['status']

                if status == mt5.ORDER_STATUS_BUY_STOP_LIMIT:
                    # Order is activated
                    print(f"Buy Order {ticket} activated at price {order['price']}")

                elif status == mt5.ORDER_STATUS_SELL_STOP_LIMIT:
                    # Order is activated
                    print(f"Sell Order {ticket} activated at price {order['price']}")
    

        # while True :
        #     orders = mt5.orders_get(symbol)

        #     if orders is None:
        #         print("No orders found.")

        #     for position in orders:
        #         # Check if the position is a sell stop order
        #         if position.type == mt5.ORDER_TYPE_SELL_STOP:                
        #             # Check if the sell stop order has been triggered
        #             if position.open_price <= self.bid_price:
        #                 print("Sell stop order activated.")
        #                 break
                    
        #         # Check if the position is a buy stop order
        #         elif position.type == mt5.ORDER_TYPE_BUY_STOP:
        #             # Check if the buy stop order has been triggered
        #             if position.open_price <= self.ask_price:
        #                 print("Buy stop order activated.")
        #                 break

        
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


  


# new = AutoBot()
# new.auto_trade()