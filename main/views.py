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
from .forms import HoneynetForm
from .ansible import StartAnsible
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

    def post(self, request, hn_pk, hp_pk):
        honeypot = Honeypot.objects.get(id=hp_pk)
        atrs = ["name", "username", "password", "ovf", "compose", "tcpdump", "ssh_port", "ssh_key"]
        for atr in atrs:
            if request.POST.get(atr) != "":
                setattr(honeypot, atr, request.POST.get(atr))
        honeypot.save()
        return redirect(reverse("honeynets_details", kwargs={"hn_pk": hn_pk}))


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
        response = FileResponse(open(f.file.name, mode="rb"))
        # Cleanup before sending the file
        os.remove(f.file.name)
        return response



class DeleteHoneypot(View):
    def post(self, request, hn_pk, hp_pk):
        print(request.POST)
        honeypot = Honeypot.objects.get(pk=hp_pk)
        honeynet = get_object_or_404(Honeynet, pk=hn_pk)
        if request.GET.get('cleanup'):
            ansible = StartAnsible([honeypot], honeynet)
            rc = ansible.start_cleanup()
            if rc == 0:
                honeypot.delete()
        else:
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
        return redirect(reverse("honeypots_detail", kwargs={"hn_pk": hn_pk, "hp_pk":hp_pk}))


class DeleteHoneynet(View):
    def get(self, request, hn_pk):
        honeynet = Honeynet.objects.get(pk=hn_pk)
        honeypots = Honeypot.objects.filter(honeynet__id=honeynet.id)
        if len(list(honeypots)) > 0 and request.GET.get('cleanup') == 'true':
            ansible = StartAnsible(honeypots, honeynet)
            rc = ansible.start_cleanup_all()
            if rc == 0:
                honeynet.delete()
            else:
                return JsonResponse({"rc": rc, "stdout": ansible.get_playbook_stdout()})
            return JsonResponse({"rc": rc})
        else:
            honeynet.delete()
        return JsonResponse({"rc": 0})


class StartAnsibleDeploymentView(View):
    def get(self, request, hn_pk):
        self.honeynet = get_object_or_404(Honeynet, pk=hn_pk)
        self.honeypots = Honeypot.objects.filter(honeynet=self.honeynet)
        ansible = StartAnsible(self.honeypots, self.honeynet)
        rc = ansible.start_deployment()
        if rc != 0:
            return JsonResponse({"rc": rc, "stdout": ansible.get_playbook_stdout()})
        return JsonResponse({"rc": rc})


class HoneypotAddView(View):
    def post(self, request, hn_pk):
        if not Group.objects.filter(name="honeypot").exists():
            HoneypotGroupInit().handle()
        honeypot_group = Group.objects.get(name="honeypot")
        user = User.objects.create_user(
            username="honeypot-{}".format(str(uuid.uuid4()))
        )
        user.groups.add(honeypot_group)
        Token.objects.create(user=user)
        Honeypot.objects.create(
            name=request.POST.get("name"),
            author=user,
            honeynet=Honeynet.objects.get(id=hn_pk),
            username=request.POST.get("username"),
            password=request.POST.get("password"),
            ssh_key=request.POST.get("ssh_key"),
            ssh_port=request.POST.get("ssh_port"),
            tcpdump=request.POST.get("tcpdump"),
            ovf=request.POST.get("ovf"),
            compose=request.POST.get("compose"),
        )
        return redirect(reverse("honeynets_details", kwargs={"hn_pk": hn_pk}))


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
        atrs = ["name", "hostname", "username", "password", "nic", "switch"]
        for atr in atrs:
            if request.POST.get(atr) != "":
                setattr(honeynet, atr, request.POST.get(atr))
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
                username=form.cleaned_data.get("username"),
                password=form.cleaned_data.get("password"),
                hostname=form.cleaned_data.get("hostname"),
                nic=form.cleaned_data.get("nic"),
                switch=form.cleaned_data.get("switch"),
            )
            return redirect(
                reverse("honeynets_details", kwargs={"hn_pk": str(honeynet.id)})
            )
        else:
            form = HoneynetForm()
            return render(request, "honeynet.html", {"form": form})


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
