import jinja2
import subprocess
import os
import shutil
from django.forms.models import model_to_dict
from rest_framework.authtoken.models import Token


class HoneypotDeployment:
    def __init__(self, honeypot):
        self.honeypot_filename = "templates/honeypot.yml.j2"
        self.monitoring_filename = "templates/monitoring.yml.j2"
        # self.honeynet_root_dir = "/usr/share/honeynet"
        self.honeynet_root_dir = "./honeynets"
        self.honeypot = honeypot
        self.honeypot_data = model_to_dict(self.honeypot)
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
        return result

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
                return result
            shutil.rmtree(self.honeypot_dir)

    def _create_compose(self, src_file, dst_file):
        templateLoader = jinja2.FileSystemLoader(searchpath="./")
        templateEnv = jinja2.Environment(loader=templateLoader)
        template = templateEnv.get_template(src_file)
        print(model_to_dict(self.honeypot))
        data = {
            "honeypot": model_to_dict(self.honeypot),
            "honeypot_id": str(self.honeypot.id),
            "honeypot_token": str(Token.objects.get(user=self.honeypot.author)),
            "honeypot_ports": list(self.honeypot.ports.split(",")),
            "honeynet": model_to_dict(self.honeypot.honeynet),
        }
        with open(dst_file, "w+") as f:
            f.write(template.render(data))
