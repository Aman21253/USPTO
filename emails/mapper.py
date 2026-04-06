from users.models import SponsoredCustomer
from patents.models import PatentApplication

class Mapper:

    def verify_customer(self, customer_number):
        try:
            customer = SponsoredCustomer.objects.get(customer_number=customer_number, active=True)
            return True
        except SponsoredCustomer.DoesNotExist:
            print(f"❌ Customer {customer_number} not verified. Skipping.")
            return False

    def find_application(self, parsed_data):
        app_no = parsed_data.get("application_number")

        if not app_no:
            return None

        try:
            app = PatentApplication.objects.get(application_number=app_no)
            print("✅ Found:", app_no)
            return app
        except PatentApplication.DoesNotExist:
            print("❌ Not Found:", app_no)
            return None