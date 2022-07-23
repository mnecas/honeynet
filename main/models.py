from django.db import models


class Honeypot(models.Model):
    name = models.CharField(max_length=64)
    type = models.CharField(max_length=64)
    ip = models.GenericIPAddressField()
    port = models.IntegerField()


class Attacker(models.Model):
    source_addr = models.GenericIPAddressField()
    source_port = models.IntegerField()
    mac = models.CharField(max_length=20)


class HoneypotHasAttacker(models.Model):
    honeypot = models.ForeignKey(Honeypot, on_delete=models.CASCADE)
    attacker = models.ForeignKey(Attacker, on_delete=models.CASCADE)
    data = models.JSONField()
    timestamp = models.DateTimeField()


class AttackDump(models.Model):
    honeypot = models.ForeignKey(Honeypot, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=64)
