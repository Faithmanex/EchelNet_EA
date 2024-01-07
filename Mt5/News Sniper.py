import MetaTrader5 as mt5
import time

def get_current_price(symbol):
    tick = mt5.symbol_info_tick(symbol)
    return tick.ask

def get_current_stop_loss(order):
    # Get the order information
    order_info = mt5.order_get(order)
    if order_info is None:
        print("Failed to get order info, error code={}".format(mt5.last_error()))
        return None
    return order_info.sl

def set_new_stop_loss(symbol, volume, new_stop_loss):
    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "symbol": symbol,
        "volume": volume,
        "price": mt5.symbol_info_tick(symbol).ask,
        "stoplimit": new_stop_loss,
        "deviation": 20,
        "type": mt5.ORDER_TYPE_BUY,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    result = mt5.order_send(request)
    return result.retcode == mt5.TRADE_RETCODE_DONE

def place_order(symbol, volume):
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY,
        "price": mt5.symbol_info_tick(symbol).ask,
        "sl": mt5.symbol_info_tick(symbol).ask - 20 * mt5.symbol_info(symbol).point,
        "tp": mt5.symbol_info_tick(symbol).ask + 20 * mt5.symbol_info(symbol).point,
        "deviation": 20,
        "magic": 234000,
        "comment": "python script buy",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("Failed to place order, error code={}".format(result.retcode))
        return None
    return result.order



    symbol = "EURUSD"
    volume = 0.01
    trailing_stop = 20

    # check if the symbol is available for trading
    if not mt5.symbol_select(symbol, True):
        print(f"symbol {symbol} is not available for trading, error code = {mt5.last_error()}")
        mt5.shutdown()
        quit()

    # place a buy order
    order = place_order(symbol, volume)
    if order is None:
        print("Failed to place order")
        mt5.shutdown()
        quit()

    highest_price = get_current_price(symbol)

    while True:
        # get the current price
        current_price = get_current_price(symbol)
        # if the current price is higher than the highest price, update the highest price
        if current_price > highest_price:
            highest_price = current_price
        # calculate the stop loss price based on the highest price and the trailing stop
        stop_loss_price = highest_price - trailing_stop * mt5.symbol_info(symbol).point
        # get the current stop loss
        current_stop_loss = get_current_stop_loss(order)
        if current_stop_loss is None:
            break
        # if the calculated stop loss price is higher than the current stop loss, update the stop loss
        if stop_loss_price > current_stop_loss:
            if set_new_stop_loss(symbol, volume, stop_loss_price):
                print("Updated stop loss to: {}".format(stop_loss_price))
        # wait for a while before the next iteration
        time.sleep(1)

    # shut down connection to the MetaTrader 5 terminal
    mt5.shutdown()

if __name__ == "__main__":
    main()
