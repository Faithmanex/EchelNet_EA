import tkinter as tk
import customtkinter as ctk
import datetime
import pytz
import time
import MetaTrader5 as mt5
from tkinter import messagebox
import threading
from News_Algo import TradingBot

class TradingApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        # pass in the Tkinter instance as self
        self.tradingBot = TradingBot(self)

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
        self.symbol = self.symbol_entry.get()
        self.lot = float(self.lot_entry.get())
        stop_loss = float(self.stop_loss_entry.get())
        take_profit = float(self.take_profit_entry.get())
        stop_distance = float(self.stop_distance_entry.get())
        news_time_hour = self.news_time_hour.get()
        news_time_minute = self.news_time_minute.get()
        news_time_second = self.news_time_second.get()
        news_time = f"{news_time_hour}:{news_time_minute}:{news_time_second}"

        self.output_text_box.insert(tk.END, f"Starting Trading Bot for symbol: {self.symbol}\n")
        error, price, deviation, result, result1 = self.tradingBot.execute_trades(self.symbol, self.lot, stop_loss, take_profit, stop_distance, news_time)

        # handle the responses from the trading bot
        self.handle_error(error, price, deviation, result, result1)

    def handle_error(self, errorCode,price, deviation, result, result1):
        if errorCode == "initialise error":
            self.output_text_box.insert(tk.END, "initialize() failed, error code = {}\n".format(mt5.last_error()))
        elif errorCode == "symbol not found":
            self.output_text_box.insert(tk.END, "{} not found, can not call order_check()\n".format(self.symbol))
        elif errorCode == "symbol not visible":
            self.output_text_box.insert(tk.END, "{} is not visible, trying to switch on\n".format(self.symbol))
        elif errorCode == "symbol not selected":
            self.output_text_box.insert(tk.END, "symbol_select({}) failed, exit\n".format(self.symbol))
        elif errorCode == "order sent":
            self.output_text_box.insert(tk.END, "1. order_send(): by {} {} lots at {} with deviation={} points\n".format(self.symbol, self.lot, price, deviation))
        elif errorCode == "order sent error":
            self.output_text_box.insert(tk.END, "2. order_send failed, retcode={} ({}), retcode1={} ({})\n".format(
                        result.retcode, mt5.last_error(), result1.retcode, mt5.last_error()
                    ))


    def start_trading_thread(self):
        # Create a new thread and run self.start_trading in that thread
        trading_thread = threading.Thread(target=self.start_trading)
        trading_thread.start()

    def update_time(self):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.current_time_label.configure(text=f"Current Time: {now}")
        self.after(1000, self.update_time)

if __name__ == "__main__":
    app = TradingApp()
    app.update_time()
    app.mainloop()