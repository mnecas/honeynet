from rest_framework import permissions
from rest_framework import exceptions
from rest_framework.authtoken.models import Token


class HoneypotPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.META.get("HTTP_AUTHORIZATION"):
            return False
        try:
            user = Token.objects.get(
                key=request.META.get("HTTP_AUTHORIZATION").split(" ")[1]
            ).user
        except Token.DoesNotExist:
            raise exceptions.AuthenticationFailed("The token does not exist!")
        return obj.author == user

    def has_permission(self, request, view):
        return view.action != "list"
