from patents.models import PatentApplication

class Mapper:

    def find_application(self, parsed_data):
        app_no = parsed_data.get("application_number")

        try:
            app = PatentApplication.objects.get(application_number=app_no)
            print("✅ Found:", app_no)
            return app
        except PatentApplication.DoesNotExist:
            print("❌ Not Found:", app_no)
            return None