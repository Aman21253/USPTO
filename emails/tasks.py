from celery import shared_task
import logging

from emails.fetcher import EmailFetcher
from emails.parser import USPTOParser
from emails.mapper import Mapper
from emails.sync_service import SyncService
from patents.services.document_service import DocumentService

logger = logging.getLogger(__name__)

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
        logger.info(f"Total emails fetched: {len(emails)}")

        parser = USPTOParser()
        mapper = Mapper()
        sync = SyncService()
        doc_service = DocumentService()

        for msg in emails:
            body = extract_email_body(msg)
            parsed_list = parser.parse(body)

            for parsed in parsed_list:
                customer_number = parsed.get("customer_number")
                if not mapper.verify_customer(customer_number):
                    logger.warning(f"Customer {customer_number} not verified. Skipping.")
                    continue

                app = mapper.find_application(parsed)
                if app:
                    doc_service.save_document(app, parsed)
                    sync.trigger(app)

    except Exception as exc:
        logger.error(f"Task failed: {str(exc)}. Retrying...")
        self.retry(exc=exc, countdown=60)