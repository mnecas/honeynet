from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import uuid
import os
import shutil


class HoneypotSyslog(models.Model):
    address = models.CharField(max_length=128)
    tls_ca_cert = models.CharField(max_length=128)
    tls_cert = models.CharField(max_length=128)
    tls_key = models.CharField(max_length=128)
    tls_skip_verify = models.BooleanField()
    tag = models.CharField(max_length=128)
    format = models.CharField(max_length=128)
    labels = models.CharField(max_length=128)


class HoneypotExport(models.Model):
    address = models.CharField(max_length=128)
    path = models.CharField(max_length=128, blank=True, null=True)
    username = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    crontab = models.CharField(max_length=128)


class Honeynet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    subnet = models.CharField(max_length=20, blank=True)
    export = models.ForeignKey(
        HoneypotExport, on_delete=models.CASCADE, blank=True, null=True
    )

    # def delete(self, *args, **kwargs):
    #     honeynet_dir = os.path.join(settings.BASE_DIR, "honeynets", str(self.id))
    #     if os.path.exists(honeynet_dir):
    #         shutil.rmtree(honeynet_dir)


class Honeypot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True, max_length=128)
    ip_addr = models.CharField(max_length=16)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    honeynet = models.ForeignKey(Honeynet, on_delete=models.CASCADE)
    image = models.CharField(max_length=128)
    ports = models.CharField(max_length=128)
    tcpdump_filter = models.CharField(max_length=128, blank=True)
    tcpdump_timeout = models.IntegerField(default=3600, blank=True, null=True)
    tcpdump_max_size = models.IntegerField(default=100, blank=True, null=True)
    tcpdump_extra_args = models.CharField(max_length=512, blank=True)
    # honeypot_container_id = models.CharField(max_length=128)
    # monitoring_container_id = models.CharField(max_length=128)

    # def delete(self, *args, **kwargs):
    #     honeypot_dir = os.path.join(settings.BASE_DIR, "honeynets", self.honeynet.id, str(self.id))
    #     if os.path.exists(honeypot_dir):
    #         shutil.rmtree(honeypot_dir)


class Attacker(models.Model):
    source_addr = models.GenericIPAddressField()
    source_port = models.IntegerField()

    def __str__(self):
        return " - ".join([str(self.source_addr), str(self.source_port)])


class HoneypotAttack(models.Model):
    honeypot = models.ForeignKey(Honeypot, on_delete=models.CASCADE)
    attacker = models.ForeignKey(Attacker, on_delete=models.CASCADE)
    data = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return " - ".join(
            [str(self.timestamp.date), str(self.honeypot), str(self.attacker)]
        )


class AttackDump(models.Model):
    honeypot = models.ForeignKey(Honeypot, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=64)

    def __str__(self):
        return str(self.honeypot) + " - " + self.path

    def delete(self, *args, **kwargs):
        fs = FileSystemStorage()
        fs.delete(self.path)
        super(AttackDump, self).delete(*args, **kwargs)
