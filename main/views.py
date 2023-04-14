from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from django.views.generic.base import TemplateView
from main.models import HoneypotAttack, Honeypot, AttackDump, Honeynet
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.core.files.storage import FileSystemStorage
from api.serializers import HoneypotAttackSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User, Group
from main.management.commands.config import Command as HoneypotGroupInit
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from main.tools.deployment import HoneypotDeployment
from main.forms import HoneynetForm, HoneypotForm
import tarfile
import os
import json
import tempfile
import uuid
import shutil
import yaml


def get_honeypots():
    return {
        item: Honeypot.objects.filter(honeynet=item) for item in Honeynet.objects.all()
    }


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["honeynets"] = get_honeypots()
        return context


class HoneypotAddView(View):
    template_name = "honeypots.html"

    def get(self, request, hn_pk):
        honeynet = get_object_or_404(Honeynet, pk=hn_pk)
        resp = {}
        resp["honeynets"] = get_honeypots()
        resp["selected"] = honeynet
        return render(request, "honeypots.html", resp)

    def post(self, request, hn_pk):
        if not Group.objects.filter(name="honeypot").exists():
            HoneypotGroupInit().handle()
        honeypot_group = Group.objects.get(name="honeypot")
        user = User.objects.create_user(
            username="honeypot-{}".format(str(uuid.uuid4()))
        )
        user.groups.add(honeypot_group)
        Token.objects.create(user=user)
        honeypot = Honeypot(
            id=uuid.uuid4(),
            name=request.POST.get("name"),
            author=user,
            honeynet=Honeynet.objects.get(id=hn_pk),
            tcpdump_filter=request.POST.get("tcpdump_filter"),
            tcpdump_timeout=int(request.POST.get("tcpdump_timeout", 3600)),
            tcpdump_max_size=int(request.POST.get("tcpdump_max_size", 100)),
            tcpdump_extra_args=request.POST.get("tcpdump_extra_args"),
            image=request.POST.get("image"),
            ports=request.POST.get("ports"),
        )

        deployment = HoneypotDeployment(honeypot)
        result = deployment.up()
        if result.returncode == 0:
            honeypot.save()
            return redirect(reverse("honeynets_details", kwargs={"hn_pk": hn_pk}))


        honeynet = get_object_or_404(Honeynet, pk=hn_pk)
        resp = {}
        resp["honeynets"] = get_honeypots()
        resp["selected"] = honeynet
        resp["honeypot"] = honeypot
        resp["error"] = result.stderr

        return render(request, "honeypots.html", resp)

class HoneypotView(TemplateView):
    template_name = "honeypot.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        honeypot = get_object_or_404(Honeypot, pk=kwargs["hp_pk"])
        honeynet = get_object_or_404(Honeynet, pk=kwargs["hn_pk"])
        attacks = HoneypotAttack.objects.filter(honeypot=honeypot)

        keys = set()
        for attack in attacks:
            for key in attack.data:
                keys.add(key)

        dumps = AttackDump.objects.filter(honeypot=honeypot)
        token = Token.objects.get(user=honeypot.author)
        context["honeynets"] = get_honeypots()
        context["selected"] = honeypot
        context["honeypot"] = honeypot
        context["honeynet"] = honeynet
        context["token"] = token
        context["dumps"] = dumps
        context["attacks"] = attacks
        context["data_keys"] = keys
        return context

    # Edit the honeypot
    def post(self, request, hn_pk, hp_pk):
        honeypot = Honeypot.objects.filter(id=hp_pk)
        honeypot.update(
            name=request.POST.get("name"),
            tcpdump_filter=request.POST.get("tcpdump_filter"),
            tcpdump_timeout=int(request.POST.get("tcpdump_timeout", 3600)),
            tcpdump_max_size=int(request.POST.get("tcpdump_max_size", 100)),
            tcpdump_extra_args=request.POST.get("tcpdump_extra_args"),
            image=request.POST.get("image"),
            ports=request.POST.get("ports"),
        )
        return redirect(".")


class ExportView(View):
    def post(self, request, hn_pk, hp_pk):
        join_checkbox = request.POST.get("join_checkbox")
        dumps_ids = request.POST.getlist("dumps_checkboxes")
        attacks_ids = request.POST.getlist("attacks_checkboxes")
        fs = FileSystemStorage()
        honeypot = Honeypot.objects.get(pk=hp_pk)
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
        response = FileResponse(open(f.name, mode="rb"))
        # Cleanup before sending the file
        os.remove(f.name)
        return response


class HoneynetView(TemplateView):
    template_name = "honeynet.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        honeynet = get_object_or_404(Honeynet, pk=kwargs["hn_pk"])

        context["honeynets"] = get_honeypots()
        context["honeynet"] = honeynet
        context["selected"] = honeynet
        context["honeypots"] = Honeypot.objects.filter(honeynet=honeynet)
        return context

    # Edit
    def post(self, request, hn_pk):
        honeynet = Honeynet.objects.get(id=hn_pk)
        if request.POST.get("name") != "":
            honeynet.name = request.POST.get("name")
        honeynet.save()
        return redirect(".")


class HoneynetAddView(TemplateView):
    template_name = "honeynet.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["honeynets"] = get_honeypots()
        context["form"] = HoneynetForm()
        return context

    def post(self, request):
        form = HoneynetForm(request.POST)
        # check whether it's valid:

        if form.is_valid():
            honeynet = Honeynet.objects.create(
                name=form.cleaned_data.get("name"),
            )
            return redirect(
                reverse("honeynets_details", kwargs={"hn_pk": str(honeynet.id)})
            )
        else:
            form = HoneynetForm()
            return render(request, "honeynet.html", {"form": form})


class DeleteHoneypot(View):
    def get(self, request, hn_pk, hp_pk):
        honeypot = Honeypot.objects.get(pk=hp_pk)
        honeypot.delete()
        return redirect(reverse("honeynets_details", kwargs={"hn_pk": hn_pk}))


class DeleteData(View):
    def post(self, request, hn_pk, hp_pk):
        dumps_ids = request.POST.getlist("dumps_checkboxes")
        attacks_ids = request.POST.getlist("attacks_checkboxes")
        honeypot = Honeypot.objects.get(pk=hp_pk)
        attacks = HoneypotAttack.objects.filter(honeypot=honeypot, pk__in=attacks_ids)
        dumps = AttackDump.objects.filter(honeypot=honeypot, pk__in=dumps_ids)
        for attack in attacks:
            attack.delete()
        for dump in dumps:
            dump.delete()
        return redirect(
            reverse("honeypots_detail", kwargs={"hn_pk": hn_pk, "hp_pk": hp_pk})
        )


class DeleteHoneynet(View):
    def get(self, request, hn_pk):
        honeynet = Honeynet.objects.get(pk=hn_pk)
        honeynet.delete()
        return redirect("/")


class LoginView(View):
    def get(self, request):
        form = AuthenticationForm(request)
        return render(request, "login.html", {"form": form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("/")
        else:
            form = AuthenticationForm(request)
        return render(request, "login.html", {"form": form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("/")

    def post(self, request):
        logout(request)
        return redirect("/")
