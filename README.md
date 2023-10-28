# Readme

## Installation
- Make sure your mysql database is configured with 'root' as a user and no password: change accordingly to your configuration in settings.py.
- Create a database named 'LittleLemon'
- Run a Mysql import command on the LittleLemon.sql file to populate the LittleLemon database

## Routes to test

### Static content routes

- Homepage: http://127.0.0.1:8000/restaurant

### APIs routes

- List Menus Items: http://127.0.0.1:8000/restaurant/api/menu/
- Details of a Menu items: http://127.0.0.1:8000/restaurant/api/menu/1
- Bookings: http://127.0.0.1:8000/restaurant/api/booking/tables/
- Users management: http://127.0.0.1:8000/auth/users/


### Test 

- Run `python manage.py test` to run models and views tests