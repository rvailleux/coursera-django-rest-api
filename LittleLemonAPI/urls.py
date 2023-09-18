
from django.urls import include, path

from LittleLemonAPI.views import CartManagementView, MenuItemsView, UsersByGroupView

urlpatterns = [
    path('menu-items', MenuItemsView.as_view({'get': 'list', 'post':'create'}), name="MenuItems"),
    path('menu-items/<int:pk>', MenuItemsView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch':'partial_update', 
        'delete': 'destroy'}), name="MenuItem"),
    path('groups/<str:groupname>/users', 
         UsersByGroupView.as_view({'get':'list', 'post':'update'})),
    path('groups/<str:groupname>/<int:user_id>', 
         UsersByGroupView.as_view({'delete':'destroy'})),

    path('cart/menu-items', CartManagementView.as_view({'get': 'list'}))

        
]
