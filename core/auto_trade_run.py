import os
import time
import schedule
import subprocess
from datetime import datetime

# Get the python interpreter
env = os.path.abspath("env")
venv = os.path.abspath("venv")

if env :
    python_path = rf"{env}\Scripts\python.exe"
elif venv:
    python_path = rf"{venv}\Scripts\python.exe"
else:
    python_path = "python"


def get_calendar_data():
    script_path = os.path.join(os.path.dirname(__file__), 'forex_calendar.py') 
    # os.system(f'python {script_path}')
    subprocess.run([python_path, script_path], check=True)

def run_auto_bot():
    script_path = os.path.join(os.path.dirname(__file__), 'Auto_Trade.py')
    os.system(f'python {script_path}')

# Schedule the job to run daily at 10:00
schedule.every().day.at("01:00").do(get_calendar_data)

schedule.every().day.at("01:02").do(run_auto_bot)

def run_automatically():
    print("auto bot triggered")
    while True:
        schedule.run_pending()
        time.sleep(20)
