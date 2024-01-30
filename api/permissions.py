from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
   # Custom permission to only allow admins to edit or delete, others can only read.

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class IsForumAdminOrReadOnly(permissions.BasePermission):
    
   # Custom permission to only allow forum admins to edit or delete, others can only read.
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        forum = view.get_object()
        return forum.admin == request.user

class IsMessageAuthorOrAdmin(permissions.BasePermission):
    #Custom permission to only allow message authors or forum admins to delete messages.
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            forum_admin = obj.forum.admin == request.user
            message_author = obj.author == request.user
            return forum_admin or message_author
        return True
