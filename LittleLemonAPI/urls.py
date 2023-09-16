
from django.urls import include, path

from LittleLemonAPI.views import MenuItemsView, UserViewByGroup

urlpatterns = [
    path('menu-items', MenuItemsView.as_view({'get': 'list', 'post':'create'}), name="MenuItems"),
    path('menu-items/<int:pk>', MenuItemsView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch':'partial_update', 
        'delete': 'destroy'}), name="MenuItem"),
    path('groups/<str:groupname>/users', 
         UserViewByGroup.as_view({'get':'list', 'post':'update'}),)
]
