from django.shortcuts import render
from .models import PatentApplication

def dashboard(request):
    applications = PatentApplication.objects.prefetch_related("patentdocument_set").all()
    return render(request, "patents/dashboard.html", {"applications": applications})