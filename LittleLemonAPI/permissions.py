from rest_framework import permissions


class IsManagerOrReadOnlyPermission(permissions.BasePermission):
    """
    Custom permission to only allow managers  to edit it.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.

        if request.method in permissions.SAFE_METHODS:
            return True
        
        if not request.user.is_authenticated:
            return False
        
        # Write permissions are only allowed to the user within Manager group.
        return request.user.groups.filter(name="manager").exists()
    

class IsManagerPermission(permissions.BasePermission):
    """
    Custom permission to only allow managers  to edit it.
    """

    def has_permission(self, request, view):
        
        # Write permissions are only allowed to the user within Manager group.
        return request.user.groups.filter(name="manager").exists()