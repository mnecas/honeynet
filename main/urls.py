from django.urls import path, include
from main.views import (
    IndexView,
    HoneypotView,
    ExportView,
    DeleteData,
    EditHoneypot,
    HoneypotAddView,
)

urlpatterns = [
    path("add/", HoneypotAddView.as_view()),
    path("honeypots/<uuid:pk>/", HoneypotView.as_view()),
    path("honeypots/<uuid:pk>/delete", DeleteData.as_view()),
    path("honeypots/<uuid:pk>/export", ExportView.as_view()),
    path("honeypots/<uuid:pk>/edit", EditHoneypot.as_view()),
    path("", IndexView.as_view()),
]
