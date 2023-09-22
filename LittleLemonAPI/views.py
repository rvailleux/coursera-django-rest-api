import json
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404
from django.contrib.auth.models import User, Group
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework import exceptions

from LittleLemonAPI.permissions import IsCustomerPermission, IsManagerOrReadOnlyPermission, IsManagerPermission, OrderPermission
from LittleLemonAPI.serializers import CartSerializer, MenuItemSerializer, OrderSerializer , UserSerializer
from LittleLemonAPI import models

from .models import Cart, MenuItem, Order



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
            raise exceptions.NotFound("Username not found")
        
        try:
            # Fetch the group object using the provided groupname
            group = Group.objects.get(name=groupname)
        except Group.DoesNotExist:
            raise exceptions.NotFound("Group name not found")
        
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
            raise exceptions.NotFound("User id not found")
        
        try:
            # Fetch the group object using the provided groupname
            group = Group.objects.get(name=groupname)
        except Group.DoesNotExist:
            raise exceptions.NotFound("Group name not found")
        
        # Remove the user from the group
        user.groups.remove(group)
        
        # Save the user object
        user.save()

        return Response({'message': f'User {user.username} removed from group {groupname}.'}, status=status.HTTP_200_OK)


class CartView(viewsets.ModelViewSet):

    model = Cart
    serializer_class = CartSerializer
    permission_classes= [IsCustomerPermission]

    def get_queryset(self):
        print(f"{self.request.user}")
        return get_list_or_404(Cart.objects.filter(user_id=self.request.user.id))
    
    def create(self, request):
        
        user = request.user
        menuitem_id = request.data.get("menuitem")
        quantity = request.data.get("quantity")

        if quantity == None or menuitem_id == None : return Response(data={'message': "Missing parameter."},status=status.HTTP_404_NOT_FOUND)

        try:
            # Fetch the menuitem to add
            menuitem = MenuItem.objects.get(id=menuitem_id)
            cartitem = Cart.objects.create(
                user=user,
                menuitem=menuitem,
                quantity=quantity
            )

            cartitem.save()

            return JsonResponse(model_to_dict(cartitem), status=status.HTTP_201_CREATED)
       
        except MenuItem.DoesNotExist:
            raise exceptions.NotFound("Menu item not found")
        except User.DoesNotExist:
            raise exceptions.NotFound("User not found")
        
    def destroy(self, request):
        user = request.user
        action_return = Cart.objects.filter(user=user).delete()
        return Response(data={"message": f"{action_return[0]} cart item(s) deleted", 
                        "nb_items" : action_return[0]}, status=status.HTTP_200_OK)
        
        
class OrdersView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [OrderPermission]

    def get_queryset(self):        

        if self.request.user.groups.filter(name="manager").exists():
            return Order.objects.all()
        
        elif self.request.user.groups.filter(name="delivery-crew").exists():
            return Order.objects.filter(delivery_crew_id=self.request.user.id)
        
        elif self.request.user.is_authenticated:
            return Order.objects.filter(user_id=self.request.user.id)
        
    def post(self):
        current_cart = get_object_or_404(Cart.objects.get(user=self.request.user))
        
