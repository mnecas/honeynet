from dataclasses import field
from rest_framework import serializers
from main.models import Honeypot, Attacker, HoneypotAttack


class HoneypotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Honeypot
        fields = ["id", "name", "type"]


class AttackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attacker
        fields = ["source_addr", "source_port", "mac"]


class HoneypotAttackSerializer(serializers.ModelSerializer):
    class Meta:
        model = HoneypotAttack
        fields = ["honeypot", "attacker", "data", "timestamp"]
