from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('run-sync/', views.run_sync, name='run_sync'),
    path('applications/', views.applications_view, name='applications'),
    path('logs/', views.logs_view, name='logs'),
]