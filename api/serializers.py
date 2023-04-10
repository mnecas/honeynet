from dataclasses import field
from rest_framework import serializers
from main.models import Honeypot, Attacker, HoneypotAttack, HoneypotLog


class HoneypotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Honeypot
        fields = ["id", "name"]


class AttackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attacker
        fields = ["source_addr", "source_port"]


class HoneypotAttackSerializer(serializers.ModelSerializer):
    class Meta:
        model = HoneypotAttack
        fields = ["data"]

class HoneypotLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = HoneypotLog
        fields = ["time", "log_level", "message"]
