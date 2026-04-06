from celery import shared_task

from emails.fetcher import EmailFetcher
from emails.parser import USPTOParser
from emails.mapper import Mapper
from emails.sync_service import SyncService
from patents.services.document_service import DocumentService


def extract_email_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()

            if content_type in ["text/plain", "text/html"]:
                return part.get_payload(decode=True).decode(errors="ignore")
    else:
        return msg.get_payload(decode=True).decode(errors="ignore")

    return ""


@shared_task
def process_uspto_emails():
    fetcher = EmailFetcher()  # ✅ FIXED

    emails = fetcher.fetch_unseen_emails()

    print(f"📬 Total emails fetched: {len(emails)}")

    parser = USPTOParser()
    mapper = Mapper()
    sync = SyncService()
    doc_service = DocumentService()

    for msg in emails:
        try:
            print("📩 Processing email...")

            body = extract_email_body(msg)

            parsed_list = parser.parse(body)

            print(f"📊 Parsed {len(parsed_list)} records")

            for parsed in parsed_list:
                print("📊 Data:", parsed)

                app = mapper.find_application(parsed)

                if app:
                    doc_service.save_document(app, parsed)
                    sync.trigger(app)

        except Exception as e:
            print("❌ Error processing email:", str(e))