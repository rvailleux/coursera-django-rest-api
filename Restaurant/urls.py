from django.urls import include, path
from .views import BookingViewSet, SingleMenuItemView, MenuItemsView, index
from rest_framework.routers import DefaultRouter



router = DefaultRouter()
router.register(r'tables', BookingViewSet)

urlpatterns = [
path('', index , name='home'),
path('api/menu/', MenuItemsView.as_view(), name="menu-items"),
path('api/menu/<int:pk>', SingleMenuItemView.as_view()),
path('api/booking/', include(router.urls)),
]

