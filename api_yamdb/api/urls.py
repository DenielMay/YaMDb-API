from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, GenreViewSet, TitleViewSet,
    ReviewViewSet, CommentsViewSet,
)

v1_router = DefaultRouter()
v1_router.register(r'categories', CategoryViewSet, basename='categories')
v1_router.register(r'genres', GenreViewSet, basename='genres')
v1_router.register(r'titles', TitleViewSet, basename='titles')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/', include(v1_router.urls)),
]
