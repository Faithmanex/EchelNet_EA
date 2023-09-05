import MetaTrader5 as mt5
import numpy as np

def ma_crossover_strategy():
    # Connect to MetaTrader 5
    if not mt5.initialize():
        print("Failed to initialize MetaTrader 5")
        return
    
    # Set the symbol and timeframe
    symbol = "EURUSD"
    timeframe = mt5.TIMEFRAME_H1
    
    # Set the MA parameters
    ma_fast_period = 5
    ma_medium_period = 10
    ma_slow_period = 20
    
    # Calculate the number of bars required for MA calculations
    ma_bars = max(ma_fast_period, ma_medium_period, ma_slow_period)
    
    # Retrieve the OHLC data for the required number of bars plus one
    rates = mt5.copy_rates_from(symbol, timeframe, ma_bars + 1, mt5.COPY_RATE_CLOSE)
    
    # Extract the Close prices from the rates data
    close_prices = np.array([bar.close for bar in rates])
    
    # Calculate the Moving Averages using the CopyBuffer function
    ma_fast = mt5.copy_buffer(0, 0, 0, ma_bars, close_prices, ma_fast_period, 0)
    ma_medium = mt5.copy_buffer(0, 0, 0, ma_bars, close_prices, ma_medium_period, 0)
    ma_slow = mt5.copy_buffer(0, 0, 0, ma_bars, close_prices, ma_slow_period, 0)
    
    # Check for crossover
    if ma_fast[-2] < ma_medium[-2] and ma_fast[-1] > ma_medium[-1]:
        # Open a buy position
        lot_size = 0.01
        stop_loss = 50
        take_profit = 100
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_BUY,
            "price": mt5.symbol_info_tick(symbol).ask,
            "sl": mt5.symbol_info_tick(symbol).ask - stop_loss * mt5.symbol_info(symbol).point,
            "tp": mt5.symbol_info_tick(symbol).ask + take_profit * mt5.symbol_info(symbol).point,
            "magic": 123456,
            "comment": "Buy"
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print("Failed to open buy position:", result.comment)
    
    elif ma_fast[-2] > ma_medium[-2] and ma_fast[-1] < ma_medium[-1]:
        # Open a sell position
        lot_size = 0.01
        stop_loss = 50
        take_profit = 100
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_SELL,
            "price": mt5.symbol_info_tick(symbol).bid,
            "sl": mt5.symbol_info_tick(symbol).bid + stop_loss * mt5.symbol_info(symbol).point,
            "tp": mt5.symbol_info_tick(symbol).bid - take_profit * mt5.symbol_info(symbol).point,
            "magic": 123456,
            "comment": "Sell"
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print("Failed to open sell position:", result.comment)
    
    # Disconnect from MetaTrader 5
    mt5.shutdown()

# Run the strategy
ma_crossover_strategy()
