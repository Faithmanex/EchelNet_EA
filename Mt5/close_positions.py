import MetaTrader5 as mt5

if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()

symbol = "Step Index"

positions = mt5.positions_get(symbol=symbol)

if positions == None:
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
    print("No positions found")
