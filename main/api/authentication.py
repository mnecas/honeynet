from rest_framework import permissions
from rest_framework import exceptions
from rest_framework.authtoken.models import Token


class HoneypotPermission(permissions.BasePermission):
    def get_user(self, request):
        try:
            user = Token.objects.get(key=request.auth).user
        except Token.DoesNotExist:
            raise exceptions.AuthenticationFailed("The token does not exist!")
        return user

    def has_object_permission(self, request, view, obj):
        if not request.auth:
            return False
        user = self.get_user(request)
        return obj.author == user

    def has_permission(self, request, view):
        user = self.get_user(request)
        is_honeypot_user = user.groups.filter(name="honeypot").exists()
        return is_honeypot_user and view.action != "list"
