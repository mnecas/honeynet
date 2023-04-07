from rest_framework.authtoken.models import Token
import os
import uuid
import shutil
import yaml


class StartAnsible:
    def __init__(self, honeypots, honeynet):
        self.honeypots = honeypots
        self.honeynet = honeynet

    def generate_ansible_runner_dir(self):
        self.id = str(uuid.uuid4())
        self.path = os.path.join("/tmp", self.id)
        print("Creating path '{}'".format(self.path))
        os.mkdir(self.path)

        shutil.copytree("project", self.path, dirs_exist_ok=True)
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
            path = os.path.join(self.path, str(honeypot.id))
            os.mkdir(path)
            if honeypot.compose != "" and honeypot.compose != None:
                with open(os.path.join(path, "docker-compose.yml"), "w+") as f:
                    f.write(honeypot.compose)
            if honeypot.ssh_key != "" and honeypot.ssh_key != None:
                with open(os.path.join(path, "key"), "w+") as f:
                    f.write(honeypot.ssh_key)

    def get_playbook_status_code(self):
        with open(os.path.join(self.path,"artifacts",self.id,"rc")) as f:
            return int(f.read())

    def get_playbook_stdout(self):
        with open(os.path.join(self.path,"artifacts",self.id,"stdout")) as f:
            return f.read()

    def start_deployment(self):
        return self.start_palybook("deployment.yml")

    def start_cleanup(self):
        return self.start_palybook("cleanup.yml")

    def start_cleanup_all(self):
        return self.start_palybook("cleanup_all.yml")

    def start_palybook(self, playbook):
        self.generate_ansible_runner_dir()
        os.system(f"ansible-runner run {self.path} -p {playbook} -i {self.id}")
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
                    "id": str(honeypot.id),
                    "vmware_vm_ssh_key_file": os.path.join(self.path, str(honeypot.id), "key") if honeypot.ssh_key else None,
                    "vmware_vm_ssh_port": honeypot.ssh_port,
                    "token": str(Token.objects.get(user=honeypot.author)),
                    # "filter": honeypot.filter,
                    "vmware_vm_ssh_user": honeypot.username,
                    "vmware_vm_ssh_pass": honeypot.password,
                    "tcpdump": honeypot.tcpdump,
                    "ovf_image": honeypot.ovf,
                    "portgroup_name": "honeypots-portgroup",
                    "compose_file": os.path.join(self.path, str(honeypot.id), "docker-compose.yml")
                    if honeypot.compose
                    else None,
                }
                for honeypot in self.honeypots
            ],
        }
