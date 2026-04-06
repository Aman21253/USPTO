from patents.models import PatentDocument
from datetime import datetime

class DocumentService:

    def save_document(self, application, parsed_data):
        doc_code = parsed_data.get("document_code")
        date_str = parsed_data.get("mailroom_date")

        # Convert string → date
        mail_date = datetime.strptime(date_str, "%m/%d/%Y").date()

        obj, created = PatentDocument.objects.get_or_create(
            application=application,
            document_code=doc_code,
            mailroom_date=mail_date
        )

        if created:
            print(f"✅ Saved: {doc_code}")
        else:
            print(f"⚠️ Duplicate skipped: {doc_code}")

        return obj