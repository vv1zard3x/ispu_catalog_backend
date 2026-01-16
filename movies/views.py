from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Movie, Genre, MovieCast
from .serializers import (
    MovieListSerializer, 
    MovieDetailSerializer, 
    GenreSerializer, 
    MovieCastSerializer
)


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    """API для фильмов"""
    queryset = Movie.objects.prefetch_related('genres', 'cast__actor').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['genres']
    search_fields = ['title']
    ordering_fields = ['rating', 'release_date', 'vote_count', 'title']
    ordering = ['-release_date']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MovieDetailSerializer
        return MovieListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Фильтр по жанру через параметр genre
        genre = self.request.query_params.get('genre')
        if genre:
            queryset = queryset.filter(genres__id=genre)
        return queryset

    @action(detail=True, methods=['get'])
    def cast(self, request, pk=None):
        """Получить актёрский состав фильма"""
        movie = self.get_object()
        cast = MovieCast.objects.filter(movie=movie).select_related('actor').order_by('order')
        serializer = MovieCastSerializer(cast, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Поиск фильмов по названию"""
        query = request.query_params.get('q', '')
        queryset = self.queryset.filter(title__icontains=query)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = MovieListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = MovieListSerializer(queryset, many=True)
        return Response({'results': serializer.data})


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    """API для жанров"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = None  # Жанры без пагинации
