"""
Notification services for DilTru price alerts.

Handles email delivery in background threads so the caller
(model save, management command, etc.) is never blocked by SMTP I/O.
"""
import logging
import threading

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_price_alert_email(alert):
    """
    Send an email notifying the user that a tracked product has hit
    their target price.  Runs in a background thread (fire-and-forget).

    Args:
        alert: A ``PriceAlert`` instance with ``product`` and ``owner``
               already loaded.
    """
    def _send_task():
        try:
            formatted_price = f"{int(alert.product.current_price):,d}"
            formatted_target = f"{int(alert.target_price):,d}"

            subject = (
                f"\U0001f3f7\ufe0f Price Drop Alert!: "
                f"{alert.product.name[:30]}... is KSh {formatted_price}!"
            )
            message = (
                f"Good news!\n\n"
                f"The item '{alert.product.name}' you are tracking "
                f"has dropped to KSh {formatted_price}.\n"
                f"Your target was KSh {formatted_target}.\n\n"
                f"Buy it now: {alert.product.jumia_url}\n\n"
                f"Happy Shopping,\n"
                f"The DilTru Team \U0001f600"
            )

            logger.info("Sending price-alert email to %s …", alert.owner.email)
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [alert.owner.email],
                fail_silently=False,
            )
            logger.info("Email sent successfully to %s.", alert.owner.email)
        except Exception:
            logger.exception(
                "Failed to send price-alert email to %s", alert.owner.email
            )

    email_thread = threading.Thread(target=_send_task, daemon=True)
    email_thread.start()
