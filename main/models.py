from django.db import models


class Honeypot(models.Model):
    name = models.CharField(max_length=64)
    type = models.CharField(max_length=64)
    ip = models.GenericIPAddressField()

    def __str__(self):
        return f"{self.name} - {self.type}"


class HoneypotData(models.Model):
    data = models.JSONField()
    honeypot = models.ForeignKey(Honeypot, on_delete=models.CASCADE)
