from rest_framework.routers import DefaultRouter
from .views import AppUserViewSet


router = DefaultRouter()
router.register(r'users', AppUserViewSet, basename='appuser')

urlpatterns = router.urls
