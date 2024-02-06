import MetaTrader5 as mt5

# Initialize MetaTrader5
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

symbol = "XAUUSD"

# Get positions for the specified symbol
positions = mt5.positions_get(symbol=symbol)

# Close all open positions
if positions is None:
    print("No positions found, error code={}".format(mt5.last_error()))
elif len(positions) > 0:
    for position in positions:
        action = mt5.TRADE_ACTION_DEAL if position.type == mt5.ORDER_TYPE_BUY else mt5.TRADE_ACTION_DEAL
        trade_request = {
            "action": action,
            "symbol": symbol,
            "volume": position.volume,
            "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
            "position": position.ticket,
            "price": mt5.symbol_info_tick(symbol).bid if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).ask,
            "deviation": 20,
            "magic": 234000,
            "comment": "python script close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        result = mt5.order_send(trade_request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print("Order failed, retcode={}".format(result.retcode))
        else:
            print("Position Closed")
else:
    print("No positions found")

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
