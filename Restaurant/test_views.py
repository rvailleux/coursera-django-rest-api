from django.forms import model_to_dict
from django.test import TestCase
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User

from Restaurant.models import MenuItem
from .views import MenuItemsView

class MenuItemsViewTest(TestCase):
    def setUp(self):
        self.menuItems = []
        self.menuItems.append(MenuItem.objects.create(title="IceCream", price=80, inventory=100))
        self.menuItems.append(MenuItem.objects.create(title="Burger", price=120, inventory=100))
        self.menuItems.append(MenuItem.objects.create(title="Salad", price=10, inventory=100))

        self.activeUser = User.objects.create(username="user1", password="django123@")

        self.client = Client()

    def test_getall(self):
        self.client.force_login(self.activeUser)

        url = reverse('menu-items')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)  # Check if the response is successful

        items = response.json()  # Parse JSON response

        self.assertEqual(len(items), len(self.menuItems))  # Check if the number of items matches

        # Check if each item in self.menuItems is present in the response
        for menuItem in self.menuItems:
            self.assertTrue(any(item['title'] == menuItem.title for item in items))
            
