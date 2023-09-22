from rest_framework import permissions
from rest_framework.authtoken.models import Token

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
        
        print(f"{request.user.username} - {request.user.groups}")
        # Write permissions are only allowed to the user within Manager group.
        return request.user.groups.filter(name="manager").exists()
    
class IsCustomerPermission(permissions.BasePermission):
    """
    Custom permission to allow cart access only to customers with a valid token.
    """

    def has_permission(self, request, view):

        #The user must be authentified trough a Token and be a customer (in no group)        
        if not isinstance(request.auth, Token): 
                return False

        return True
    

class OrderPermission(permissions.BasePermission):
    """
    Custom permission to enable access to endpoints depending on roles.
    """

    def has_permission(self, request, view):
        
        if not request.user.is_authenticated:
            return False
        
        else:
            if request.method == "GET":
                return True
            if request.method == "POST":
                return True
            else:
                return False