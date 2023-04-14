from api.authentication import HoneypotPermission
from api.serializers import (
    AttackerSerializer,
    HoneypotSerializer,
    HoneypotAttackSerializer,
)
from main.models import Attacker, Honeypot, AttackDump
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import (
    IsAuthenticated,
    DjangoModelPermissions,
)
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import User, Group
from django.core.files.storage import FileSystemStorage
from main.management.commands.config import Command as HoneypotGroupInit
from django.core.exceptions import ObjectDoesNotExist
import os
import uuid
import copy


class HoneypotViewSet(ModelViewSet):
    queryset = Honeypot.objects.all()
    serializer_class = HoneypotSerializer

    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == "create":
            self.permission_classes = []
        else:
            self.permission_classes = [
                IsAuthenticated,
                DjangoModelPermissions,
                HoneypotPermission,
            ]
        return super(ModelViewSet, self).get_permissions()

    def create(self, request):
        honeypot_serializer = HoneypotSerializer(data=request.data)
        if honeypot_serializer.is_valid():
            if Honeypot.objects.filter(name=request.data.get("name")).exists():
                return Response(status=400)

            if not Group.objects.filter(name="honeypot").exists():
                HoneypotGroupInit().handle()
            honeypot_group = Group.objects.get(name="honeypot")

            user = User.objects.create_user(
                username="honeypot-{}".format(str(uuid.uuid4()))
            )
            user.groups.add(honeypot_group)
            token = Token.objects.create(user=user)
            honeypot_serializer.save(author=user)
            return Response(
                status=201,
                content_type="application/json",
                data={
                    "token": token.key,
                    "id": Honeypot.objects.filter(name=request.data.get("name"))[0].id,
                },
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
        # uploaded_file_url = fs.url(filename)
        AttackDump.objects.get_or_create(path=filename, honeypot=honeypot)
        return Response(status=201)

    @action(detail=True, methods=["post"])
    def attack(self, request, *args, **kwargs):
        honeypot = self.get_object()
        data = copy.deepcopy(request.data)
        if not data.get("attacker"):
            return Response(status=400)
        attacker_serializer = AttackerSerializer(data=data.pop("attacker"))
        honeypot_attack_serializer = HoneypotAttackSerializer(data=data)
        if honeypot_attack_serializer.is_valid() and attacker_serializer.is_valid():
            attacker, _ = Attacker.objects.get_or_create(
                **attacker_serializer.validated_data
            )
            honeypot_attack_serializer.save(honeypot=honeypot, attacker=attacker)
            return Response(status=201)
        return Response(status=200)
