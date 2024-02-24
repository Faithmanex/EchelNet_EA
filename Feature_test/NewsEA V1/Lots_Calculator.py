import MetaTrader5 as mt5

def handle_mt5_error(message):
    print(message)
    mt5.shutdown()

# Connect to MetaTrader 5
if not mt5.initialize():
    handle_mt5_error("initialize() failed")

# Get account information
account_info = mt5.account_info() 
if account_info is None:
    handle_mt5_error("Get account information failed")

# Get symbol information
symbol = input("Enter a valid symbol: ")   # Input the desired symbol
while True:  # Input validation loop
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is not None:
        break
    else:
        symbol = input("Invalid symbol. Enter a valid symbol: ") 

# Risk management settings
account_risk_percentage = 25
stop_loss_pips = 5

# Broker-specific settings (Adjust as needed)
min_lot_size = 0.01  # Assuming your broker allows 0.01 lots
max_lot_size = 10.0  # Hypothetical max lot size
leverage = 100       # Example leverage value

# Calculate pip value dynamically 
if symbol_info.digits == 5:
    pip_value = symbol_info.trade_tick_size * 10
elif symbol_info.digits == 3:
    pip_value = symbol_info.trade_tick_size * symbol_info.trade_tick_value / 10
else:
    pip_value = symbol_info.trade_tick_size * 10

# Calculate lot size (consider broker restrictions)
account_balance = account_info.balance
risk_amount = account_balance * account_risk_percentage / 100
risk_in_pips = stop_loss_pips * pip_value
lot_size = (risk_amount / risk_in_pips) / symbol_info.trade_contract_size 
lot_size = max(min_lot_size, min(lot_size, max_lot_size))  # Clamp lot size
lot_size = f'{lot_size:.2f}'

print("Recommended lot size for", symbol, ":", lot_size)

# Disconnect from MetaTrader 5
mt5.shutdown()
