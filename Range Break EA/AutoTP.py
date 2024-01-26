import MetaTrader5 as mt5
import time  # Import the time module for a delay between modifications

# Initialize connection to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed")
    mt5.shutdown()

points = 50  # Replace with desired number of points

# Define a function to modify the TakeProfit level
def modify_take_profit():
    # Get the list of open positions
    positions = mt5.positions_get()
    
    if positions is not None and len(positions) > 0:
        for position in positions:
            # Get the symbol of the position
            symbol = position.symbol
            entry_price = position.price_open
            
            # Get the current price of the symbol
            current_price = mt5.symbol_info_tick(symbol).bid if position.volume > 0 else mt5.symbol_info_tick(symbol).ask
            
            # Calculate the TakeProfit price based on the direction of the position
            print(position.type)
            tp_price = entry_price + points * mt5.symbol_info(symbol).point if position.type == 0 else entry_price - points * mt5.symbol_info(symbol).point
            
            # Check if the calculated TakeProfit price is valid
            if tp_price == current_price:
                print(f"Invalid TakeProfit price for position {position.ticket}")
                continue

            # Create a request to modify the position
            request = {
                'action': mt5.TRADE_ACTION_SLTP,
                'position': position.ticket,
                'tp': tp_price,
            }
            
            # Send the request
            result = mt5.order_send(request)
            
            # Check if the request was successful
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                print(f"Failed to modify position {position.ticket}, error code: {result.retcode}")
            else:
                print(f"Successfully modified position {position.ticket}")
                time.sleep(15)
                     
                # Get all orders
                orders = mt5.orders_get()
                
                # Check if orders is None
                if orders is None:
                    print("No orders found.")
                    return

                # Filter out only the pending orders
                # Assuming that a pending order is either a BUY_STOP or SELL_STOP order
                pending_orders = [order for order in orders if order.type == mt5.ORDER_TYPE_BUY_LIMIT or order.type == mt5.ORDER_TYPE_SELL_LIMIT]
                
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
                        print("Pending Limit order deleted")
                        return

# Infinite loop to continuously check and modify TakeProfit levels
while 1==1:
    modify_take_profit()
    time.sleep(0)  # Adjust the delay as needed

# Disconnect from the MetaTrader 5 terminal
mt5.shutdown()