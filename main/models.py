from django.db import models
from django.contrib.auth.models import User


class Honeypot(models.Model):
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=128)
    author = models.ForeignKey(User, on_delete=models.CASCADE)


class Attacker(models.Model):
    source_addr = models.GenericIPAddressField()
    source_port = models.IntegerField()
    mac = models.CharField(max_length=20)


class HoneypotAttack(models.Model):
    honeypot = models.ForeignKey(Honeypot, on_delete=models.CASCADE)
    attacker = models.ForeignKey(Attacker, on_delete=models.CASCADE)
    data = models.JSONField()
    timestamp = models.DateTimeField()


class AttackDump(models.Model):
    honeypot = models.ForeignKey(Honeypot, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=64)
