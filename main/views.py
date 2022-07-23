from django.shortcuts import render
from django.core import serializers
from django.http import HttpResponse
from main.models import Honeypot, HoneypotData


def index(request):
    if request.method == 'GET':
        return render(request, 'index.html', {})

def honeypot(request):
    if request.method == 'GET':
        data = serializers.serialize('json', Honeypot.objects.all())
        return HttpResponse(data, content_type='application/json')

def data(request):
    if request.method == 'GET':
        data = serializers.serialize('json', HoneypotData.objects.all())
        return HttpResponse(data, content_type='application/json')
