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
    HoneypotAddView,
    LogoutView,
    LoginView,
)

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LoginView.as_view(), name="logout"),
    path("honeynets/", HoneynetAddView.as_view(), name="honeynets"),
    path("honeynets/<uuid:pk>/", HoneynetView.as_view(), name="honeynets_details"),
    path(
        "honeynets/<uuid:pk>/start",
        StartAnsibleDeploymentView.as_view(),
        name="honeynets_start",
    ),
    path(
        "honeynets/<uuid:pk>/delete", DeleteHoneynet.as_view(), name="honeynets_delete"
    ),
    path(
        "honeynets/<uuid:hn_pk>/honeypots/", HoneypotAddView.as_view(), name="honeypots"
    ),
    path(
        "honeynets/<uuid:hn_pk>/honeypots/<uuid:hp_pk>/",
        HoneypotView.as_view(),
        name="honeypots_detail",
    ),
    path(
        "honeynets/<uuid:hn_pk>/honeypots/<uuid:hp_pk>/delete/",
        DeleteData.as_view(),
        name="honeypots_deletedata",
    ),
    path(
        "honeynets/<uuid:hn_pk>/honeypots/<uuid:hp_pk>/export/",
        ExportView.as_view(),
        name="honeypots_export",
    ),
    path("", IndexView.as_view()),
]
