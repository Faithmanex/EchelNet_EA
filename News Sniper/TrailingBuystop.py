from datetime import datetime
import MetaTrader5 as mt5
import pandas as pd
import time

print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)

pd.set_option('display.max_columns', 500) 
pd.set_option('display.width', 1500)     

if not mt5.initialize():
   print("initialize() failed, error code =",mt5.last_error())
   quit()
while 1 ==1:
    rates = mt5.copy_rates_from_pos("Step Index", mt5.TIMEFRAME_M1, 0, 1)

    print(rates)

    rates_frame = pd.DataFrame(rates)
    rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')

    # Convert tick_volume to float before printing
    # print(int(rates_frame['tick_volume']))
    # print("\nDisplay dataframe with data")
    print(rates_frame)
    if 21 == 21:
        symbol = "Boom 300 Index"
        lot = 1
        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).ask
        deviation = 10000000
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            "sl": price - 100 * point,
            "tp": price + 100 * point,
            "deviation": deviation,
            "magic": 234000,
            "comment": "python script open",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }
        
        # send a trading request
        result = mt5.order_send(request)
        # check the execution result
        print("1. order_send(): by {} {} lots at {} with deviation={} points".format(symbol,lot,price,deviation));
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print("2. order_send failed, retcode={}".format(result.retcode))
            # request the result as a dictionary and display it element by element
            result_dict=result._asdict()
            for field in result_dict.keys():
                print("   {}={}".format(field,result_dict[field]))
                # if this is a trading request structure, display it element by element as well
                if field=="request":
                    traderequest_dict=result_dict[field]._asdict()
                    for tradereq_filed in traderequest_dict:
                        print("       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))
            print("shutdown() and quit")
            mt5.shutdown()
            quit()
        
        print("2. order_send done, ", result)
        print("   opened position with POSITION_TICKET={}".format(result.order))
        print("   sleep 2 seconds before closing position #{}".format(result.order))
        time.sleep(2)