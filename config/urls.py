from django.urls import path, include

urlpatterns = [
    path("", include("patents.urls")),
    path('emails/', include('emails.urls')),
]