from django.contrib.auth.models import User, Group
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from LittleLemonAPI.models import Cart, Category, MenuItem

class test_CartManagement(APITestCase):
     
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        
        self.domain = 'localhost:8000'

        self.validUserPassword = 'pass1234'

        self.valid_user_customer_w_cart =  User.objects.create_user(
            email='cart@test.com', 
            username='mrCartCustomer', 
            password=self.validUserPassword)
        self.valid_user_customer_w_cart.save()
        self.valid_user_customer_w_cart_token = Token.objects.get_or_create(user=self.valid_user_customer_w_cart)[0]
        self.valid_user_customer_w_cart_token.save()

        self.valid_user_customer_wo_cart =  User.objects.create_user(
            email='nocart_customer@test.com', 
            username='mrNoCartCustomer', 
            password=self.validUserPassword)
        self.valid_user_customer_wo_cart.save()
        self.valid_user_customer_wo_cart_token = Token.objects.get_or_create(user=self.valid_user_customer_wo_cart)[0]
        self.valid_user_customer_wo_cart_token.save()
        self.menuitems = []

        self.menuitems.append(MenuItem.objects.create(
            title="Burger", 
            price=5.00, 
            featured=False,
            category=Category.objects.get_or_create(slug="cat1", title="Category1")[0]))

        self.menuitems.append(MenuItem.objects.create(
            title="Pasta", 
            price=20.00, 
            featured=True,
            category=Category.objects.get_or_create(slug="cat2", title="Category2")[0]))
        
        self.menuitems.append(MenuItem.objects.create(
            title="Bretzels", 
            price=4.00, 
            featured=False,
            category=Category.objects.get_or_create(slug="cat2", title="Category2")[0]))
        

        self.carts = []
        tempCart = Cart(user=self.valid_user_customer_w_cart, 
                        menuitem=self.menuitems[0],
                        quantity=3)
        tempCart.save()
        self.carts.append(tempCart)
        
        tempCart = Cart(user=self.valid_user_customer_w_cart, 
                        menuitem=self.menuitems[1],
                        quantity=2)
        tempCart.save()
        self.carts.append(tempCart)


    
    def test_cart_model_create(self):
        
        #create a cart without price and unit_price
        quantity = 4

        cart = Cart(user=self.valid_user_customer_w_cart,
                     menuitem=self.menuitems[2],
                     quantity=quantity)
        cart.save()
        assert cart.unit_price == self.menuitems[2].price
        assert cart.price == quantity * self.menuitems[2].price

        cart.delete()


    def test_cart_get(self):
         url = f"https://{self.domain}/api/cart/menu-items"

         # return 401 if user is anonymous
         self.client.logout()
         assert self.client.get(url).status_code == status.HTTP_401_UNAUTHORIZED

         # return the items if user is loggedin with existing cart items
         self.client.logout()
         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.valid_user_customer_w_cart_token.key)
         response = self.client.get(url)
         assert response.status_code == status.HTTP_200_OK

        # check all cart items are returned
         db_cart_ids = {cart.id for cart in self.carts}
         response_cart_ids = {cart_item['id'] for cart_item in response.json()}
         assert db_cart_ids == response_cart_ids

        # return 404 if user is loggedin but without any cart item
         self.client.logout()
         self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.valid_user_customer_wo_cart_token.key)
         assert self.client.get(url).status_code == status.HTTP_404_NOT_FOUND

    def test_cart_post(self):

        url = f"https://{self.domain}/api/cart/menu-items"


        data={"menuitem":self.menuitems[0].id,
              "quantity":4}
        
        missing_data={"menuitem":self.menuitems[0].id}

        # return 401 if user not authentified
        self.client.logout()
        response = self.client.post(url, data=data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


        # return 201 if user is loggedin and add a menu item
        self.client.logout()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.valid_user_customer_wo_cart_token.key)

        response = self.client.post(url, data=data)
        assert response.status_code == status.HTTP_201_CREATED

        assert response.json()['menuitem'] == self.menuitems[0].id
        assert int(response.json()['quantity']) == data['quantity']
        assert response.json()['user'] == self.valid_user_customer_wo_cart.id
        
        Cart.objects.filter(user=self.valid_user_customer_wo_cart).delete()

        # return  if missing data
        response = self.client.post(url, data=missing_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_cart_delete(self):
        url = f"https://{self.domain}/api/cart/menu-items"

        self.client.logout()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.valid_user_customer_w_cart_token.key)
        assert Cart.objects.filter(user=self.valid_user_customer_w_cart).exists()
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_200_OK
        assert not Cart.objects.filter(user=self.valid_user_customer_w_cart).exists()

         