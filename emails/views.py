from django.http import HttpResponse
from .tasks import process_uspto_emails

def run_task(request):
    process_uspto_emails.delay()  # Celery async
    return HttpResponse("✅ Task triggered! Check terminal.")