import logging
from users.models import SponsoredCustomer
from patents.models import PatentApplication

logger = logging.getLogger(__name__)

class Mapper:

    def verify_customer(self, customer_number):
        try:
            SponsoredCustomer.objects.get(customer_number=customer_number, active=True)
            logger.info(
                f"✅ Customer {customer_number} verified",
                extra={"application_number": "N/A", "customer_number": customer_number, "email_subject": "N/A"}
            )
            return True
        except SponsoredCustomer.DoesNotExist:
            logger.warning(
                f"❌ Customer {customer_number} not verified. Skipping.",
                extra={"application_number": "N/A", "customer_number": customer_number, "email_subject": "N/A"}
            )
            return False

    def find_application(self, parsed_data):
        app_no = parsed_data.get("application_number")

        if not app_no:
            return None

        try:
            app = PatentApplication.objects.get(application_number=app_no)
            logger.info(
                f"✅ Found application {app_no}",
                extra={
                    "application_number": app.application_number,
                    "customer_number": getattr(app, "customer_number", "N/A"),
                    "email_subject": "N/A"
                }
            )
            return app
        except PatentApplication.DoesNotExist:
            logger.warning(
                f"❌ Not Found application {app_no}",
                extra={"application_number": app_no, "customer_number": "N/A", "email_subject": "N/A"}
            )
            return None