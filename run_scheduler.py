"""
Standalone scheduler that invokes the ``update_prices`` management command
at regular intervals.

Usage:
    python run_scheduler.py
"""
import logging
import os
import time

import schedule

# Override the .env file just for this script — always target the cloud DB
os.environ['USE_CLOUD_DB'] = 'True'

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diltru_app.settings')
import django  # noqa: E402
django.setup()

from django.core.management import call_command  # noqa: E402

logger = logging.getLogger(__name__)


def job():
    logger.info("Starting scheduled price update…")
    try:
        call_command('update_prices')
    except Exception:
        logger.exception("Scheduled price-update job failed")
    logger.info("Update complete. Waiting for next run…")


# Schedule the job — runs every 30 minutes
schedule.every(30).minutes.do(job)

logger.info("Price Tracker Scheduler started. Press Ctrl+C to stop.")

job()

while True:
    schedule.run_pending()
    time.sleep(1)