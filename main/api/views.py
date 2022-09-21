from main.api.serializers import HoneypotSerializer, HoneypotAttackSerializer
from main.models import Honeypot, HoneypotAttack
from rest_framework import viewsets


class HoneypotViewSet(viewsets.ModelViewSet):
    queryset = Honeypot.objects.all()
    serializer_class = HoneypotSerializer
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    permission_classes = []


class HoneypotAttackViewSet(viewsets.ModelViewSet):
    queryset = HoneypotAttack.objects.all()
    serializer_class = HoneypotAttackSerializer
    permission_classes = []
