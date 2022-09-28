from django.shortcuts import render
from django.core import serializers
from django.http import HttpResponse
from main.models import Honeypot, AttackDump
from django.core.exceptions import BadRequest
from django.core.files.storage import FileSystemStorage
from main.api.serializers import HoneypotSerializer, AttackerSerializer
from rest_framework.response import Response


def index(request):
    if request.method == "GET":
        return render(request, "index.html", {})
