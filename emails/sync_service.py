import logging
import time
from django.core.mail import send_mail
from django.conf import settings
from patents.models import PatentApplication

logger = logging.getLogger(__name__)

class SyncService:
    """
    Handles syncing patent applications, manages priority flag,
    adds exponential backoff retries and alert emails on repeated failures.
    """

    MAX_RETRIES = 5
    BASE_DELAY = 60  # seconds for first retry

    def mark_priority(self, application: PatentApplication):
        if not application.priority:
            application.priority = True
            application.save(update_fields=["priority"])
            logger.info(
                f"⚡ Priority set for {application.application_number}",
                extra={
                    "application_number": application.application_number,
                    "customer_number": getattr(application, "customer_number", "N/A"),
                    "email_subject": "N/A"
                }
            )

    def sync_application(self, application: PatentApplication):
        """
        Sync a single patent application with retries and alert emails.
        """
        attempt = 0

        while attempt <= self.MAX_RETRIES:
            try:
                logger.info(
                    f"🔥 Sync triggered for {application.application_number} (attempt {attempt + 1})",
                    extra={
                        "application_number": application.application_number,
                        "customer_number": getattr(application, "customer_number", "N/A"),
                        "email_subject": "N/A"
                    }
                )

                # TODO: Insert actual sync logic here
                # e.g., call USPTO API or process documents

                # Reset priority if it was set
                if application.priority:
                    application.priority = False
                    application.save(update_fields=["priority"])
                    logger.info(
                        f"✅ Priority reset for {application.application_number}",
                        extra={
                            "application_number": application.application_number,
                            "customer_number": getattr(application, "customer_number", "N/A"),
                            "email_subject": "N/A"
                        }
                    )
                return  # Success, exit loop

            except Exception as e:
                attempt += 1
                logger.error(
                    f"❌ Error syncing {application.application_number}: {e} (attempt {attempt})",
                    extra={
                        "application_number": getattr(application, "application_number", "N/A"),
                        "customer_number": getattr(application, "customer_number", "N/A"),
                        "email_subject": "N/A"
                    }
                )

                if attempt > self.MAX_RETRIES:
                    self.send_failure_alert(application, e)
                    break

                # Exponential backoff before retrying
                delay = self.BASE_DELAY * (2 ** (attempt - 1))
                logger.info(
                    f"⏳ Retrying {application.application_number} in {delay} seconds",
                    extra={
                        "application_number": getattr(application, "application_number", "N/A"),
                        "customer_number": getattr(application, "customer_number", "N/A"),
                        "email_subject": "N/A"
                    }
                )
                time.sleep(delay)

    def daily_sync(self):
        """
        Process all patent applications, prioritizing high-priority apps first.
        """
        try:
            priority_apps = PatentApplication.objects.filter(priority=True).order_by("id")
            normal_apps = PatentApplication.objects.filter(priority=False).order_by("id")

            logger.info(
                f"📌 High-priority apps count: {priority_apps.count()}",
                extra={"application_number": "N/A", "customer_number": "N/A", "email_subject": "N/A"}
            )
            logger.info(
                f"📌 Normal apps count: {normal_apps.count()}",
                extra={"application_number": "N/A", "customer_number": "N/A", "email_subject": "N/A"}
            )

            for app in priority_apps:
                self.sync_application(app)

            for app in normal_apps:
                self.sync_application(app)

            logger.info(
                "✅ Daily sync completed successfully",
                extra={"application_number": "N/A", "customer_number": "N/A", "email_subject": "N/A"}
            )

        except Exception as e:
            logger.error(
                f"❌ Daily sync failed: {e}",
                extra={"application_number": "N/A", "customer_number": "N/A", "email_subject": "N/A"}
            )
            raise e

    def send_failure_alert(self, application: PatentApplication, error: Exception):
        """
        Send email alert to admins if a sync repeatedly fails.
        """
        subject = f"[URGENT] Sync Failure for Application {application.application_number}"
        message = (
            f"Application Number: {application.application_number}\n"
            f"Customer Number: {getattr(application, 'customer_number', 'N/A')}\n"
            f"Error: {str(error)}\n"
            "The system failed to sync this application after multiple attempts."
        )
        admin_emails = [admin[1] for admin in settings.ADMINS]  # Django ADMINS setting

        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, admin_emails)
            logger.info(
                f"📧 Alert email sent for {application.application_number}",
                extra={
                    "application_number": application.application_number,
                    "customer_number": getattr(application, "customer_number", "N/A"),
                    "email_subject": "N/A"
                }
            )
        except Exception as mail_error:
            logger.error(
                f"❌ Failed to send alert email for {application.application_number}: {mail_error}",
                extra={
                    "application_number": getattr(application, "application_number", "N/A"),
                    "customer_number": getattr(application, "customer_number", "N/A"),
                    "email_subject": "N/A"
                }
            )