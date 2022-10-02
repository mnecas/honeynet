from django.db import models
from django.contrib.auth.models import User


class Honeypot(models.Model):
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=128)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return " - ".join([self.name, self.type])


class Attacker(models.Model):
    source_addr = models.GenericIPAddressField()
    source_port = models.IntegerField()
    mac = models.CharField(max_length=20)

    def __str__(self):
        return " - ".join([str(self.source_addr), str(self.source_port), str(self.mac)])


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
