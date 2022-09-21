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


# MIXINS

# class HoneypotList(mixins.ListModelMixin,
#                   mixins.CreateModelMixin,
#                   generics.GenericAPIView):
#     queryset = Honeypot.objects.all()
#     serializer_class = HoneypotSerializer

#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)


# class HoneypotDetail(mixins.RetrieveModelMixin,
#                     mixins.UpdateModelMixin,
#                     mixins.DestroyModelMixin,
#                     generics.GenericAPIView):
#     queryset = Honeypot.objects.all()
#     serializer_class = HoneypotSerializer

#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)

#     def put(self, request, *args, **kwargs):
#         return self.update(request, *args, **kwargs)

#     def delete(self, request, *args, **kwargs):
#         return self.destroy(request, *args, **kwargs)

# MANUAL

# class HoneypotList(APIView):
#     """
#     List all honeypots, or create a new snippet.
#     """
#     def get(self, request, format=None):
#         honeypots = Honeypot.objects.all()
#         serializer = HoneypotSerializer(honeypots, many=True)
#         return Response(serializer.data)

#     def post(self, request, format=None):
#         serializer = HoneypotSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class HoneypotDetail(APIView):
#     """
#     Retrieve, update or delete a snippet instance.
#     """
#     def get_object(self, pk):
#         try:
#             return Honeypot.objects.get(pk=pk)
#         except Honeypot.DoesNotExist:
#             raise Http404

#     def get(self, request, pk, format=None):
#         snippet = self.get_object(pk)
#         serializer = HoneypotSerializer(snippet)
#         return Response(serializer.data)

#     def put(self, request, pk, format=None):
#         snippet = self.get_object(pk)
#         serializer = HoneypotSerializer(snippet, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk, format=None):
#         snippet = self.get_object(pk)
#         snippet.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
