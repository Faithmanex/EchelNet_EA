import schedule
import time
import subprocess

# Function to run a script using subprocess
def run_script(script_name):
    subprocess.run(["python", script_name])

# Schedule the jobs
def schedule_jobs():
    schedule.every().day.at("00:00").do(run_script, "../core/forex_calendar.py")
    schedule.every().day.at("00:00").do(run_script, "../core/News.py")

# Initialize the scheduler
schedule_jobs()

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)