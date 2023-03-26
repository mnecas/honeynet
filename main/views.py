from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
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
import tarfile
import os
import json
import tempfile
import uuid
import shutil
import yaml


def get_honeypots():
    return {item:Honeypot.objects.filter(honeynet=item) for item in Honeynet.objects.all()}

class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["honeynets"] = get_honeypots()
        print(context)
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
        context["honeynets"] = get_honeypots()
        context["selected"] = honeypot
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


class DeleteHoneynet(View):
    def get(self, request, pk):
        honeypot = Honeynet.objects.get(pk=pk)
        honeypot.delete()
        return redirect("/")

class EditHoneypot(View):
    def post(self, request, pk):
        name = request.POST.get("name")
        honeypot = Honeypot.objects.get(pk=pk)
        if name:
            honeypot.name = name
        honeypot.save()
        return redirect(".")


class ViewHoneynet(TemplateView):
    template_name = "honeynet.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        honeynet = get_object_or_404(Honeynet, pk=kwargs["pk"])

        context["honeynets"] = get_honeypots()
        context["honeynet"] = honeynet
        context["selected"] = honeynet
        context["honeypots"] = Honeypot.objects.filter(honeynet=honeynet)
        return context

    def post(self, request, pk):
        name = request.POST.get("name")
        honeypot = Honeypot.objects.get(pk=pk)
        if name:
            honeypot.name = name
        honeypot.save()
        return redirect(".")

class StartAnsibleDeploymentView(View):
    def get(self, request, pk):
        self.honeynet = get_object_or_404(Honeynet, pk=pk)
        self.honeypots = Honeypot.objects.filter(honeynet=self.honeynet)
        rc = self.start_palybook()
        if rc != 0:
            return JsonResponse({"rc": rc, "stdout": self.get_playbook_stdout()})
        return JsonResponse({"rc": rc})

    def generate_ansible_runner_dir(self):
        self.id = str(uuid.uuid4())
        self.path = os.path.join("/tmp", self.id)
        print("Creating path '{}'".format(self.path))
        os.mkdir(self.path)

        shutil.copytree('project', self.path, dirs_exist_ok=True)
        env_path = os.path.join(self.path, "env")
        os.mkdir(env_path)

        self.generate_env_vars(env_path)
        self.store_docker_compose()

    def generate_env_vars(self, path):
        path = os.path.join(path, "extravars")
        with open(path, "w+") as f:
            f.write(yaml.dump(self.format_data(), default_flow_style=False))

    def store_docker_compose(self):
        for honeypot in self.honeypots:
            if honeypot.compose != "" and honeypot.compose != None :
                path = os.path.join(self.path, str(honeypot.id))
                os.mkdir(path)
                with open(os.path.join(path, "docker-compose.yml"), "w+") as f:
                    f.write(honeypot.compose)

    def get_playbook_status_code(self):
        with open(f"{self.path}/artifacts/{self.id}/rc") as f:
            return int(f.read())

    def get_playbook_stdout(self):
        with open(f"{self.path}/artifacts/{self.id}/stdout") as f:
            return f.read()

    def start_palybook(self):
        self.generate_ansible_runner_dir()
        os.system(f"ansible-runner run {self.path} -p deployment.yml -i {self.id} -q")
        return self.get_playbook_status_code()

    def format_data(self):
        return {
            "esxi_hostname": self.honeynet.hostname,
            "esxi_username": self.honeynet.username,
            "esxi_password": self.honeynet.password,
            "nic_name": self.honeynet.nic,
            "switch_name": self.honeynet.switch,
            "vms": [
                {
                    "name": honeypot.name,
                    "vmware_vm_user": honeypot.username,
                    "vmware_vm_pass": honeypot.password,
                    "portgroup_name": "honeypots-portgroup",
                    "compose_file": os.path.join(os.path.join(self.path, str(honeypot.id)), "docker-compose.yml")
                } for honeypot in self.honeypots
            ]
        }


class HoneynetAddView(TemplateView):
    template_name = "honeynet.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["honeynets"] = get_honeypots()
        return context

    def post(self, request):
        honeynet, created = Honeynet.objects.get_or_create(
            name=request.POST.get("name"),
            hostname=request.POST.get("hostname"),
            username=request.POST.get("username"),
            nic=request.POST.get("nic"),
            switch=request.POST.get("switch")
        )
        if not created:
            return redirect("/")

        nodes = json.loads(request.POST["honeypots"])
        for node in nodes:
            self.createHoneypot(node, honeynet)

        return redirect("/")

    def createHoneypot(self, node, honeynet):
        if not Group.objects.filter(name="honeypot").exists():
            HoneypotGroupInit().handle()
        honeypot_group = Group.objects.get(name="honeypot")
        user = User.objects.create_user(
            username="honeypot-{}".format(
                str(uuid.uuid4())
            )
        )
        user.groups.add(honeypot_group)
        Token.objects.create(user=user)

        return Honeypot.objects.create(
            name=node.get("name"),
            author=user,
            honeynet=honeynet,
            username=node.get("username"),
            password=node.get("password"),
            ovf=node.get("ovf"),
            compose=node.get("compose"),
        )
