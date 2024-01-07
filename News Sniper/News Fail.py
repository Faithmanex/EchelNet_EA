import MetaTrader5 as mt5

def connect_to_mt5():
    mt5.initialize()

def disconnect_from_mt5():
    mt5.shutdown()

def get_symbol_prices(symbol):
    tick = mt5.symbol_info_tick(symbol)
    return tick.last, tick.ask, tick.bid

def calculate_stop_levels(ask_price, bid_price, stop_distance):
    buy_stop_price = round(ask_price + stop_distance, 5)
    sell_stop_price = round(bid_price - stop_distance, 5)
    return buy_stop_price, sell_stop_price

def place_stop_order(action, symbol, volume, price, tp, sl, timeframe):
    order_request = {
        "action": action,
        "symbol": symbol,
        "volume": volume,
        "price": price,
        # "tp": tp,
        # "sl": sl,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
        "timeframe": timeframe,
    }

    order_result = mt5.order_send(order_request)
    return order_result

def main():
    try:
        # Connect to MetaTrader 5
        connect_to_mt5()

        # Define parameters
        symbol = "EURUSD"
        lot_size = 0.01
        stop_distance = 20
        timeframe = mt5.TIMEFRAME_M1

        # Get current prices
        last_price, ask_price, bid_price = get_symbol_prices(symbol)

        # Calculate stop levels
        buy_stop_price, sell_stop_price = calculate_stop_levels(ask_price, bid_price, stop_distance)

        # Define take profit and stop loss levels (in points)
        take_profit = 50
        stop_loss = 50

        # Place buy stop order
        buy_tp = round(buy_stop_price + take_profit * mt5.symbol_info(symbol).point, 5)
        buy_sl = round(buy_stop_price - stop_loss * mt5.symbol_info(symbol).point, 5)

        buy_stop_result = place_stop_order(mt5.ORDER_TYPE_BUY_STOP, symbol, lot_size, buy_stop_price, buy_tp, buy_sl, timeframe)
        print("Buy Stop Order Result:", buy_stop_result)

        # Place sell stop order
        sell_tp = round(sell_stop_price - take_profit * mt5.symbol_info(symbol).point, 5)
        sell_sl = round(sell_stop_price + stop_loss * mt5.symbol_info(symbol).point, 5)

        sell_stop_result = place_stop_order(mt5.ORDER_TYPE_SELL_STOP, symbol, lot_size, sell_stop_price, sell_tp, sell_sl, timeframe)
        print("Sell Stop Order Result:", sell_stop_result)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Disconnect from MetaTrader 5
        disconnect_from_mt5()

if __name__ == "__main__":
    main()
