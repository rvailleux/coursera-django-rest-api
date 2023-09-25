from datetime import date
import json
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404
from django.contrib.auth.models import User, Group
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter

from LittleLemonAPI.permissions import IsCustomerPermission, IsManagerOrReadOnlyPermission, IsManagerOrAdminPermission, OrderPermission, OrdersPermission
from LittleLemonAPI.serializers import CartSerializer, CategorySerializer, MenuItemSerializer, OrderItemSerializer, OrderSerializer, UserSerializer
from LittleLemonAPI import models

from .models import Cart, Category, MenuItem, Order, OrderItem


class MenuItemsView(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsManagerOrReadOnlyPermission]
    filter_backends = [OrderingFilter] 
    ordering_fields = ['price']  # Specify the fields by which you can order

    pagination_class = PageNumberPagination
    pagination_class.page_size = 4



class UsersByGroupView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsManagerOrAdminPermission]

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
    permission_classes = [IsCustomerPermission]

    def get_queryset(self):
        print(f"{self.request.user}")
        return get_list_or_404(Cart.objects.filter(user_id=self.request.user.id))

    def create(self, request):

        user = request.user
        menuitem_id = request.data.get("menuitem")
        quantity = request.data.get("quantity")

        if quantity == None or menuitem_id == None:
            return Response(data={'message': "Missing parameter."}, status=status.HTTP_404_NOT_FOUND)

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
                        "nb_items": action_return[0]}, status=status.HTTP_200_OK)


class OrdersView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [OrdersPermission]

    def get_queryset(self):

        if self.request.user.groups.filter(name="manager").exists():
            return Order.objects.all()

        elif self.request.user.groups.filter(name="delivery-crew").exists():
            return Order.objects.filter(delivery_crew_id=self.request.user.id)

        elif self.request.user.is_authenticated:
            return Order.objects.filter(user_id=self.request.user.id)

    def post(self, data):
        current_cart_items = Cart.objects.filter(user=self.request.user)

        if not current_cart_items.exists():
            return Response(data={"message": f"No cart item found to create order."}, status=status.HTTP_404_NOT_FOUND)


        new_order = Order(user=self.request.user,
                          date=date.today())

        new_order.save()

        for cart_item in current_cart_items:
            new_order.orderitem_set.create(menuitem=cart_item.menuitem,
                                           quantity=cart_item.quantity)

        current_cart_items.delete()
        
        return JsonResponse(model_to_dict(new_order), status=status.HTTP_201_CREATED)


class OrderView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [OrderPermission]


class CategoriesView(generics.ListCreateAPIView):
     queryset = Category.objects.all()
     serializer_class = CategorySerializer

class CategoryView(generics.RetrieveAPIView):
     queryset = Category.objects.all()
     serializer_class = CategorySerializer

class MenuItemsInCategoryView(generics.ListAPIView):
    
    serializer_class = MenuItemSerializer

    def get_queryset(self):
        category_id = self.kwargs['pk']
        return get_list_or_404(MenuItem.objects.filter(category_id=category_id))