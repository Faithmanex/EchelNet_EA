import os
import sys
import json
import pytz
import time
import datetime
import threading
import tkinter as tk
import MetaTrader5 as mt5
import customtkinter as ctk
from tkinter import messagebox
sys.path.append("..")
from core import auto_trade_run
from core.News_Algo import TradingBot


mt5.initialize()


class TradingApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        # pass in the Tkinter instance as self
        self.tradingBot = TradingBot()

        self.title("EchelNet News Algo")
        self.geometry("550x600")
        ctk.set_appearance_mode("dark")

        # create a directory to save all json files
        directory_path = "..\\core\\json_data"
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        # Initialize the connection
        if not mt5.initialize():
            print("Failed to initialize, error code =", mt5.last_error())
            return

        # Get all symbols
        symbols = mt5.symbols_get()
        if symbols is None:
            print("No symbols found.")
            return
         # Extract the names of the symbols
        symbol_names = [symbol.name for symbol in symbols]
        
        # Labels
        
        self.symbol_label = ctk.CTkLabel(self, text="Symbol:", anchor="w", justify="left")
        self.symbol_label.grid(row=0, column=0, pady=5, padx=10, sticky="w")

        self.lot_label = ctk.CTkLabel(self, text="Lot:", anchor="w", justify="left")
        self.lot_label.grid(row=1, column=0, pady=5, padx=10, sticky="w")

        self.stop_loss_label = ctk.CTkLabel(self, text="Stop Loss:", anchor="w", justify="left")
        self.stop_loss_label.grid(row=2, column=0, pady=5, padx=10, sticky="w")

        self.stop_distance_label = ctk.CTkLabel(self, text="Stop Distance:", anchor="w", justify="left")
        self.stop_distance_label.grid(row=4, column=0, pady=5, padx=10, sticky="w")

        self.timeout_label = ctk.CTkLabel(self, text="Timeout:", anchor="w", justify="left")
        self.timeout_label.grid(row=5, column=0, pady=5, padx=10, sticky="w")

        self.news_time_label = ctk.CTkLabel(self, text="News Time (HH:MM:SS):", anchor="w", justify="left")
        self.news_time_label.grid(row=6, column=0, pady=5, padx=10, sticky="w")


        # Entries
        
        self.symbol_menu = ctk.CTkComboBox(self, values=symbol_names, width=150)
        self.symbol_menu.grid(row=0, column=1, pady=5, padx=10)
        
        self.lot_entry = ctk.CTkEntry(self, placeholder_text="0.5", width=60)
        self.lot_entry.insert(0, "0.5")
        self.lot_entry.grid(row=1, column=1, pady=5, padx=10, sticky="w")

        self.stop_loss_entry = ctk.CTkEntry(self, placeholder_text="30", width=60)
        self.stop_loss_entry.insert(0, "30")
        self.stop_loss_entry.grid(row=2, column=1, pady=5, padx=10, sticky="w")

        self.stop_distance_entry = ctk.CTkEntry(self, placeholder_text="Distance from Price", width=60)
        self.stop_distance_entry.insert(0, "30")
        self.stop_distance_entry.grid(row=4, column=1, pady=5, padx=10, sticky="w")

        # Timeout Entry
        self.timeout_entry = ctk.CTkEntry(self, placeholder_text="Timeout", width=60)
        self.timeout_entry.insert(0, "60")
        self.timeout_entry.grid(row=5, column=1, pady=5, padx=10, sticky="w")

        # Time Picker
        self.news_time_hour = ctk.CTkComboBox(self, values=[f"{i:02d}" for i in range(24)], width=60)
        self.news_time_hour.grid(row=6, column=1, pady=10, padx=10, sticky="w")
        self.news_time_minute = ctk.CTkComboBox(self, values=[f"{i:02d}" for i in range(60)], width=60)
        self.news_time_minute.grid(row=6, column=2, pady=10, padx=10, sticky="w")
        self.news_time_second = ctk.CTkComboBox(self, values=[f"{i:02d}" for i in range(60)], width=60)
        self.news_time_second.grid(row=6, column=3, pady=10, padx=10, sticky="w")
                
        # ... [previous code for labels and entries]

        # Start Trading Button
        self.start_button = ctk.CTkButton(self, text="Start Trading", command=self.start_trading_thread, fg_color="green")
        self.start_button.grid(row=7, column=0, columnspan=4, pady=5, padx=5)

        # Cancel All Pending Orders Button
        self.cancel_button = ctk.CTkButton(self, text="Cancel All Pending Orders", command=lambda: self.tradingBot.cancel_all_pending_orders(self.symbol), fg_color="red")
        self.cancel_button.grid(row=7, column=0, pady=10, padx=10)

        # Auto Trading Button
        self.start_button = ctk.CTkButton(self, text="Auto Trade", command=lambda: self.start_auto_trading_thread(), fg_color="blue")
        self.start_button.grid(row=7, column=2, columnspan=4, pady=5, padx=5)

        # ... [remaining code for output textbox and current time display]


        # Output Text Box
        self.output_text_box = ctk.CTkTextbox(self, height=150, width=300, font=("Arial", 12))
        self.output_text_box.grid(row=9, column=0, columnspan=4, pady=5, padx=10)
        self.output_text_box.bind('<KeyRelease>', self.adjust_height)

        # Current Time Display
        self.current_time_label = ctk.CTkLabel(self, text="")
        self.current_time_label.grid(row=8, column=2, columnspan=4, pady=5, padx=5)


    def adjust_height(self, event):
            text_content = event.widget.get('1.0', 'end')
            lines = text_content.split('\n')
            height = min(len(lines), 50) # Limit the maximum height to 50 lines
            event.widget.config(height=height)



    # Funtions 
    def update_time(self):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.current_time_label.configure(text=f"Current Time: {now}")
        self.after(1000, self.update_time)


    def automatic_run(self):
        self.get_user_data('auto')
        # run automatically
        auto_trade_run.run_automatically()
    
    def get_user_data(self, mode):
        lot = float(self.lot_entry.get())
        stop_loss = float(self.stop_loss_entry.get())
        stop_distance = float(self.stop_distance_entry.get())
        timeout = float(self.timeout_entry.get())

        data = {
            "lot": lot,
            "stop_loss": stop_loss,
            "stop_distance": stop_distance,
            "timeout": timeout
        }

        if mode == "auto":
            with open("../core/json_data/user_data.json", 'w') as file:
                json.dump(data, file, indent=4)
        elif mode == "start":
            return lot, stop_loss, stop_distance, timeout

    def start_trading(self):
        
        # Get the data
        self.lot, stop_loss, stop_distance, timeout = self.get_user_data("start")

        self.symbol = self.symbol_menu.get() 
        news_time_hour = self.news_time_hour.get() 
        news_time_minute = self.news_time_minute.get()
        news_time_second = self.news_time_second.get()
        news_time = f"{news_time_hour}:{news_time_minute}:{news_time_second}"

        self.output_text_box.insert(tk.END, f"Sending order for symbol: {self.symbol}\nTime: {news_time}\nLot Size: {self.lot}\nStop Loss: {stop_loss} points\nStop Distance: {stop_distance}\nTimeout: {timeout}\n\n")
        response, price, deviation, result, result1 = self.tradingBot.execute_trades(self.symbol, self.lot, stop_loss, stop_distance, news_time)

        # handle the responses from the trading bot
        self.handle_response(response, price, deviation, result, result1)


        #handle timeout
        if response == "order sent":
            # This is to add extra positon to the buy or sell stop when either of them is triggered
            # Used to cover losses and recover all
            BUY_MAGIC = 123456
            SELL_MAGIC = 654321
            self.tradingBot.check_triggered_orders(self.symbol, BUY_MAGIC, SELL_MAGIC, deviation)
                
            time.sleep(timeout)
            self.tradingBot.cancel_all_pending_orders(self.symbol)



    def handle_response(self, errorCode,price, deviation, result, result1):
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
            self.output_text_box.insert(tk.END, f"2. order_send failed, retcode={result.retcode} ({mt5.last_error()}), retcode1={result1.retcode} ({mt5.last_error()})\n")


    # Multithreading functions
            
    def start_trading_thread(self):
        # Create a new thread and run self.start_trading in that thread
        trading_thread = threading.Thread(target=self.start_trading)
        trading_thread.start()

    def start_auto_trading_thread(self):
        # Create a new thread and run self.start_trading in that thread

        trading_thread = threading.Thread(target=self.automatic_run)
        trading_thread.start()



if __name__ == "__main__":
    app = TradingApp()
    app.update_time()
    app.mainloop()

    # app.start_auto_trading_thread()