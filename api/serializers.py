from dataclasses import field
from rest_framework import serializers
from main.models import Honeypot, Attacker, HoneypotAttack


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
