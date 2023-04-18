import jinja2
import subprocess
import os
import shutil
from django.forms.models import model_to_dict
from rest_framework.authtoken.models import Token
import docker
import multiprocessing


class HoneynetData:
    def __init__(self):
        pass


class HoneynetDeployment:
    def __init__(self, honeynet):
        self.honeynet = honeynet
        self.client = docker.from_env()
        self.honeynet_root_dir = "honeynets"
        self.honeynet_dir = os.path.join(self.honeynet_root_dir, str(honeynet.id))

    def up(self):
        if self.client.networks.list(names=[self.honeynet.name]):
            raise Exception(f"The docker network '{self.honeynet.name}' already exists!")

        if self.honeynet.subnet:
            ipam_pool = docker.types.IPAMPool(
                subnet=self.honeynet.subnet,
            )
            ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])
            self.client.networks.create(self.honeynet.name, ipam=ipam_config)
        else:
            self.client.networks.create(self.honeynet.name)

    def _delete_container(self, container):
        container.stop()
        container.remove()

    def down(self):
        network = self.client.networks.get(self.honeynet.name)
        process_list = []
        for container in network.containers:
            process = multiprocessing.Process(
                target=self._delete_container, args=(container,)
            )
            process_list.append(process)

        for process in process_list:
            process.start()

        for process in process_list:
            process.join()
        network.remove()
        shutil.rmtree(self.honeynet_dir)

    def get_subnet(self):
        network = self.client.api.inspect_network(self.honeynet.name)
        return network["IPAM"]["Config"][0]["Subnet"]


class HoneypotDeployment:
    def __init__(self, honeypot, update=False):
        self.honeypot_filename = "deployment/templates/honeypot.yml.j2"
        self.monitoring_filename = "deployment/templates/monitoring.yml.j2"
        # self.honeynet_root_dir = "/usr/share/honeynet"
        self.honeynet_root_dir = "honeynets"
        self.honeypot = honeypot
        self.client = docker.from_env()
        self.update = update

        if not os.path.exists(self.honeynet_root_dir):
            os.makedirs(self.honeynet_root_dir)

        self.honeynet_dir = os.path.join(
            self.honeynet_root_dir, str(honeypot.honeynet.id)
        )
        if not os.path.exists(self.honeynet_dir):
            os.makedirs(self.honeynet_dir)

        self.honeypot_dir = os.path.join(self.honeynet_dir, str(honeypot.id))
        if not os.path.exists(self.honeypot_dir):
            os.makedirs(self.honeypot_dir)
        self.honeypot_path = os.path.join(self.honeypot_dir, "honeypot.yml")
        self.honeypot_monitoring_path = os.path.join(
            self.honeypot_dir, "monitoring.yml"
        )

    def up(self):
        # Up containers
        self._create_compose(self.honeypot_filename, self.honeypot_path)
        self._create_compose(self.monitoring_filename, self.honeypot_monitoring_path)
        result = subprocess.run(
            [
                "deployment/deploy-honeypot.sh",
                self.honeypot_path,
                self.honeypot_monitoring_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode != 0:
            self.down()
            return (False, result)
        return (True, result)

    def down(self):
        # Down
        if os.path.exists(self.honeypot_dir):
            result = subprocess.run(
                [
                    "deployment/delete-honeypot.sh",
                    self.honeypot_path,
                    self.honeypot_monitoring_path,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if result.returncode != 0:
                return (False, result)
            shutil.rmtree(self.honeypot_dir)
        return (True, None)

    def _create_compose(self, src_file, dst_file):
        templateLoader = jinja2.FileSystemLoader(searchpath="./")
        templateEnv = jinja2.Environment(loader=templateLoader)
        template = templateEnv.get_template(src_file)
        data = {
            "honeypot": model_to_dict(self.honeypot),
            "honeypot_id": str(self.honeypot.id),
            "honeypot_token": str(Token.objects.get(user=self.honeypot.author)),
            "honeypot_ports": list(self.honeypot.ports.split(",")),
            "honeynet": model_to_dict(self.honeypot.honeynet),
            "update": self.update,
        }
        with open(dst_file, "w+") as f:
            f.write(template.render(data))

    def get_honeypot_container_id(self):
        with open(os.path.join(self.honeypot_dir, "honeypot_id")) as f:
            honeypot_id = f.read()
        return honeypot_id

    def get_monitoring_container_id(self):
        with open(os.path.join(self.honeypot_dir, "monitoring_id")) as f:
            honeypot_id = f.read()
        return honeypot_id

    def get_ip(self):
        container_info = self.client.api.inspect_container(
            str(self.get_honeypot_container_id()).replace("\n", "")
        )
        return container_info["NetworkSettings"]["Networks"][
            self.honeypot.honeynet.name
        ]["IPAddress"]
