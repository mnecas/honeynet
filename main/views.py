from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from django.views.generic.base import TemplateView
from main.models import HoneypotAttack, Honeypot, AttackDump
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.core.files.storage import FileSystemStorage
import tarfile
import os.path
import tempfile


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["honeypots"] = Honeypot.objects.all()
        return context


class HoneypotView(TemplateView):
    template_name = "honeypot.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        honeypot = get_object_or_404(Honeypot, pk=kwargs["pk"])
        attacks = HoneypotAttack.objects.filter(honeypot=honeypot)

        keys = set()
        for attack in attacks:
            for key in attack.data:
                keys.add(key)

        dumps = AttackDump.objects.filter(honeypot=honeypot)

        context["honeypots"] = Honeypot.objects.all()
        context["honeypot"] = honeypot
        context["dumps"] = dumps
        context["attacks"] = attacks
        context["data_keys"] = keys
        return context


class ExportView(View):
    def post(self, request, pk):
        remove_checkbox = request.POST.get("remove_checkbox")
        join_checkbox = request.POST.get("join_checkbox")
        dumps_ids = request.POST.getlist("dumps_checkboxes")
        attacks_ids = request.POST.getlist("attacks_checkboxes")
        print(request.POST)
        print(attacks_ids)
        print(dumps_ids)
        print(join_checkbox)
        print(remove_checkbox)
        honeypot = Honeypot.objects.get(pk=pk)
        # attacks = HoneypotAttack.objects.filter(honeypot=honeypot, pk__in=attacks_ids)
        dumps = AttackDump.objects.filter(honeypot=honeypot, pk__in=dumps_ids)

        fs = FileSystemStorage()
        with tempfile.NamedTemporaryFile("wb", suffix=".tar.gz", delete=False) as f:
            with tarfile.open(fileobj=f, mode="w:gz") as tar:
                for dump in dumps:
                    file = fs.open(dump.path)
                    print(file)
                    tar.add(dump.path, arcname=os.path.basename(dump.path))

        # # filename = obj.model_attribute_name.path
        # response = FileResponse(open(f, 'rb'))
        # return response
