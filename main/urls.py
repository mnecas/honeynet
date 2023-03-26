from django.urls import path, include
from main.views import (
    IndexView,
    HoneypotView,
    ExportView,
    DeleteData,
    HoneynetAddView,
    HoneynetView,
    DeleteHoneynet,
    StartAnsibleDeploymentView,
    HoneypotAddView
)

urlpatterns = [
    path("honeynets/", HoneynetAddView.as_view()),
    path("honeynets/<uuid:pk>/", HoneynetView.as_view()),
    path("honeynets/<uuid:pk>/start", StartAnsibleDeploymentView.as_view()),
    path("honeynets/<uuid:pk>/delete", DeleteHoneynet.as_view()),

    path("honeynets/<uuid:hn_pk>/honeypots/", HoneypotAddView.as_view()),
    #TODO Remove extra url
    path("honeynets/<uuid:hn_pk>/honeypots/<uuid:hp_pk>", HoneypotView.as_view()),
    path("honeynets/<uuid:hn_pk>/honeypots/<uuid:hp_pk>/", HoneypotView.as_view()),
    path("honeynets/<uuid:hn_pk>/honeypots/<uuid:hp_pk>/delete", DeleteData.as_view()),
    path("honeynets/<uuid:hn_pk>/honeypots/<uuid:hp_pk>/export", ExportView.as_view()),
    path("", IndexView.as_view()),
]
