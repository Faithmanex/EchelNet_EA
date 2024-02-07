import matplotlib.pyplot as plt
import MetaTrader5 as mt5

# Initialize MT5 connection
if not mt5.initialize():
    print("initialize() failed")
    mt5.shutdown()

# Get account info
account_info = mt5.account_info()

# Extract balance from account_info
balance = account_info.balance

# Plot balance
plt.figure(figsize=(10, 5))
plt.bar(['Balance'], [balance])
plt.title('Account Balance Summary')
plt.xlabel('Account Parameter')
plt.ylabel('Value')
plt.show()

# Shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
