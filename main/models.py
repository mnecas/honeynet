from django.db import models


class Honeypot(models.Model):
    type = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.type}"


class HoneypotData(models.Model):
    data = models.JSONField()


class HoneypotStruct(models.Model):
    honeypot = models.ForeignKey(Honeypot, on_delete=models.CASCADE)
    type = models.CharField(max_length=64)
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.type}"
