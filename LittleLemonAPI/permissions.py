from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.authtoken.models import Token

from LittleLemonAPI.models import Order

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
        return request.user.groups.filter(name="manager").exists() or request.user.is_superuser
    

class IsManagerOrAdminPermission(permissions.BasePermission):
    """
    Custom permission to only allow managers  to edit it.
    """

    def has_permission(self, request, view):
        # Write permissions are only allowed to the user within Manager group.
        return request.user.groups.filter(name="manager").exists() or request.user.is_superuser
    
class IsCustomerPermission(permissions.BasePermission):
    """
    Custom permission to allow cart access only to customers with a valid token.
    """

    def has_permission(self, request, view):

        #The user must be authentified trough a Token and be a customer (in no group)        
        if not isinstance(request.auth, Token): 
                return False

        return True
    

class OrdersPermission(permissions.BasePermission):
    """
    Custom permission to enable access to endpoints depending on roles.
    """

    def has_permission(self, request, view):
        
        if not request.user.is_authenticated:
            return False
        
        else:
            if request.method == "GET":
                return True
            elif request.method == "POST":
                return True
            else:
                return False
            

class OrderPermission(permissions.BasePermission):
    """
    Custom permission to enable access to endpoints depending on roles.
    """

    def has_permission(self, request, view):
        
        if not request.user.is_authenticated:
            return False
        
        else:
            current_user_groups_names = {group.name for group in request.user.groups.all()}
            
            if request.method == "GET" or request.method == "PUT" or request.method == "PATCH":
    
                if not {'delivery-crew', 'manager'}.intersection(current_user_groups_names):
                    order = get_object_or_404(Order, id=view.kwargs.get('pk'))
                    return request.user.id == order.user.id    
                
            if request.method == 'PATCH' and {'delivery-crew', 'manager'}.intersection(current_user_groups_names):
                
                return True
            
            if request.method == 'DELETE' and 'manager' in current_user_groups_names:
                return True

        return False