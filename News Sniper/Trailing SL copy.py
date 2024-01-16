# import libraries
import MetaTrader5 as mt5
import time
import sys

# connect Python to MetaTrader5
mt5.initialize()

# CONFIGS

MAX_DIST_SL = 0.0002  # Max distance between current price and SL, otherwise SL will update
TRAIL_AMOUNT = 0.0001  # Amount by how much SL updates
DEFAULT_SL = 0.0002 # If position has no SL, set a default SL


# function to trail SL
# Add a list of symbols to which you want to apply the trailing stop loss
SYMBOLS = ["EURUSD", "USDJPY", "GBPUSD", "USDCHF", "USDCAD", "AUDUSD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY", "AUDJPY", "NZDJPY", "AUDNZD"
]

def trail_sl():
  # get all open positions
  positions = mt5.positions_get()

  # check if positions exist
  if positions:
      for position in positions:
          # Check if the position's symbol is in the SYMBOLS list
          if position.symbol in SYMBOLS:
              # get position data
              order_type = position.type
              price_current = position.price_current
              price_open = position.price_open
              sl = position.sl
              trail = price_open
              

              dist_from_sl = abs(round(price_current - sl, 6))

              if dist_from_sl > MAX_DIST_SL:
                 # calculating new sl
                 if sl != 0.0:
                    if order_type == 0: # 0 stands for BUY
                        new_sl = trail + TRAIL_AMOUNT
                        if sl > price_open:
                            trail = sl
                            new_sl = trail + TRAIL_AMOUNT

                    elif order_type == 1: # 1 stands for SELL
                        new_sl = trail - TRAIL_AMOUNT
                        if sl < price_open:
                            trail = sl
                            new_sl = trail - TRAIL_AMOUNT

                 else:
                    # setting default SL if the is no SL on the symbol
                    new_sl = price_open - DEFAULT_SL if order_type == 0 else price_open + DEFAULT_SL

                 request = {
                    'action': mt5.TRADE_ACTION_SLTP,
                    'position': position.ticket,
                    'sl': new_sl,
                    'comment': "EchelNet",
                 }

                 result = mt5.order_send(request)
                 print(result)
                 return result
             
  else:
      print('No open positions')




if __name__ == '__main__':
    print('Starting Trailing Stoploss..')
    # print(f'Position: {str(TICKET)}')

    # strategy loop
    while True:
        result = trail_sl()
        # wait 1 second
        time.sleep(0.1)



