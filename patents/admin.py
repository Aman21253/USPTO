from django.contrib import admin
from .models import PatentApplication, PatentDocument

admin.site.register(PatentApplication)
admin.site.register(PatentDocument)