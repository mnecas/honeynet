from django.urls import path, include
from main.views import IndexView, HoneypotView, ExportView, DeleteData, EditHoneypot

urlpatterns = [
    path("honeypots/<int:pk>/", HoneypotView.as_view()),
    path("honeypots/<int:pk>/delete-data", DeleteData.as_view()),
    path("honeypots/<int:pk>/export", ExportView.as_view()),
    path("honeypots/<int:pk>/edit", EditHoneypot.as_view()),
    path("", IndexView.as_view()),
]
