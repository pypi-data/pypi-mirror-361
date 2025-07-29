from django.urls import path
from . import views

app_name = "celery_eye"

urlpatterns = [
    path("download-log/", views.download_log, name="download_log"),
]
