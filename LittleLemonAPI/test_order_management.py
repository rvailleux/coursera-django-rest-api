from datetime import date
import time
from django.contrib.auth.models import User, Group
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from LittleLemonAPI.models import Cart, Category, MenuItem, Order, OrderItem

class test_OrderManagement(APITestCase):
     
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

        self.valid_user_manager_w_order =  User.objects.create_user(
            email='manager@test.com', 
            username='mrManagerOrderCustomer', 
            password=self.validUserPassword)
        self.valid_user_manager_w_order.groups.add(self.manager_group)
        self.valid_user_manager_w_order.save()
        self.valid_user_manager_w_order_token = Token.objects.get_or_create(user=self.valid_user_manager_w_order)[0]
        self.valid_user_manager_w_order_token.save()

        self.valid_user_customer_w_cart_wo_order =  User.objects.create_user(
            email='customerCartNoOrder@test.com', 
            username='CartNoOrderCustomer', 
            password=self.validUserPassword)
        self.valid_user_customer_w_cart_wo_order.save()
        self.valid_user_customer_w_cart_wo_order_token = Token.objects.get_or_create(user=self.valid_user_customer_w_cart_wo_order)[0]
        self.valid_user_customer_w_cart_wo_order_token.save()

        self.valid_user_dcms = []
        valid_user_temp = User.objects.create_user(
            email='deliver@test.com', 
            username='msDeliveryCrew', 
            password=self.validUserPassword)
        valid_user_temp.groups.add(self.dc_group)
        valid_user_temp.save()
        self.valid_user_dcm_w_order_token = Token.objects.get_or_create(user=valid_user_temp)[0]
        self.valid_user_dcm_w_order_token.save()
        self.valid_user_dcms.append(valid_user_temp)

        self.valid_user_customer_w_order =  User.objects.create_user(
            email='cart@test.com', 
            username='mrCartCustomer', 
            password=self.validUserPassword)
        self.valid_user_customer_w_order.save()
        self.valid_user_customer_w_order_token = Token.objects.get_or_create(user=self.valid_user_customer_w_order)[0]
        self.valid_user_customer_w_order_token.save()

        self.valid_user_customer_wo_cart_wo_order =  User.objects.create_user(
            email='nocart_noorder_customer@test.com', 
            username='mrNoCartNoOrderCustomer', 
            password=self.validUserPassword)
        self.valid_user_customer_wo_cart_wo_order.save()
        self.valid_user_customer_wo_cart_wo_order_token = Token.objects.get_or_create(user=self.valid_user_customer_wo_cart_wo_order)[0]
        self.valid_user_customer_wo_cart_wo_order_token.save()

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
        tempCart = Cart(user=self.valid_user_customer_w_cart_wo_order, 
                        menuitem=self.menuitems[0],
                        quantity=3)
        tempCart.save()
        self.carts.append(tempCart)
        
        tempCart = Cart(user=self.valid_user_customer_w_cart_wo_order, 
                        menuitem=self.menuitems[1],
                        quantity=2)
        tempCart.save()
        self.carts.append(tempCart)
        
        #initiatlize Order

        self.orders = []
        tempOrder = Order(user=self.valid_user_customer_w_order,
                          date=date.today(), 
                          delivery_crew = self.valid_user_dcms[0])
        
        tempOrder.save()
        
        tempOrder.orderitem_set.create(order=tempOrder,
                                    menuitem=self.carts[0].menuitem,
                                    quantity=self.carts[0].quantity)
        
        tempOrder.orderitem_set.create(order=tempOrder,
                                    menuitem=self.carts[1].menuitem,
                                    quantity=self.carts[1].quantity)
        
        self.orders.append(tempOrder)


        tempOrder = Order(user=self.valid_user_manager_w_order,
                          date=date.today())
        
        tempOrder.save()
        
        tempOrder.orderitem_set.create(order=tempOrder,
                                    menuitem=self.carts[0].menuitem,
                                    quantity=self.carts[0].quantity)

        self.orders.append(tempOrder)

    def test_order_list(self):
        url = f"https://{self.domain}/api/orders"

        # not authenticated
        self.client.logout()
        response = self.client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # CUSTOMER
        self.client.logout()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.valid_user_customer_w_order_token.key)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        # check all and only users orders are returned
        db_orders_ids = {order.id for order in self.valid_user_customer_w_order.order_set.all()}
        response_order_ids = {order['id'] for order in response.json()}
        assert db_orders_ids == response_order_ids

        # MANAGER
        self.client.logout()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.valid_user_manager_w_order_token.key)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        # check all orders are returned
        db_orders_ids = {order.id for order in Order.objects.all()}
        response_order_ids = {order['id'] for order in response.json()}
        assert db_orders_ids == response_order_ids

        # DC Members
        self.client.logout()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.valid_user_dcm_w_order_token.key)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        # check all orders where the delivery crew member is assigned to are returned
        db_orders_ids = {order.id for order in Order.objects.filter(delivery_crew_id=self.valid_user_dcms[0].id)}
        response_order_ids = {order['id'] for order in response.json()}
        assert db_orders_ids == response_order_ids
        
    def test_order_add(self): 
        url = f"https://{self.domain}/api/orders"

        data = {
            
        }

        self.client.logout()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.valid_user_customer_w_cart_wo_order_token.key)

        #Order Created - Cart items removed
        assert Cart.objects.filter(user=self.valid_user_customer_w_cart_wo_order).exists()
        assert not Order.objects.filter(user=self.valid_user_customer_w_cart_wo_order).exists()   

        cart_menuitem_ids = {cart_item.menuitem_id for cart_item in Cart.objects.filter(user=self.valid_user_customer_w_cart_wo_order)}

        response = self.client.post(url, data)

        assert not Cart.objects.filter(user=self.valid_user_customer_w_cart_wo_order).exists()
        assert Order.objects.filter(user=self.valid_user_customer_w_cart_wo_order).exists() 

        # Order items correspond to former cart items in db
        new_order_id = Order.objects.get(user=self.valid_user_customer_w_cart_wo_order).id
        new_order_menuitems_ids = {orderitem.menuitem_id for orderitem in OrderItem.objects.filter(order_id=new_order_id)}
                                   
        assert new_order_menuitems_ids == cart_menuitem_ids


        #No Cart items return 404 and no order created
        self.client.logout()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.valid_user_customer_wo_cart_wo_order_token.key)
        
        assert not Cart.objects.filter(user=self.valid_user_customer_wo_cart_wo_order).exists()
        assert not Order.objects.filter(user=self.valid_user_customer_wo_cart_wo_order).exists() 

        response = self.client.post(url, data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

        assert not Order.objects.filter(user=self.valid_user_customer_wo_cart_wo_order).exists() 

