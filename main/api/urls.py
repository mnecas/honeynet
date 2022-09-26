from django.urls import path, include, re_path
from rest_framework.urlpatterns import format_suffix_patterns
from main.api.views import HoneypotViewSet, FileUploadView

honeypot_list = HoneypotViewSet.as_view({"get": "list", "post": "create"})

honeypot_detail = HoneypotViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)

urlpatterns = [
    path("honeypots/", honeypot_list),
    path("honeypots/<int:pk>/", honeypot_detail),
    path("honeypots/<int:pk>/upload", FileUploadView.as_view()),
    # path("honeypots/<int:pk>/data", FileUploadView.as_view()),
    path("api-auth/", include("rest_framework.urls")),
]

urlpatterns = format_suffix_patterns(urlpatterns)
