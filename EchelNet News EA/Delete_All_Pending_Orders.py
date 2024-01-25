import MetaTrader5 as mt5

# Initialize MetaTrader5
if not mt5.initialize():
   print("initialize() failed, error code =", mt5.last_error())
   quit()

symbol = "EURUSDm"

# Get pending orders for the specified symbol
orders = mt5.orders_get(symbol=symbol)

# Delete all pending orders
if orders is None:
   print("No pending orders found, error code={}".format(mt5.last_error()))
elif len(orders) > 0:
   for order in orders:
       trade_request = {
           "action": mt5.TRADE_ACTION_REMOVE,
           "order": order.ticket,
       }
       result = mt5.order_send(trade_request)
       if result.retcode != mt5.TRADE_RETCODE_DONE:
           print("Order delete failed, retcode={}".format(result.retcode))
       else:
           print("Pending order deleted")
else:
   print("No pending orders found")

mt5.shutdown()
