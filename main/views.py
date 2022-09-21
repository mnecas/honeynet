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


def honeypots(request):
    if request.method == "GET":
        data = serializers.serialize("json", Honeypot.objects.all())
        return HttpResponse(data, content_type="application/json")
    if request.method == "POST":
        honeypot, _ = Honeypot.objects.get_or_create(
            type=request.POST.get("type"),
            name=request.POST.get("name"),
        )
        data = serializers.serialize("json", [honeypot])
        return HttpResponse(data, content_type="application/json")


def honeypot(request, id):
    if request.method == "GET":
        data = serializers.serialize("json", Honeypot.objects.filter(id=id))
        return HttpResponse(data, content_type="application/json")
    if request.method == "POST":
        file = request.FILES.get("data", "")
        if not file:
            return BadRequest("No data file.")
        try:
            honeypot = Honeypot.objects.get(id=id)
        except Honeypot.DoesNotExist:
            return BadRequest("Honeypot does not exits.")
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        uploaded_file_url = fs.url(filename)
        AttackDump.objects.get_or_create(path=uploaded_file_url, honeypot=honeypot)
        return HttpResponse("OK")
