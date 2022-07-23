from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path("api/honeypot", views.honeypots),
    path("api/honeypot/<int:id>", views.honeypot),
]
