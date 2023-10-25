from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Booking, Menu

class MenuItemSerializer(ModelSerializer):
    

    class Meta: 
        model = Menu
        fields = '__all__'


class BookingSerializer(ModelSerializer):
    
       class Meta: 
        model = Booking
        fields = '__all__'



class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']