from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
import uuid


class Honeynet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    hostname = models.CharField(max_length=128)
    username = models.CharField(max_length=128)
    password = models.CharField(max_length=128)
    nic = models.CharField(max_length=128)
    switch = models.CharField(max_length=128)


class Honeypot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    honeynet = models.ForeignKey(Honeynet, on_delete=models.CASCADE)
    compose = models.TextField(blank=True)
    ovf = models.CharField(max_length=128, blank=True)
    username = models.CharField(max_length=128, blank=True)
    tcpdump_filter = models.CharField(max_length=128, blank=True)
    tcpdump_timeout = models.IntegerField(default=3600, blank=True, null=True)
    tcpdump_max_size = models.IntegerField(default=100, blank=True, null=True)
    tcpdump_extra_args = models.CharField(max_length=512, blank=True)
    password = models.CharField(max_length=128, blank=True)
    ssh_port = models.IntegerField(default=22)
    ssh_key = models.TextField(blank=True)


class Attacker(models.Model):
    source_addr = models.GenericIPAddressField()
    source_port = models.IntegerField()

    def __str__(self):
        return " - ".join([str(self.source_addr), str(self.source_port)])

class HoneypotLog(models.Model):
    honeypot = models.ForeignKey(Honeypot, on_delete=models.CASCADE)
    log_level = models.CharField(max_length=128, blank=True)
    message = models.CharField(max_length=128, blank=True)
    time = models.DateTimeField(auto_now_add=True)


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
