from django.urls import path, include
from main.views import IndexView, HoneypotView

urlpatterns = [
    path("honeypots/<int:pk>", HoneypotView.as_view()),
    path("", IndexView.as_view()),
]
