import schedule
import time
import os
import sys
from django.core.management import call_command

# Override the .env file just for this script
os.environ['USE_CLOUD_DB'] = 'True' 

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diltru_app.settings')
import django
django.setup()

def job():
    print("\n--- Starting Scheduled Price Update ---")
    try:
        call_command('update_prices')
    except Exception as e:
        print(f"Job failed: {e}")
    print("--- ✓✓ Update Complete. Waiting for next run... ---\n")

# Schedule the job
schedule.every(30).minutes.do(job) # runs every 6 hours for rate limit compliance
print("::: Price Tracker Scheduler Started. :::")
print(":::       Press Ctrl+C to stop.      :::")

while True:
    schedule.run_pending()
    time.sleep(1)