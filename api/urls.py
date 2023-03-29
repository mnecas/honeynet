from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from api.views import HoneypotViewSet

honeypot_list = HoneypotViewSet.as_view({"get": "list", "post": "create"})

honeypot_detail = HoneypotViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)
honeypot_upload = HoneypotViewSet.as_view({"post": "upload"})

honeypot_attack = HoneypotViewSet.as_view({"post": "attack"})

urlpatterns = [
    # path("<uuid:pk>/", honeypot_detail, name="honeypot"),
    path("<uuid:pk>/upload", honeypot_upload, name="upload"),
    path("<uuid:pk>/attack", honeypot_attack, name="attack"),
    # path("", honeypot_list, name="honeypots"),
    # path("api-auth/", include("rest_framework.urls")),
]

urlpatterns = format_suffix_patterns(urlpatterns)
