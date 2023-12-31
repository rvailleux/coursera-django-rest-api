from django.urls import include, path
from .views import BookingViewSet, SingleMenuItemView, MenuItemsView, index
from rest_framework.routers import DefaultRouter

#import obtain_auth_token view
from rest_framework.authtoken.views import obtain_auth_token



router = DefaultRouter()
router.register(r'tables', BookingViewSet)

urlpatterns = [
path('', index , name='home'),
path('api/menu/', MenuItemsView.as_view(), name="menu-items"),
path('api/menu/<int:pk>', SingleMenuItemView.as_view({'get': 'retrieve', 'delete': 'destroy', 'put': 'update'})),
path('api/booking/', include(router.urls)),
path('api-token-auth/', obtain_auth_token)
]

