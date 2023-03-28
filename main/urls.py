from django.urls import path, include
from django.contrib.auth.decorators import login_required
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
    path("logout/", login_required(LogoutView.as_view()), name="logout"),
    path("honeynets/", login_required(HoneynetAddView.as_view()), name="honeynets"),
    path(
        "honeynets/<uuid:pk>/",
        login_required(HoneynetView.as_view()),
        name="honeynets_details",
    ),
    path(
        "honeynets/<uuid:pk>/start",
        login_required(StartAnsibleDeploymentView.as_view()),
        name="honeynets_start",
    ),
    path(
        "honeynets/<uuid:pk>/delete",
        login_required(DeleteHoneynet.as_view()),
        name="honeynets_delete",
    ),
    path(
        "honeynets/<uuid:hn_pk>/honeypots/",
        login_required(HoneypotAddView.as_view()),
        name="honeypots",
    ),
    path(
        "honeynets/<uuid:hn_pk>/honeypots/<uuid:hp_pk>/",
        login_required(HoneypotView.as_view()),
        name="honeypots_detail",
    ),
    path(
        "honeynets/<uuid:hn_pk>/honeypots/<uuid:hp_pk>/delete/",
        login_required(DeleteData.as_view()),
        name="honeypots_deletedata",
    ),
    path(
        "honeynets/<uuid:hn_pk>/honeypots/<uuid:hp_pk>/export/",
        login_required(ExportView.as_view()),
        name="honeypots_export",
    ),
    path("", login_required(IndexView.as_view())),
]
