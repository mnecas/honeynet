from main.api.authentication import HoneypotPermission
from main.api.serializers import (
    AttackerSerializer,
    HoneypotSerializer,
    HoneypotAttackSerializer,
)
from main.models import Attacker, Honeypot, HoneypotAttack, AttackDump
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticated,
    DjangoModelPermissions,
)
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, parser_classes
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import User, Group
from django.core.files.storage import FileSystemStorage
from django.http import Http404

import os
import uuid


class HoneypotViewSet(ModelViewSet):
    queryset = Honeypot.objects.all()
    serializer_class = HoneypotSerializer

    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == "create":
            permission_classes = []
        else:
            permission_classes = [
                DjangoModelPermissions,
                IsAuthenticated,
                IsAdminUser | HoneypotPermission,
            ]
        return [permission() for permission in permission_classes]

    def create(self, request):
        honeypot_serializer = HoneypotSerializer(data=request.data)
        if honeypot_serializer.is_valid():
            if Honeypot.objects.filter(
                name=request.data.get("name"), type=request.data.get("type")
            ).exists():
                return Response(status=400)

            honeypot_group = Group.objects.get(name="honeypot")
            user = User.objects.create_user(
                username="honeypot-{}-{}".format(
                    request.data.get("type"), str(uuid.uuid4())
                )
            )
            user.groups.add(honeypot_group)
            token = Token.objects.create(user=user)
            honeypot_serializer.save(author=user)
            return Response(
                {
                    "token": token.key,
                    "id": Honeypot.objects.filter(name=request.data.get("name"))[0].id,
                }
            )
        return Response(status=400)

    @action(detail=True, methods=["post"], parser_classes=[FileUploadParser])
    def upload(self, request, *args, **kwargs):
        honeypot = self.get_object()
        file_obj = request.data.get("filename")
        if not file_obj:
            return Response(status=400)
        fs = FileSystemStorage()
        file_path = os.path.join(str(honeypot.pk), file_obj.name)
        filename = fs.save(file_path, file_obj)
        uploaded_file_url = fs.url(filename)
        AttackDump.objects.get_or_create(path=uploaded_file_url, honeypot=honeypot)
        return Response(status=204)

    @action(detail=True, methods=["post"])
    def attack(self, request, *args, **kwargs):
        honeypot = self.get_object()
        attacker_serializer = AttackerSerializer(data=request.data.pop("attacker"))
        honeypot_attack_serializer = HoneypotAttackSerializer(data=request.data)
        if honeypot_attack_serializer.is_valid() and attacker_serializer.is_valid():
            attacker, _ = Attacker.objects.get_or_create(
                **attacker_serializer.validated_data
            )
            honeypot_attack_serializer.save(honeypot=honeypot, attacker=attacker)
        return Response(status=204)
