from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')


class IsAnalystOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return request.user.role in ['analyst', 'admin']


class IsViewerAnalystAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return request.user.role in ['viewer', 'analyst', 'admin']


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.role == 'admin' or obj.user == request.user
