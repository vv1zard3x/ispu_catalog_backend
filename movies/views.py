from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Movie, Genre, Actor, MovieCast
from .serializers import (
    MovieListSerializer, 
    MovieDetailSerializer, 
    GenreSerializer, 
    MovieCastSerializer,
    ActorSerializer
)


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    """API для фильмов"""
    queryset = Movie.objects.prefetch_related('genres', 'cast__actor').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['genres']
    search_fields = ['title', 'overview']
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
        
        # Фильтр по актёру
        actor = self.request.query_params.get('actor')
        if actor:
            queryset = queryset.filter(cast__actor__id=actor)
        
        # Фильтр по году выхода
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(release_date__year=year)
        
        # Фильтр по минимальному рейтингу
        min_rating = self.request.query_params.get('min_rating')
        if min_rating:
            queryset = queryset.filter(rating__gte=float(min_rating))
        
        return queryset.distinct()

    @action(detail=True, methods=['get'])
    def cast(self, request, pk=None):
        """Получить актёрский состав фильма"""
        movie = self.get_object()
        cast = MovieCast.objects.filter(movie=movie).select_related('actor').order_by('order')
        serializer = MovieCastSerializer(cast, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Поиск фильмов по названию и описанию"""
        query = request.query_params.get('q', '')
        queryset = self.queryset.filter(
            Q(title__icontains=query) | Q(overview__icontains=query)
        )
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
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    pagination_class = None


class ActorViewSet(viewsets.ReadOnlyModelViewSet):
    """API для актёров"""
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def movies(self, request, pk=None):
        """Получить фильмы актёра"""
        actor = self.get_object()
        movies = Movie.objects.filter(cast__actor=actor).distinct()
        page = self.paginate_queryset(movies)
        if page is not None:
            serializer = MovieListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = MovieListSerializer(movies, many=True)
        return Response({'results': serializer.data})
