from rest_framework.permissions import BasePermission



class IsXanAuthenticated(BasePermission):
    """
    Allows access only to xan_authenticated users.
    """

    def has_permission(self, request, view): # type: ignore
        return bool(request.xan and request.xan.is_authenticated)


