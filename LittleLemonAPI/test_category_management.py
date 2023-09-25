from datetime import datetime, timedelta
from decimal import Decimal
from django.contrib.auth.models import User, Group
from django.forms import model_to_dict
import pytest
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from LittleLemonAPI.models import Cart, Category, MenuItem, Order, OrderItem



class test_Categories(APITestCase):
        
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        
        self.domain = "localhost:8000"

        self.validUserPassword = "pass1234"

        self.validUserManager = User.objects.create_user(
            email="manager@test.com", username='mrManager', password=self.validUserPassword)
        self.validUserManager.groups.add(Group.objects.get_or_create(name="manager")[0])
        self.validUserManager.save()        
        self.valid_user_manager_token = Token.objects.get_or_create(user=self.validUserManager)[0]
        self.valid_user_manager_token.save()


        self.validUserDCM = User.objects.create_user(
            email="deliver@test.com", 
            username='msDeliveryCrew', 
            password=self.validUserPassword)
        self.validUserDCM.groups.add(Group.objects.get_or_create(name="delivery-crew")[0])
        self.validUserDCM.save()
        self.valid_user_dcm_token = Token.objects.get_or_create(user=self.validUserDCM)[0]
        self.valid_user_dcm_token.save()

        self.valid_user_customer =  User.objects.create_user(
            email='customerCartNoOrder@test.com', 
            username='CartNoOrderCustomer', 
            password=self.validUserPassword)
        self.valid_user_customer.save()
        self.valid_user_customer_token = Token.objects.get_or_create(user=self.valid_user_customer)[0]
        self.valid_user_customer_token.save()

        self.menuitem = []

        self.menuitem.append(MenuItem.objects.create(
            title="Burger", 
            price=5.00, 
            featured=False,
            category=Category.objects.get_or_create(slug="cat1", title="Category1")[0]))

        self.menuitem.append(MenuItem.objects.create(
            title="Pasta", 
            price=20.00, 
            featured=True,
            category=Category.objects.get_or_create(slug="cat2", title="Category2")[0]))
        
        self.menuitem.append(MenuItem.objects.create(
            title="Bretzels", 
            price=4.00, 
            featured=False,
            category=Category.objects.get_or_create(slug="cat2", title="Category2")[0]))

    def test_category_post(self):
        url = f"https://{self.domain}/api/categories"

        data = {
            'slug': 'new-category',     
            'title': 'New Category',
        }

        # Manager
        self.client.logout()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.valid_user_manager_token.key)
        response = self.client.post(url, data=data)
        assert response.status_code == status.HTTP_201_CREATED
        