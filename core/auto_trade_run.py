import os
import time
import schedule
import subprocess
from datetime import datetime


def get_calendar_data():
    script_path = os.path.join(os.path.dirname(__file__), 'forex_calendar.py') 
    os.system(f'python {script_path}')

def run_auto_bot():
    script_path = os.path.join(os.path.dirname(__file__), 'Auto_Trade.py')
    os.system(f'python {script_path}')

# Schedule the job to run  at 10:00
schedule.every().day.at("00:10").do(get_calendar_data)

schedule.every().day.at("00:15").do(run_auto_bot)

def run_automatically():
    # change the current working directory
    os.chdir(os.path.dirname(__file__))
    print("Auto Bot started")
    while True:
        schedule.run_pending()
        time.sleep(10)


