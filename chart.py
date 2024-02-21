import MetaTrader5 as mt5

# --- Input parameters ---
profit_threshold = 50  # Points of profit to activate trailing
trailing_distance = 20  # Distance of trailing stop-loss 

# --- Initialize MetaTrader 5 ---
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

# --- Function to modify a position with a trailing stop loss ---
def modify_position(position, trailing_stop, profit):   
    symbol = position.symbol()
    ticket = position.ticket()
    current_price = mt5.symbol_info_tick(symbol).ask if position.type() == 0 else mt5.symbol_info_tick(symbol).bid
    
    if position.profit() >= profit:
        new_stop_loss = current_price - trailing_stop * mt5.symbol_info(symbol).point  # For buy positions
        if position.type() == 1:  # For sell positions
            new_stop_loss = current_price + trailing_stop * mt5.symbol_info(symbol).point

        # Send modification request
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": symbol,
            "position": ticket,
            "sl": new_stop_loss
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print("Failed to modify order #{}: {}".format(ticket, result.comment))

# --- Main EA logic ---
while True:
    positions = mt5.positions_get()

    if positions is not None:  
        for pos in positions:
            modify_position(pos, trailing_distance, profit_threshold)

    mt5.sleep(5000)  # Check every 5 seconds

# --- Deinitialize MetaTrader 5 ---
mt5.shutdown()
