from celery import Celery
from celery.schedules import crontab
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# --- CELERY BEAT SCHEDULE ---
app.conf.beat_schedule = {
    "fetch-uspto-emails-every-30-mins": {
        "task": "emails.tasks.process_uspto_emails",
        "schedule": crontab(minute='*/30'),  # Every 30 minutes
        "options": {"queue": "celery"},
    },
}