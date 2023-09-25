from datetime import datetime, timedelta
from decimal import Decimal
from django.contrib.auth.models import User, Group
from django.forms import model_to_dict
import pytest
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
                          date=datetime.today(), 
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
                          date=datetime.today())
        
        tempOrder.save()
        
        tempOrder.orderitem_set.create(order=tempOrder,
                                    menuitem=self.carts[0].menuitem,
                                    quantity=self.carts[0].quantity)

        self.orders.append(tempOrder)

    def test_orders_list(self):
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

        #check that for each order, order items are also returned
        for order in response.json():
            for orderitem in order['orderitems']:
                    orderitem_from_db = OrderItem.objects.get(id=orderitem['id'])
                    assert orderitem['id'] == orderitem_from_db.id
                    assert orderitem['title'] == orderitem_from_db.menuitem.title
                    assert orderitem['quantity'] == orderitem_from_db.quantity
                    assert Decimal(orderitem['price']) == orderitem_from_db.price
        
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

    def test_order_retrieve(self): 
        url = f"https://{self.domain}/api/orders/"

        order_id = Order.objects.filter(user=self.valid_user_customer_w_order).first().id
        
        #Passing case - Should list every OrderItem for the orderid
        self.client.logout()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.valid_user_customer_w_order_token.key)

        response = self.client.get(url+ f"{order_id}")

        assert response.status_code == status.HTTP_200_OK

        #Checking returned values
        assert order_id == response.json()['id']

        #Wrong user for te given order should return 403
        self.client.logout()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.valid_user_customer_wo_cart_wo_order_token.key)

        response = self.client.get(url+ f"{order_id}")

        assert response.status_code == status.HTTP_403_FORBIDDEN


    def test_order_update(self):
        order = Order.objects.filter(user=self.valid_user_customer_w_order).first()

        # Create minimal data for the update
        order_data = {
            "id": order.id,
            "user": order.user.id,
            "status": True,  # Update the status (required field)
            "date": "2023-09-25", 
            "delivery_crew": order.delivery_crew.id
        }

        # Define the URL for the specific order
        url = f"https://{self.domain}/api/orders/{order.id}"

        ## MANAGER CAN T UPDATE
        # Logout and set credentials to a manager
        self.client.logout()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.valid_user_manager_w_order_token.key)

        # Make the PUT request with minimal order_data
        response = self.client.put(url, data=order_data, format='json')

        # Check the response status code
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Make the PUT request with minimal order_data
        response = self.client.patch(url, data=order_data, format='json')

        # Check the response status code
        assert response.status_code == status.HTTP_200_OK

        dcm_update_order_data = {
            "id": order.id,
            "status": True,  # Only authorized field to be modified by DC member
        }

        ## DC Member CAN UPDATE ONLY ONE FIELD
        # Logout and set credentials to a manager
        self.client.logout()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.valid_user_dcm_w_order_token.key)

        # Make the PUT request with minimal order_data
        response = self.client.put(url, data=order_data, format='json')

        # Check the response status code
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Make the PUT request with minimal order_data
        response = self.client.patch(url, data=order_data, format='json')

        assert response.status_code == status.HTTP_200_OK

        # Make the PUT request with minimal order_data
        response = self.client.patch(url, data=dcm_update_order_data, format='json')

        # Check the response status code
        assert response.status_code == status.HTTP_200_OK


        # Logout and set credentials to customer that owns the order
        self.client.logout()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.valid_user_customer_w_order_token.key)

        # Make the PUT request with minimal order_data
        response = self.client.put(url, data=order_data, format='json')

        # Check the response status code
        assert response.status_code == status.HTTP_200_OK


         # Create minimal data for the update
        previous_value = order.status

        partial_order_data = {
            "id": order.id,
            "status": not order.status,  # Update the status (required field)
        }

        # Make the PUT request with some order_data
        response = self.client.patch(url, data=partial_order_data, format='json')

        # Check the response status code
        assert response.status_code == status.HTTP_200_OK

        # Check the value actually changed
        assert not response.json()["status"] == previous_value


         # Logout and set credentials to customer that doesnt own the order
        self.client.logout()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.valid_user_customer_wo_cart_wo_order_token.key)

        # Make the PUT request with minimal order_data
        response = self.client.put(url, data=order_data, format='json')

        # Check the response status code
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_order_delete(self):
         
        order = Order.objects.filter(user=self.valid_user_customer_w_order).first()
        orderitems_ids = {orderitem.id for orderitem in OrderItem.objects.filter(order_id=order.id).all()}

         # Define the URL for the specific order
        url = f"https://{self.domain}/api/orders/{order.id}"


        ## Customer CANT DELETE, even if owner
        # Logout and set credentials to a customer
        self.client.logout()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.valid_user_customer_w_order_token.key)

        # Make the PUT request with minimal order_data
        response = self.client.delete(url)

        # Check the response status code
        assert response.status_code == status.HTTP_403_FORBIDDEN


        ## DCMember CANT DELETE
        # Logout and set credentials to a dcm member
        self.client.logout()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.valid_user_dcm_w_order_token.key)

        # Make the PUT request with minimal order_data
        response = self.client.delete(url)

        # Check the response status code
        assert response.status_code == status.HTTP_403_FORBIDDEN



        ## MANAGER CAN DELETE
        # Logout and set credentials to a manager
        self.client.logout()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.valid_user_manager_w_order_token.key)

        # Make the PUT request with minimal order_data
        response = self.client.delete(url)

        # Check the response status code
        assert response.status_code == status.HTTP_204_NO_CONTENT

        with pytest.raises(Order.DoesNotExist):
            order.refresh_from_db()

        for orderitem_id in orderitems_ids:
            with pytest.raises(OrderItem.DoesNotExist):
                OrderItem.objects.get(id=orderitem_id)
