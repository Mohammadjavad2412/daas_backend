from rest_framework.permissions import BasePermission


class OnlyOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.email == obj.email:
            return True
        return False
    
    
class OnlyAdmin(BasePermission):
    def has_permission(self, request, view):
        try:
            if request.user and request.user.is_superuser:
                return True
            return False
        except:
            return False
        