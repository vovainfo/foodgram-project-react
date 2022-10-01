from rest_framework.permissions import (BasePermission,
                                        IsAuthenticatedOrReadOnly)


class OwnerAndAdminOrReadOnly(IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        return (
            request.method == 'GET'
            or (request.user == obj.author)
            or request.user.is_staff
        )


class AdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method == 'GET'
            or request.user.is_authenticated
            and request.user.is_staff
        )
