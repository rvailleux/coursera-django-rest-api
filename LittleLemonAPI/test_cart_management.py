from django.contrib.auth.models import User, Group
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

class test_UserGroups(APITestCase):
     
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        
        self.domain = 'localhost:8000'

        self.validUserPassword = 'pass1234'

        self.valid_user_managers = []

        self.manager_group = Group.objects.create(name='manager')
        self.manager_group.save()

        self.dc_group = Group.objects.create(name='delivery-crew')
        self.dc_group.save()

        valid_user_temp = User.objects.create_user(
            email='manager@test.com', 
            username='mrManager', 
            password=self.validUserPassword)
        valid_user_temp.groups.add(self.manager_group)
        valid_user_temp.save()

        self.valid_user_managers.append(valid_user_temp)

        valid_user_temp = User.objects.create_user(
            email='manager2@test.com', 
            username='mrManager2', 
            password=self.validUserPassword)
        valid_user_temp.groups.add(self.manager_group)
        valid_user_temp.save()
        self.valid_user_managers.append(valid_user_temp)

        self.valid_user_dcms = []
        valid_user_temp = User.objects.create_user(
            email='deliver@test.com', 
            username='msDeliveryCrew', 
            password=self.validUserPassword)
        valid_user_temp.groups.add(self.dc_group)
        valid_user_temp.save()
        self.valid_user_dcms.append(valid_user_temp)

        valid_user_temp = User.objects.create_user(
            email='deliver2@test.com', 
            username='msDeliveryCrew2', 
            password=self.validUserPassword)
        valid_user_temp.groups.add(self.dc_group)
        valid_user_temp.save()
        self.valid_user_dcms.append(valid_user_temp)

        self.valid_user_no_group_customer =  User.objects.create_user(
            email='nogroup@test.com', 
            username='mrNoGroup', 
            password=self.validUserPassword)
        self.valid_user_no_group_customer.save()
    
    def test_cart_get(self):
        url = f"https://{self.domain}/api/cart/menu-item"


        self.client.logout()
        assert self.client.get(url).status_code == status.HTTP_401_UNAUTHORIZED