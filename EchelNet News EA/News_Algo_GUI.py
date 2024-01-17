import tkinter as tk
import customtkinter as ctk
import datetime
import pytz
import time
import MetaTrader5 as mt5
from tkinter import messagebox
import threading

class TradingApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("EchelNet News Algo")
        self.geometry("600x400")
        ctk.set_appearance_mode("dark")

        # Labels
        self.symbol_label = ctk.CTkLabel(self, text="Symbol:")
        self.symbol_label.grid(row=0, column=0, pady=10, padx=10)

        self.lot_label = ctk.CTkLabel(self, text="Lot:")
        self.lot_label.grid(row=1, column=0, pady=10, padx=10)

        self.stop_loss_label = ctk.CTkLabel(self, text="Stop Loss:")
        self.stop_loss_label.grid(row=2, column=0, pady=10, padx=10)

        self.take_profit_label = ctk.CTkLabel(self, text="Take Profit:")
        self.take_profit_label.grid(row=3, column=0, pady=10, padx=10)

        self.stop_distance_label = ctk.CTkLabel(self, text="Stop Distance:")
        self.stop_distance_label.grid(row=4, column=0, pady=10, padx=10)

        self.news_time_label = ctk.CTkLabel(self, text="News Time (HH:MM:SS):")
        self.news_time_label.grid(row=5, column=0, pady=10, padx=10)

        # Entries
        self.symbol_entry = ctk.CTkEntry(self, placeholder_text="USDJPY", width=200)
        self.symbol_entry.grid(row=0, column=1, pady=10, padx=10)

        self.lot_entry = ctk.CTkEntry(self, placeholder_text="0.5", width=200)
        self.lot_entry.grid(row=1, column=1, pady=10, padx=10)

        self.stop_loss_entry = ctk.CTkEntry(self, placeholder_text="35", width=200)
        self.stop_loss_entry.grid(row=2, column=1, pady=10, padx=10)

        self.take_profit_entry = ctk.CTkEntry(self, placeholder_text="150", width=200)
        self.take_profit_entry.grid(row=3, column=1, pady=10, padx=10)

        self.stop_distance_entry = ctk.CTkEntry(self, placeholder_text="35", width=200)
        self.stop_distance_entry.grid(row=4, column=1, pady=10, padx=10)

        # Time Picker
        self.news_time_hour = ctk.CTkComboBox(self, values=[f"{i:02d}" for i in range(24)], width=60)
        self.news_time_hour.grid(row=5, column=1, pady=10, padx=10, sticky="ew")
        self.news_time_minute = ctk.CTkComboBox(self, values=[f"{i:02d}" for i in range(60)], width=60)
        self.news_time_minute.grid(row=5, column=2, pady=10, padx=10, sticky="ew")
        self.news_time_second = ctk.CTkComboBox(self, values=[f"{i:02d}" for i in range(60)], width=60)
        self.news_time_second.grid(row=5, column=3, pady=10, padx=10, sticky="ew")

        # Button
        self.start_button = ctk.CTkButton(self, text="Start Trading", command=self.start_trading_thread, fg_color="green")
        self.start_button.grid(row=6, column=0, columnspan=4, pady=10, padx=5)

        # Output Text Box
        self.output_text_box = ctk.CTkTextbox(self, height=10, width=200)
        self.output_text_box.grid(row=7, column=0, columnspan=4, pady=5, padx=10)

        # Current Time Display
        self.current_time_label = ctk.CTkLabel(self, text="")
        self.current_time_label.grid(row=6, column=2, columnspan=4, pady=10, padx=5)

    def start_trading(self):
        symbol = self.symbol_entry.get()
        lot = float(self.lot_entry.get())
        stop_loss = float(self.stop_loss_entry.get())
        take_profit = float(self.take_profit_entry.get())
        stop_distance = float(self.stop_distance_entry.get())
        news_time_hour = self.news_time_hour.get()
        news_time_minute = self.news_time_minute.get()
        news_time_second = self.news_time_second.get()
        news_time = f"{news_time_hour}:{news_time_minute}:{news_time_second}"

        self.output_text_box.insert(tk.END, f"Starting Trading Bot for symbol: {symbol}\n")
        self.execute_trades(symbol, lot, stop_loss, take_profit, stop_distance, news_time)

    def start_trading_thread(self):
        # Create a new thread and run self.start_trading in that thread
        trading_thread = threading.Thread(target=self.start_trading)
        trading_thread.start()

    def execute_trades(self, symbol, lot, stop_loss, take_profit, stop_distance, news_time):
        # create a timezone object for WAT
        wat = pytz.timezone('Africa/Lagos')

        # establish connection to the MetaTrader 5 terminal
        if not mt5.initialize():
            self.output_text_box.insert(tk.END, "initialize() failed, error code = {}\n".format(mt5.last_error()))
            return

        # prepare the buy request structure
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            self.output_text_box.insert(tk.END, "{} not found, can not call order_check()\n".format(symbol))
            mt5.shutdown()
            return

        if not symbol_info.visible:
            self.output_text_box.insert(tk.END, "{} is not visible, trying to switch on\n".format(symbol))
            if not mt5.symbol_select(symbol, True):
                self.output_text_box.insert(tk.END, "symbol_select({}) failed, exit\n".format(symbol))
                mt5.shutdown()
                return

        point = symbol_info.point
        price = mt5.symbol_info_tick(symbol).ask
        deviation = 20

        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY_STOP,
            "price": price + stop_distance * point,
            "sl": price - stop_loss * point,
            "deviation": deviation,
            "magic": 234000,
            "comment": "EchelNet News EA",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }

        request1 = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_SELL_STOP,
            "price": price - stop_distance * point,
            "sl": price + stop_loss * point,
            "deviation": deviation,
            "magic": 235000,
            "comment": "EchelNet Sniper",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }

        # start the time loop
        while True:
            now_wat = datetime.datetime.now(wat)
            formatted_time = now_wat.strftime("%H:%M:%S")
            self.output_text_box.insert(tk.END, "{}\n".format(formatted_time))

            if formatted_time == news_time:
                result = mt5.order_send(request)
                result1 = mt5.order_send(request1)
                self.output_text_box.insert(tk.END, "1. order_send(): by {} {} lots at {} with deviation={} points\n".format(symbol, lot, price, deviation))
                if result.retcode != mt5.TRADE_RETCODE_DONE or result1.retcode != mt5.TRADE_RETCODE_DONE:
                    self.output_text_box.insert(tk.END, "2. order_send failed, retcode={} ({}), retcode1={} ({})\n".format(
                        result.retcode, mt5.last_error(), result1.retcode, mt5.last_error()
                    ))
                break

            time.sleep(0.1)

        mt5.shutdown()

        pass

    def update_time(self):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.current_time_label.configure(text=f"Current Time: {now}")
        self.after(1000, self.update_time)

if __name__ == "__main__":
    app = TradingApp()
    app.update_time()
    app.mainloop()
