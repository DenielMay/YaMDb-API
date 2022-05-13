from rest_framework import permissions


class AdminModeratorOrAuthorOfEntity(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or (request.user.is_authenticated
                and (request.user.role != 'user' or request.user.is_superuser))
        )


class AdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return bool(
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated
                and (request.user.role == 'admin' or request.user.is_superuser))
        )
