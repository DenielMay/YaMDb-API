from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import get_jwt_token, register, UserViewSet

router = DefaultRouter()

router.register('users', UserViewSet)

urlpatterns = [
    path('v1/auth/signup/', register, name='register'),
    path('v1/auth/token/', get_jwt_token, name='token'),
    path('v1/', include(router.urls)),
]
