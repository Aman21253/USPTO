import logging
from django.shortcuts import render, redirect
from patents.models import PatentApplication
from emails.tasks import daily_priority_sync
from django.utils.timezone import now
import os

LAST_SYNC_FILE = 'last_sync.txt'  # adjust to your last sync file location
LOG_FILE_PATH = 'celery.log'  # adjust to your celery log file location

logger = logging.getLogger(__name__)

def dashboard(request):
    priority_count = PatentApplication.objects.filter(priority=True).count()
    normal_count = PatentApplication.objects.filter(priority=False).count()
    total_count = priority_count + normal_count

    # 🔥 Recent activity (last 5)
    recent_apps = PatentApplication.objects.order_by('-id')[:5]

    # 🔥 Last sync time
    last_sync = None
    if os.path.exists(LAST_SYNC_FILE):
        with open(LAST_SYNC_FILE, "r") as f:
            last_sync = f.read()

    context = {
        'priority_count': priority_count,
        'normal_count': normal_count,
        'total_count': total_count,
        'recent_apps': recent_apps,
        'last_sync': last_sync
    }
    return render(request, 'emails/dashboard.html', context)


# 🔥 Run Sync Button
def run_sync(request):
    daily_priority_sync.delay()

    # Save last sync time
    with open(LAST_SYNC_FILE, "w") as f:
        f.write(str(now()))

    return redirect('dashboard')

def applications_view(request):
    applications = PatentApplication.objects.all().order_by('-id')
    return render(request, 'emails/applications.html', {'applications': applications})


def logs_view(request):
    logs = []
    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, 'r') as f:
            logs = f.readlines()[-1000:]  # last 1000 lines
    return render(request, 'emails/logs.html', {'logs': logs})