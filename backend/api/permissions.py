from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the object has a 'user' attribute and it matches the request user
        if hasattr(obj, "user"):
            return obj.user == request.user

        # For User objects, check if it's the same user
        if obj.__class__.__name__ == "User":
            return obj == request.user

        return False
