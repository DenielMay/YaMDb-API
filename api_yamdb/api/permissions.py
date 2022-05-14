from rest_framework import permissions


class Admin(permissions.BasePermission):
    """Разрешение на все у суперюзера"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
                request.user.is_admin or request.user.is_superuser)


class SafeMethods(permissions.BasePermission):
    """"Безопасные методы"""

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class AdminModeratorOwner(permissions.BasePermission):
    """Админ, модератор и автор могут редактировать/удалять коммент, ревью"""

    def has_object_permission(self, request, view, obj):
        return (request.user.is_admin
                or request.user.is_moderator
                or obj.author == request.user)
