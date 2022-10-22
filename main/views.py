from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from django.views.generic.base import TemplateView
from main.models import HoneypotAttack, Honeypot, AttackDump
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.core.files.storage import FileSystemStorage
from api.serializers import HoneypotAttackSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User, Group
import tarfile
import os
import json
import tempfile
import uuid


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["honeypots"] = Honeypot.objects.all()
        return context


class HoneypotAddView(TemplateView):
    template_name = "honeypot_form.html"

    def post(self, request):
        honeypot_group = Group.objects.get(name="honeypot")

        user = User.objects.create_user(
            username="honeypot-{}-{}".format(
                request.POST.get("type"), str(uuid.uuid4())
            )
        )
        user.groups.add(honeypot_group)
        Token.objects.create(user=user)

        Honeypot.objects.create(
            name=request.POST.get("name"), type=request.POST.get("type"), author=user
        )
        return redirect("/")

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
        token = Token.objects.get(user=honeypot.author)
        context["honeypots"] = Honeypot.objects.all()
        context["honeypot"] = honeypot
        context["token"] = token
        context["dumps"] = dumps
        context["attacks"] = attacks
        context["data_keys"] = keys
        return context


class ExportView(View):
    def post(self, request, pk):
        join_checkbox = request.POST.get("join_checkbox")
        dumps_ids = request.POST.getlist("dumps_checkboxes")
        attacks_ids = request.POST.getlist("attacks_checkboxes")
        fs = FileSystemStorage()
        honeypot = Honeypot.objects.get(pk=pk)
        attacks = HoneypotAttack.objects.filter(honeypot=honeypot, pk__in=attacks_ids)
        dumps = AttackDump.objects.filter(honeypot=honeypot, pk__in=dumps_ids)
        dumps_files = list(map(lambda x: fs.open(x.path).name, dumps))
        # Create temporary tar.gz file to which we will add all selected items
        with tempfile.NamedTemporaryFile("wb", suffix=".tar.gz", delete=False) as f:
            with tarfile.open(fileobj=f, mode="w:gz") as tar:
                if attacks_ids:
                    data = HoneypotAttackSerializer(attacks, many=True).data
                    with open("/tmp/data.json", "w+") as data_file:
                        data_file.write(json.dumps(data))
                    tar.add(data_file.name, arcname=os.path.basename(data_file.name))

                if join_checkbox and dumps:
                    file = "/tmp/honeypot.pcap"
                    # Join all pcaps to one
                    os.system(
                        "mergecap -w {name} {pcap_list}".format(
                            name=file, pcap_list=" ".join(dumps_files)
                        )
                    )
                    tar.add(file, arcname=os.path.basename(file))
                    os.remove(file)
                else:
                    for file in dumps_files:
                        tar.add(file, arcname=os.path.basename(file))
        # Load the temporary to memory
        response = FileResponse(open(f.file.name, mode="rb"))
        # Cleanup before sending the file
        os.remove(f.file.name)
        return response


class DeleteData(View):
    def get(self, request, pk):
        honeypot = Honeypot.objects.get(pk=pk)
        honeypot.delete()
        return redirect("/")

    def post(self, request, pk):
        dumps_ids = request.POST.getlist("dumps_checkboxes")
        attacks_ids = request.POST.getlist("attacks_checkboxes")
        honeypot = Honeypot.objects.get(pk=pk)
        attacks = HoneypotAttack.objects.filter(honeypot=honeypot, pk__in=attacks_ids)
        dumps = AttackDump.objects.filter(honeypot=honeypot, pk__in=dumps_ids)
        for attack in attacks:
            attack.delete()
        for dump in dumps:
            dump.delete()
        return redirect(".")


class EditHoneypot(View):
    def post(self, request, pk):
        name = request.POST.get("name")
        type = request.POST.get("type")
        honeypot = Honeypot.objects.get(pk=pk)
        if name:
            honeypot.name = name
        if type:
            honeypot.type = type
        honeypot.save()
        return redirect(".")
