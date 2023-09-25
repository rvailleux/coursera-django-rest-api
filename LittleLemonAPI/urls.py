
from django.urls import path

from LittleLemonAPI.views import CartView, CategoriesView, CategoryView, MenuItemsInCategoryView, MenuItemsView, OrderView, UsersByGroupView, OrdersView

urlpatterns = [
    path('menu-items', MenuItemsView.as_view({
        'get': 'list', 
        'post':'create'}), name="MenuItems"),

    path('menu-items/<int:pk>', MenuItemsView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch':'partial_update', 
        'delete': 'destroy'}), name="menuitem-detail"),

    path('categories', CategoriesView.as_view()),
    path('categories/<int:pk>', CategoryView.as_view()),
    path('categories/<int:pk>/menu-items', MenuItemsInCategoryView.as_view()),

    path('groups/<str:groupname>/users', UsersByGroupView.as_view({
             'get':'list', 
             'post':'update'})),

    path('groups/<str:groupname>/<int:user_id>', UsersByGroupView.as_view({
        'delete':'destroy'})),

    path('cart/menu-items', CartView.as_view({
        'get': 'list', 
        'post':'create', 
        'delete':'destroy'})),

    path('orders', OrdersView.as_view()), 

    path('orders/<int:pk>', OrderView.as_view(), name='orderitem-detail')

]