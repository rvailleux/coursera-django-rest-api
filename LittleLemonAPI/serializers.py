from rest_framework import serializers
from django.contrib.auth.models import User, Group, AnonymousUser
from LittleLemonAPI.models import Cart, Category, MenuItem, Order, OrderItem


class MenuItemSerializer(serializers.HyperlinkedModelSerializer):

    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all())

    class Meta:
        model = MenuItem
        fields = ['url','title', 'price', 'featured', 'category', 'category_id']
        read_only_fields = ['category']

class GroupSerializer(serializers.ModelSerializer, ):
    class Meta:
        name = Group.objects.all()
        model = Group
        fields = ['name']


class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'id', 'groups']
        read_only_fields = ['username', 'email', 'id']


class CartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    menuitem = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all())

    class Meta:
        model = Cart
        fields = ['id', 'user', 'menuitem', 'quantity', 'unit_price', 'price']
        read_only_fields = ['id', 'user', 'unit_price', 'price']
        optional_fields = ['unit_price', 'price']

        def create(self, validated_data):
            user = self.request.user
            if not isinstance(user, AnonymousUser):
                validated_data["user"] = user


class OrderItemSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    menuitem = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'menuitem', 'quantity', 'unit_price', 'price']
        read_only_fields = ['id', 'user', 'unit_price', 'price']
        optional_fields = ['unit_price', 'price']

class ShortOrderItemSerializer(serializers.HyperlinkedModelSerializer):

    title = serializers.CharField(source='get_title')

    class Meta:
        model = OrderItem
        fields=['url', 'title', 'quantity','price']

class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    delivery_crew = UserSerializer()
    orderitems = ShortOrderItemSerializer(many=True, source='orderitem_set')

    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew',
                  'status', 'orderitems', 'total', 'date']
        read_only_fields = ['id', 'user', 'total']
        optional_fields = ['delivery_crew', 'total', 'status']
