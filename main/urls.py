from django.urls import path, include
from main.views import (
    IndexView,
    HoneypotView,
    ExportView,
    DeleteData,
    EditHoneypot,
    HoneynetAddView,
    ViewHoneynet,
    DeleteHoneynet,
    StartAnsibleDeploymentView
)

urlpatterns = [
    path("honeynets/", HoneynetAddView.as_view()),
    path("honeynets/<uuid:pk>/", ViewHoneynet.as_view()),
    path("honeynets/<uuid:pk>/start", StartAnsibleDeploymentView.as_view()),
    path("honeynets/<uuid:pk>/delete", DeleteHoneynet.as_view()),
    path("honeypots/<uuid:pk>/", HoneypotView.as_view()),
    path("honeypots/<uuid:pk>/delete", DeleteData.as_view()),
    path("honeypots/<uuid:pk>/export", ExportView.as_view()),
    path("honeypots/<uuid:pk>/edit", EditHoneypot.as_view()),
    path("", IndexView.as_view()),
]
