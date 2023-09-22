from decimal import Decimal
from django.contrib.auth.models import User, Group
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from LittleLemonAPI.models import Category, MenuItem


class test_MenuItems(APITestCase):
        
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        
        self.domain = "localhost:8000"

        self.validUserPassword = "pass1234"
        self.validUserManager = User.objects.create_user(
            email="manager@test.com", username='mrManager', password=self.validUserPassword)
        self.validUserManager.groups.add(Group.objects.get_or_create(name="manager")[0])
        self.validUserManager.save()


        self.validUserDCM = User.objects.create_user(
            email="deliver@test.com", 
            username='msDeliveryCrew', 
            password=self.validUserPassword)
        self.validUserDCM.groups.add(Group.objects.get_or_create(name="delivery-crew")[0])
        self.validUserDCM.save()

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


    def test_menuitems_list_get_post(self):
        '''
        Test /api/menu-items endpoint for all identified and unidentified users
        '''
        url = f"https://{self.domain}/api/menu-items"

        data= {
            'title': 'Donut', 
            'price' : '2.0',
            'featured': 'false', 
            'category': str(self.menuitem[0].category_id)
        }

        # CUSTOMER
        self.client.logout()
        # GET Test valid when not identified
        response = self.client.get(url)
        self.assertEqual(response.status_code,  status.HTTP_200_OK)
        self.assertEqual(len(response.json()), len(self.menuitem))

        # POST NOK
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code,  status.HTTP_401_UNAUTHORIZED)

        #DELIVERY CREW MEMBERS
        # GET OK
        self.client.force_login(user=self.validUserDCM)
        response = self.client.get(url)
        self.assertEqual(response.status_code,  status.HTTP_200_OK)
        self.assertEqual(len(response.json()), len(self.menuitem))
        self.client.logout()

        # POST NOK
        self.client.force_login(user=self.validUserDCM)
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code,  status.HTTP_403_FORBIDDEN)
        self.client.logout()


        #MANAGER
        # GET Test valid when identified as a user from group manager
        self.client.force_login(user=self.validUserManager)
        response = self.client.get(url)
        self.assertEqual(response.status_code,  status.HTTP_200_OK)
        self.assertEqual(len(response.json()), len(self.menuitem))
        self.client.logout()

         # POST OK
        self.client.force_login(user=self.validUserManager)
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code,  status.HTTP_201_CREATED)
        self.client.logout()
        

    def test_menuitem_retrieve(self):
        '''
        Testing the /api/menu-items/{menuItem} endpoint
        '''

        url = f"https://{self.domain}/api/menu-items/{self.menuitem[0].id}"


        # CUSTOMER
        self.client.logout()
        # GET Test valid when not identified
        response = self.client.get(url)
        self.assertEqual(response.status_code,  status.HTTP_200_OK)
        self.assertEqual(response.json()['title'], self.menuitem[0].title)
        self.assertEqual(Decimal(response.json()['price']), self.menuitem[0].price)
        self.assertEqual(response.json()['featured'], self.menuitem[0].featured)
        self.assertEqual(response.json()['category_id'], self.menuitem[0].category_id)

        # DELIVERY CREW MEMBER
        self.client.force_login(user=self.validUserDCM)
        response = self.client.get(url)
        self.assertEqual(response.status_code,  status.HTTP_200_OK)
        self.assertEqual(response.json()['title'], self.menuitem[0].title)
        self.assertEqual(Decimal(response.json()['price']), self.menuitem[0].price)
        self.assertEqual(response.json()['featured'], self.menuitem[0].featured)
        self.assertEqual(response.json()['category_id'], self.menuitem[0].category_id)

        # MANAGER
        self.client.logout()
        self.client.force_login(user=self.validUserManager)
        response = self.client.get(url)
        self.assertEqual(response.status_code,  status.HTTP_200_OK)
        self.assertEqual(response.json()['title'], self.menuitem[0].title)
        self.assertEqual(Decimal(response.json()['price']), self.menuitem[0].price)
        self.assertEqual(response.json()['featured'], self.menuitem[0].featured)
        self.assertEqual(response.json()['category_id'], self.menuitem[0].category_id)

    def test_menuitem_update(self):
        '''
        Testing the /api/menu-items/{menuItem} endpoint
        '''

        url = f"https://{self.domain}/api/menu-items/{self.menuitem[0].id}"

        data= {
            'title': 'Donut', 
            'price' : 2.0,
            'featured': False, 
            'category': self.menuitem[0].category_id
        }
        
        #PUT
        # CUSTOMER
        self.client.logout()
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code,  status.HTTP_401_UNAUTHORIZED)


        # DELIVERY CREW MEMBER
        self.client.logout()
        self.client.force_login(user=self.validUserDCM)
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code,  status.HTTP_403_FORBIDDEN)

        #MANAGER
        self.client.logout()
        self.client.force_login(user=self.validUserManager)
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code,  status.HTTP_200_OK)
        self.menuitem[0].refresh_from_db()
        self.assertEqual(self.menuitem[0].title, data['title'])
        self.assertEqual(self.menuitem[0].price, data['price'])
        self.assertEqual(self.menuitem[0].featured, data['featured'])
        self.assertEqual(self.menuitem[0].category_id, data['category'])

        #PATCH
        patch_data = { 'price' : 3.0}
        # CUSTOMER
        self.client.logout()
        response = self.client.patch(url, data=patch_data)
        self.assertEqual(response.status_code,  status.HTTP_401_UNAUTHORIZED)


        # DELIVERY CREW MEMBER
        self.client.logout()
        self.client.force_login(user=self.validUserDCM)
        response = self.client.patch(url, data=patch_data)
        self.assertEqual(response.status_code,  status.HTTP_403_FORBIDDEN)

        #MANAGER
        self.client.logout()
        self.client.force_login(user=self.validUserManager)
        response = self.client.patch(url, data=patch_data)
        self.assertEqual(response.status_code,  status.HTTP_200_OK)
        self.menuitem[0].refresh_from_db()
        self.assertEqual(self.menuitem[0].title, data['title'])
        self.assertEqual(self.menuitem[0].price, patch_data['price'])
        self.assertEqual(self.menuitem[0].featured, data['featured'])
        self.assertEqual(self.menuitem[0].category_id, data['category'])

    def test_menuitem_delete(self):
        '''
        Testing the /api/menu-items/{menuItem} endpoint with DELETE query
        '''

        deletedItemId = self.menuitem[0].id
        url = f"https://{self.domain}/api/menu-items/{deletedItemId}"

        self.assertTrue(MenuItem.objects.filter(id=deletedItemId).exists())


        #PUT
        # CUSTOMER
        self.client.logout()
        response = self.client.delete(url)
        self.assertEqual(response.status_code,  status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(MenuItem.objects.filter(id=deletedItemId).exists())

        # DELIVERY CREW MEMBER
        self.client.logout()
        self.client.force_login(user=self.validUserDCM)
        response = self.client.delete(url)
        self.assertEqual(response.status_code,  status.HTTP_403_FORBIDDEN)
        self.assertTrue(MenuItem.objects.filter(id=deletedItemId).exists())

        #MANAGER
        self.client.logout()
        self.client.force_login(user=self.validUserManager)
        response = self.client.delete(url)
        self.assertEqual(response.status_code,  status.HTTP_204_NO_CONTENT)
        self.assertFalse(MenuItem.objects.filter(id=deletedItemId).exists())

