from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MovieViewSet, GenreViewSet

router = DefaultRouter()
router.register(r'movies', MovieViewSet, basename='movie')
router.register(r'genres', GenreViewSet, basename='genre')

urlpatterns = [
    path('', include(router.urls)),
]
