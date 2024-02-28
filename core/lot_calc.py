import MetaTrader5 as mt5

def get_symbol_properties(symbol):
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"Symbol {symbol} not found. Please check the symbol.")
        return None
    return symbol_info

def get_currency_rate(symbol, account_currency, symbol_currency):
    if account_currency == symbol_currency:
        return 1.0  # No conversion needed for the same currency

    # Replace this with your method of obtaining the current exchange rate
    tick = mt5.symbol_info_tick(symbol)
    if tick is not None:
        return tick.bid
    else:
        print(f"Unable to retrieve tick information for symbol {symbol}")
        return None

def calculate_lot_size(account_balance, risk_percentage, stop_loss_points, symbol_properties, account_currency):
    if symbol_properties is None:
        return None

    contract_size = symbol_properties.trade_contract_size
    tick_size = symbol_properties.trade_tick_size
    symbol_currency = symbol_properties.currency_profit

    if symbol_currency != 'USD':
        exchange_rate = get_currency_rate(symbol_properties.name, account_currency, symbol_currency)
    else:
        exchange_rate = 1.0  # No conversion needed for USD

    risk_amount = (account_balance * risk_percentage) / 100
    lot_size = (risk_amount / (stop_loss_points * tick_size * contract_size)) * exchange_rate

    return lot_size

def main():
    mt5.initialize()

    # Replace 'EURUSD' with the desired symbol
    symbol = 'EURUSD'

    # Replace these values with your actual account balance, risk percentage, and stop loss in points
    account_balance = mt5.account_info().balance  # Example account balance
    risk_percentage = 10  # Example risk percentage
    stop_loss_points = 50  # Example stop loss in points

    # Replace 'USD' with your actual account currency
    account_currency = 'USD'

    symbol_properties = get_symbol_properties(symbol)
    if symbol_properties:
        lot_size = calculate_lot_size(account_balance, risk_percentage, stop_loss_points, symbol_properties, account_currency)
        if lot_size is not None:
            print(f"Lot size for {symbol}: {lot_size:.2f} lots")

    mt5.shutdown()

if __name__ == "__main__":
    main()
