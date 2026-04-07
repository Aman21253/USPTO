from celery import shared_task
import logging

from emails.fetcher import EmailFetcher
from emails.parser import USPTOParser
from emails.mapper import Mapper
from emails.sync_service import SyncService
from patents.services.document_service import DocumentService

logger = logging.getLogger(__name__)
USPTO_SUBJECT_PREFIX = (
    "USPTO: Patent Electronic System - Correspondence Notification for Customer Number"
)


def extract_email_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() in ["text/plain", "text/html"]:
                return part.get_payload(decode=True).decode(errors="ignore")
    else:
        return msg.get_payload(decode=True).decode(errors="ignore")
    return ""


@shared_task(bind=True, max_retries=3)
def process_uspto_emails(self):
    try:
        fetcher = EmailFetcher()
        emails = fetcher.fetch_unseen_emails()
        logger.info(
            f"Total emails fetched: {len(emails)}",
            extra={"application_number": "N/A", "customer_number": "N/A", "email_subject": "N/A"}
        )

        parser = USPTOParser()
        mapper = Mapper()
        sync = SyncService()
        doc_service = DocumentService()

        for msg in emails:
            sender = msg.get("From", "")
            subject = msg.get("Subject", "")

            if "noreply@uspto.gov" not in sender.lower():
                logger.info(
                    f"Skipping non-USPTO message from {sender}",
                    extra={"application_number": "N/A", "customer_number": "N/A", "email_subject": subject}
                )
                continue

            if USPTO_SUBJECT_PREFIX.lower() not in subject.lower():
                logger.info(
                    f"Skipping unsupported USPTO email subject: {subject}",
                    extra={"application_number": "N/A", "customer_number": "N/A", "email_subject": subject}
                )
                continue

            body = extract_email_body(msg)
            parsed_list = parser.parse(subject, body)
            if not parsed_list:
                logger.info(
                    f"No correspondence rows found in USPTO email",
                    extra={"application_number": "N/A", "customer_number": "N/A", "email_subject": subject}
                )
                continue

            customer_number = parsed_list[0].get("customer_number")
            if not mapper.verify_customer(customer_number):
                logger.warning(
                    f"Customer {customer_number} not verified. Skipping.",
                    extra={"application_number": "N/A", "customer_number": customer_number, "email_subject": subject}
                )
                continue

            for parsed in parsed_list:
                app = mapper.find_application(parsed)
                if not app:
                    continue

                doc_service.save_document(app, parsed)
                sync.mark_priority(app)

                logger.info(
                    f"Processed application {app.application_number} for customer {customer_number}",
                    extra={
                        "application_number": app.application_number,
                        "customer_number": customer_number,
                        "email_subject": subject
                    }
                )

    except Exception as exc:
        logger.error(
            f"Task failed: {str(exc)}. Retrying...",
            extra={"application_number": "N/A", "customer_number": "N/A", "email_subject": "N/A"}
        )
        self.retry(exc=exc, countdown=60)


@shared_task(name="emails.tasks.daily_priority_sync")
def daily_priority_sync():
    sync = SyncService()
    sync.daily_sync()