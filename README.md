# README

## Installation

```bash
cd LittleLemon

pipenv shell

pipenv install 

python manage.py makemigrations 

python manage.py migrate

#This should start a server accessible on 127.0.0.1:8000
python manage.py runserver

```

## Credentials: 

Admin credentials
> user: admin
> password: admin12345

User of group 'Manager'
> user: manager
> password: admin12345

User of group 'Delivery_crew'
> user: delivery-crew-member
> password: admin12345

User with no group
> user: customer
> password: admin12345

## Review

## Prerequisites

Please consider retrieving the tokens beforehand through the /token/login endpoint

`curl --location 'http://127.0.0.1:8000/token/login/' --form 'username="admin"' --form 'password="admin12345"'`
`curl --location 'http://127.0.0.1:8000/token/login/' --form 'username="manager"' --form 'password="admin12345"'`
`curl --location 'http://127.0.0.1:8000/token/login/' --form 'username="delivery-crew-member"' --form 'password="admin12345"'`
`curl --location 'http://127.0.0.1:8000/token/login/' --form 'username="customer"' --form 'password="admin12345"'`

We will use the following variable in the CLI:

```bash
$ADMIN_TOKEN
$MANAGER_TOKEN
$DCM_TOKEN
$CUSTOMER_TOKEN
```

1. The admin can assign users to the manager group

```bash
curl --location 'http://127.0.0.1:8000/api/groups/manager/users' \
--header "Authorization: Token $ADMIN_TOKEN" \
--form 'username="customer"'
```

2. You can access the manager group with an admin token

```bash
curl --location 'http://127.0.0.1:8000/api/groups/manager/users'\
--header "Authorization: Token $ADMIN_TOKEN"
```

3. The admin can add menu items

```bash
curl --location 'http://127.0.0.1:8000/api/menu-items' \
--header "Authorization: Token $ADMIN_TOKEN" \
--form 'title="New menu item"' \
--form 'price="2.3"' \
--form 'featured="False"' \
--form 'category="1"'
```

4. The admin can add categories

```bash
curl --location 'http://127.0.0.1:8000/api/categories' \
--header "Authorization: Token $ADMIN_TOKEN" \
--form 'title="New Category"' \
--form 'slug="new-category"'
```

5. Managers can log in 
   
`curl --location 'http://127.0.0.1:8000/token/login/' --form 'username="manager"' --form 'password="admin12345"'`


6. Managers can update the item of the day

```bash
curl --location --request PATCH 'http://127.0.0.1:8000/api/menu-items/1' \
--header "Authorization: Token $MANAGER_TOKEN" \
--form 'featured="false"'

curl --location --request PATCH 'http://127.0.0.1:8000/api/menu-items/2' \
--header "Authorization: Token $MANAGER_TOKEN" \
--form 'featured="true"'
```

7. Managers can assign users to the delivery crew

```bash
curl --location 'http://127.0.0.1:8000/api/groups/delivery-crew/users' \
--header "Authorization: Token $MANAGER_TOKEN" \
--form 'username="customer"'
```

8. Managers can assign orders to the delivery crew
```bash
curl --location --request PATCH 'http://127.0.0.1:8000/api/orders/1' \
--header "Authorization: Token $MANAGER_TOKEN" \
--form 'delivery_crew="7"'
```

9. The delivery crew can access orders assigned to them
```bash
curl --location 'http://127.0.0.1:8000/api/orders'
--header "Authorization: Token $DCM_TOKEN" \
```

10.	The delivery crew can update an order as delivered
```bash
curl --location --request PATCH 'http://127.0.0.1:8000/api/orders/1' \
--header "Authorization: Token $DCM_TOKEN" \
--form 'status="1"'
```

11.	Customers can register

```bash
curl --location 'http://127.0.0.1:8000/api/users/' \
--form 'username="new_user"' \
--form 'email="newuser@email.com"' \
--form 'password="pass12345"'
```

12.	Customers can log in using their username and password and get access tokens
`curl --location 'http://127.0.0.1:8000/token/login/' --form 'username="customer"' --form 'password="pass12345"'`

13.	Customers can browse all categories

```bash
curl --location 'http://127.0.0.1:8000/api/categories'

curl --location 'http://127.0.0.1:8000/api/categories/1'
```

14.	Customers can browse all the menu items at once
```bash
curl --location 'http://127.0.0.1:8000/api/menu-items'
```

15.	Customers can browse menu items by category

```bash
curl --location 'http://127.0.0.1:8000/api/categories/1/menu-items'
```

16. Customers can paginate menu items

```bash
curl --location 'http://127.0.0.1:8000/api/menu-items?page=2'
```

17.	Customers can sort menu items by price

```bash
curl --location 'http://127.0.0.1:8000/api/menu-items?ordering=price'
```

18.  Customers can add menu items to the cart

```bash
curl --location 'http://127.0.0.1:8000/api/cart/menu-items' \
--header "Authorization: Token $CUSTOMER_TOKEN" \
--form 'menuitem="8"' \
--form 'quantity="2"'
```

19. Customers can access previously added items in the cart

```bash
curl --location 'http://127.0.0.1:8000/api/cart/menu-items'\
--header "Authorization: Token $CUSTOMER_TOKEN" 
```

20. Customers can place orders

```bash
curl --location --request POST 'http://127.0.0.1:8000/api/orders' \
--header "Authorization: Token $CUSTOMER_TOKEN" 
```

21.	Customers can browse their own orders

```bash
curl --location 'http://127.0.0.1:8000/api/orders' \
--header "Authorization: Token $CUSTOMER_TOKEN" 
```