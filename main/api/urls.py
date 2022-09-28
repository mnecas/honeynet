from django.urls import path, include, re_path
from rest_framework.urlpatterns import format_suffix_patterns
from main.api.views import HoneypotViewSet

honeypot_list = HoneypotViewSet.as_view({"get": "list", "post": "create"})

honeypot_detail = HoneypotViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)
honeypot_upload = HoneypotViewSet.as_view({"post": "upload"})

honeypot_attack = HoneypotViewSet.as_view({"post": "attack"})

urlpatterns = [
    path("honeypots/", honeypot_list),
    path("honeypots/<int:pk>/", honeypot_detail),
    path("honeypots/<int:pk>/upload", honeypot_upload),
    path("honeypots/<int:pk>/attack", honeypot_attack),
    path("api-auth/", include("rest_framework.urls")),
]

urlpatterns = format_suffix_patterns(urlpatterns)
