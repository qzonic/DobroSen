from rest_framework.permissions import BasePermission


class IsTaskCreator(BasePermission):
    """ Permission that allow modifying task only by creator. """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.creator == request.user


class IsSubTaskCreator(BasePermission):
    """ Permission that allow modifying subtask only by creator. """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
                obj.creator == request.user
                or obj.parent_task.creator == request.user
        )


class IsAssigned(BasePermission):
    """ Permission that allow modifying some fields in subtask only by assigned user. """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.assigned_to == request.user
