import schedule
import time
import os
import sys

# Setup Django Environment so we can run commands
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diltru_app.settings')
import django
django.setup()

from django.core.management import call_command

def job():
    print("\n--- Starting Scheduled Price Update ---")
    try:
        call_command('update_prices')
    except Exception as e:
        print(f"Job failed: {e}")
    print("--- ✓✓ Update Complete. Waiting for next run... ---\n")

# Schedule the job
# schedule.every(1).minutes.do(job) # runs every 1 minute, update to '.hours.do(job)' for rate-limit compliance
schedule.every(6).hours.do(job) # every 6 hours
print("::: Price Tracker Scheduler Started. :::")
print("Press Ctrl+C to stop.")

while True:
    schedule.run_pending()
    time.sleep(1)