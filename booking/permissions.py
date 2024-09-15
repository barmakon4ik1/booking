from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.shortcuts import redirect


class IsOwnerOrVisibleOrAdmin(BasePermission):
    """
    Разрешает доступ:
    - К видимым объектам (is_visible=True) для всех пользователей.
    - К редактированию или удалению объектов только для владельца.
    - Полный доступ для администратора ко всем объектам.
    """

    def has_object_permission(self, request, view, obj):
        # Если пользователь администратор, то предоставить полный доступ
        if request.user.is_staff:
            return True

        # Разрешить безопасные методы (GET, HEAD или OPTIONS) всем, если объект видим
        if request.method in SAFE_METHODS:
            return obj.is_visible or obj.owner == request.user

        # Разрешить редактирование и удаление только владельцу
        return obj.owner == request.user


class IsOwnerOrAdmin(BasePermission):
    """
    Разрешение, позволяющее доступ только владельцам объекта или администраторам.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем доступ, если пользователь - администратор
        if request.user.is_staff:
            return True

        # Разрешаем доступ, если пользователь - владелец объекта
        return obj.owner == request.user

