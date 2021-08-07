from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthenticatedUpdateOrReadOnly(BasePermission):
    """
    Permission, который запрещает редактировать профиль пользователю, котому данный профиль не принадлежит
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated
            and obj.user == request.user
        )
