import json
from django.shortcuts import get_list_or_404, get_object_or_404
from LittleLemonAPI.permissions import IsCustomerPermission, IsManagerOrReadOnlyPermission, IsManagerPermission
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework import status
from LittleLemonAPI.serializers import MenuItemSerializer , UserSerializer
from .models import MenuItem
from rest_framework import viewsets

from LittleLemonAPI import models

class MenuItemsView(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsManagerOrReadOnlyPermission]


class UsersByGroupView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsManagerPermission]

    def get_queryset(self):
        """
        This view returns a list of the users of the corresponding group
        """
        groupname = self.kwargs['groupname']
        return get_list_or_404(User, groups__name=groupname)
    
    def update(self, request, groupname):
        """
        This view adds a user to the corresponding usergroup
        Endpoint api/groups/<str:groupname>
        Form Data field : username
        """
        # Extract username from the request data
        username = request.data.get('username')
        
        try:
            # Fetch the user object using the provided username
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound("Username not found")
        
        try:
            # Fetch the group object using the provided groupname
            group = Group.objects.get(name=groupname)
        except Group.DoesNotExist:
            raise NotFound("Group name not found")
        
        # Add the user to the group
        user.groups.add(group)
        
        # Save the user object
        user.save()

        return Response({'message': f'User {username} added to group {groupname}.'}, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, groupname, user_id):
        """
        This view remove a user from the group
        Endpoint api/groups/<str:groupname>/<int:user_id>
        """
        print(f"Removing {user_id} from {groupname}")

        try:
            # Fetch the user object using the provided username
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound("User id not found")
        
        try:
            # Fetch the group object using the provided groupname
            group = Group.objects.get(name=groupname)
        except Group.DoesNotExist:
            raise NotFound("Group name not found")
        
        # Remove the user from the group
        user.groups.remove(group)
        
        # Save the user object
        user.save()

        return Response({'message': f'User {user.username} removed from group {groupname}.'}, status=status.HTTP_200_OK)


class CartManagementView(viewsets.ModelViewSet):

    model = models.Cart
    permission_classes= [IsCustomerPermission]

    def list(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)