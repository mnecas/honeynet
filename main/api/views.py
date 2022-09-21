from main.api.serializers import HoneypotSerializer, HoneypotAttackSerializer
from main.models import Honeypot, HoneypotAttack, AttackDump
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from django.core.files.storage import FileSystemStorage
from django.http import Http404


class HoneypotViewSet(ModelViewSet):
    queryset = Honeypot.objects.all()
    serializer_class = HoneypotSerializer
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    permission_classes = []


class HoneypotAttackViewSet(ModelViewSet):
    queryset = HoneypotAttack.objects.all()
    serializer_class = HoneypotAttackSerializer
    permission_classes = []


class FileUploadView(APIView):
    parser_classes = [FileUploadParser]
    permission_classes = []

    def get_honeypot(self, pk):
        try:
            return Honeypot.objects.get(pk=pk)
        except Honeypot.DoesNotExist:
            raise Http404

    def post(self, request, pk, format=None):
        honeypot = self.get_honeypot(pk)
        file_obj = request.data["file"]
        fs = FileSystemStorage()
        filename = fs.save(file_obj.name, file_obj)
        uploaded_file_url = fs.url(filename)
        AttackDump.objects.get_or_create(path=uploaded_file_url, honeypot=honeypot)
        return Response(status=204)
