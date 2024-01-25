import MetaTrader5 as mt5

# Connect to the MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed")
    mt5.shutdown()

# Set the magic number
magic_number = 123456

# Open a buy trade
symbol = "EURUSDm"
lot = 0.01
ask_price = mt5.symbol_info_tick(symbol).ask
bid_price = mt5.symbol_info_tick(symbol).bid
# sl = price - 100 * mt5.symbol_info(symbol).point
# tp = price + 100 * mt5.symbol_info(symbol).point
request = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": symbol,
    "volume": lot,
    "type": mt5.ORDER_TYPE_BUY,
    "price": ask_price,
    # "sl": sl,
    # "tp": tp,
    "magic": magic_number,
    "comment": "Buy trade with magic number 123456",
}
result = mt5.order_send(request)
if result.retcode != mt5.TRADE_RETCODE_DONE:
    print(f"order_send failed, retcode={result.retcode}")
    mt5.shutdown()

# Disconnect from the MetaTrader 5 terminal
mt5.shutdown()