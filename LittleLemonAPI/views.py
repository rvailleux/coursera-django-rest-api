from django.shortcuts import get_list_or_404, get_object_or_404, render
from LittleLemonAPI.permissions import IsManagerOrReadOnlyPermission, IsManagerPermission
from django.contrib.auth.models import User, Group


from LittleLemonAPI.serializers import MenuItemSerializer , UserSerializer
from .models import MenuItem
from rest_framework import viewsets

class MenuItemsView(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsManagerOrReadOnlyPermission]


class UserViewByGroup(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsManagerPermission]
    lookup_field = 'groupname'

    def get_queryset(self):
        """
        This view should return a list of the users of the corresponding group only
        for the currently authenticated user.
        """
        groupname = self.kwargs['groupname']
        print(f"groupname {groupname}")
        return get_list_or_404(User, groups__name=groupname)
    
    def post(self, request):
        """
        This view add a user to the corresponding usergroup
        """
        print(f"username {userid} groupname {groupname}")
        groupname = self.kwargs['groupname']
        userid = request.POST['userid']

        print(f"username {userid} groupname {groupname}")
        #user = get_object_or_404(User, id=userid)
        #user.groups.add(name=groupname)
        #user.save()

        return user

