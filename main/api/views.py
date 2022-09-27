from main.api.authentication import HoneypotPermission
from main.api.serializers import HoneypotSerializer, HoneypotAttackSerializer
from main.models import Honeypot, HoneypotAttack, AttackDump
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authtoken.models import Token
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
            permission_classes = [HoneypotPermission]
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

        else:
            return Response(status=400)


class HoneypotAttackViewSet(ModelViewSet):
    queryset = HoneypotAttack.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [HoneypotPermission]
    serializer_class = HoneypotAttackSerializer


class FileUploadView(APIView):
    parser_classes = [FileUploadParser]
    authentication_classes = [TokenAuthentication]
    permission_classes = [HoneypotPermission]

    def get_honeypot(self, pk):
        try:
            return Honeypot.objects.get(pk=pk)
        except Honeypot.DoesNotExist:
            raise Http404

    def post(self, request, pk, format=None):
        honeypot = self.get_honeypot(pk)
        file_obj = request.data["file"]
        fs = FileSystemStorage()
        file_path = os.path.join(str(pk), file_obj.name)
        filename = fs.save(file_path, file_obj)
        uploaded_file_url = fs.url(filename)
        AttackDump.objects.get_or_create(path=uploaded_file_url, honeypot=honeypot)
        return Response(status=204)
