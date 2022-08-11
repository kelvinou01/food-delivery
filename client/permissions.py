from rest_framework import permissions
from django.core.exceptions import ObjectDoesNotExist


class IsClient(permissions.BasePermission):
    def has_permission(self, request, view):
        try: 
            request.user.client
        except ObjectDoesNotExist:
            return False
        return True
