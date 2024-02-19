import time
from News_Algo import TradingBot
import json
from datetime import datetime, timedelta, date


class AutoBot:
    def __init__(self, user_settings="./json_data/user_data.json", calendar='./json_data/forex_calendar.json'):
         # Open the JSON file
        with open(user_settings) as user_file:
            self.settings = json.load(user_file)
        
        with open(calendar) as file:
            self.calendar = json.load(file)

        self.trade = TradingBot()


    def filter_news(self) -> list[object]:
        # Define desired currencies and impacts
        desired_currencies = ["GBP", "USD", "EUR"]
        desired_impacts = ["high"]
        previous_date = None
        new_calendar_data = []

        for calendar_data in self.calendar:
        
             # Attach a date if none present
            if calendar_data["date"] == None:
                calendar_data["date"] = previous_date
            else:
                previous_date = calendar_data["date"]

            # Skip events with undesired impact or currency
            if calendar_data["impact"] not in desired_impacts or calendar_data["currency"] not in desired_currencies:
                continue

            new_calendar_data.append(calendar_data)
        
        # Filter the data to remove news with the same time
        filtered_data = [new_calendar_data[0]]

        for data in new_calendar_data[1:]:
            if data["date"] != filtered_data[-1]["date"]:
                filtered_data.append(data)

        return filtered_data
    
       
    def auto_trade(self) -> None:
        
        # Get the news events we'll be taking
        trading_news = self.filter_news()

        for news_event in trading_news:

            news_time = news_event["date"].split(' ')[1] # News time
            time_object = datetime.strptime(news_time, '%H:%M:%S').time()

            # change the news time to take it 3 seconds before the actual time
            new_news_time = str((datetime.combine(datetime.min, time_object) - timedelta(seconds=3)).time())

            # Converting the currency to a readable form by the terminal
            if news_event['currency'] == "GBP":
                currency = news_event['currency'] + "USD"
            elif news_event['currency'] == "EUR" or  news_event['currency'] == "USD":
                currency = "EURUSD"
            
            # Place the order
            response, _, deviation, _, _, = self.trade.execute_trades(currency, 
                                                    self.settings["lot"], 
                                                    self.settings["stop_loss"], 
                                                    self.settings["stop_distance"], 
                                                    new_news_time)
            

            #handle timeout
            if response == "order sent":
                # This is to add extra positon to the buy or sell stop when either of them is triggered
                # Used to cover losses and recover all
                BUY_MAGIC = 123456
                SELL_MAGIC = 654321
                self.trade.check_triggered_orders(currency, BUY_MAGIC, SELL_MAGIC, deviation)

                time.sleep(self.settings["timeout"])
                self.trade.cancel_all_pending_orders(currency)    


if __name__ == "__main__":
    run = AutoBot()
    run.auto_trade()