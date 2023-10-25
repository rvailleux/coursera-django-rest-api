from django.urls import include, path
from .views import BookingViewSet, SingleMenuItemView, MenuItemsView
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token


router = DefaultRouter()
router.register(r'tables', BookingViewSet)

urlpatterns = [
path('menu/', MenuItemsView.as_view()),
path('menu/<int:pk>', SingleMenuItemView.as_view()),
path('booking/', include(router.urls)),
#add following line in urlpatterns list
path('api-token-auth/', obtain_auth_token),

]

