from rest_framework import serializers
from django.contrib.auth.models import User, Group
from LittleLemonAPI.models import Category, MenuItem

class MenuItemSerializer(serializers.ModelSerializer):

    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model =  MenuItem
        fields = ['title', 'price', 'featured', 'category', 'category_id']
        read_only_fields = ['category']

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        name = Group.objects.all()
        model =  Group
        fields = ['name']


class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)
    class Meta:
        model =  User
        fields = ['username', 'email', 'id', 'groups']
        read_only_fields = ['username', 'email', 'id']

