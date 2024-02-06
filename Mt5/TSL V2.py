import MetaTrader5 as mt5
import math
import time

# Initialize MT5 connection
if not mt5.initialize():
    print("initialize() failed")
    mt5.shutdown()

# Define trailing stop parameters
trailing_stop = 50
profit = 100

# Define filters
only_current_symbol = True
use_magic = False
magic_number = 0
use_comment = False
comment_filter = ""
only_type = None # Replace with the corresponding constant for the type you want to filter
enable_trailing = True

while True:
    # Check if trailing stop is enabled
    if enable_trailing:
        # Get all open positions
        positions = mt5.positions_get()
        for position in positions:
            # Apply filters
            if only_current_symbol and position.symbol != mt5.symbol_info_tick().name:
                continue
            if use_magic and position.magic != magic_number:
                continue
            if use_comment and comment_filter not in position.comment:
                continue
            if only_type is not None and position.type != only_type:
                continue

            # Calculate trailing stop level
            point = mt5.symbol_info_tick(position.symbol).point
            ts_pt = trailing_stop * point
            p = profit * point

            bid = mt5.symbol_info_tick(position.symbol).bid
            ask = mt5.symbol_info_tick(position.symbol).ask
            open_price = position.price_open
            stop_loss = position.stop_loss
            take_profit = position.take_profit

            if position.type == mt5.ORDER_TYPE_BUY:
                if (bid - open_price) >= p:
                    new_sl = max(stop_loss, bid - ts_pt)
                    request = {
                        "action": mt5.TRADE_ACTION_MODIFY,
                        "symbol": position.symbol,
                        "volume": position.volume,
                        "type": position.type,
                        "position": position.ticket,
                        "price": position.price_open,
                        "sl": new_sl,
                        "tp": take_profit,
                        "deviation": 20,
                        "magic": position.magic,
                        "comment": position.comment,
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_FOK,
                    }
                    result = mt5.order_send(request)
                    if result.retcode != mt5.TRADE_RETCODE_DONE:
                        print("Failed to update stop loss. Retcode: ", result.retcode)
            elif position.type == mt5.ORDER_TYPE_SELL:
                if (open_price - ask) >= p:
                    new_sl = min(stop_loss, ask + ts_pt)
                    request = {
                        "action": mt5.TRADE_ACTION_MODIFY,
                        "symbol": position.symbol,
                        "volume": position.volume,
                        "type": position.type,
                        "position": position.ticket,
                        "price": position.price_open,
                        "sl": new_sl,
                        "tp": take_profit,
                        "deviation": 20,
                        "magic": position.magic,
                        "comment": position.comment,
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_FOK,
                    }
                    result = mt5.order_send(request)
                    if result.retcode != mt5.TRADE_RETCODE_DONE:
                        print("Failed to update stop loss. Retcode: ", result.retcode)

    # Wait for a second before checking again
    time.sleep(1)
