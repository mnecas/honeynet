from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from main.api import views as api_views

honeypot_list = api_views.HoneypotViewSet.as_view({"get": "list", "post": "create"})

honeypot_detail = api_views.HoneypotViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)

urlpatterns = [
    # path("honeypots/", api_views.HoneypotList.as_view()),
    # path("honeypots/<int:pk>/", api_views.HoneypotDetail.as_view()),
    path("honeypots/", honeypot_list),
    path("honeypots/<int:pk>/", honeypot_detail),
    path("api-auth/", include("rest_framework.urls")),
]

urlpatterns = format_suffix_patterns(urlpatterns)
