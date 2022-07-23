

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('api/honeypot', views.honeypot),
    path('api/data', views.data),
]
