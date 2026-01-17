from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes

from .models import Movie, Genre, Actor, MovieCast
from .serializers import (
    MovieListSerializer, 
    MovieDetailSerializer, 
    GenreSerializer, 
    MovieCastSerializer,
    ActorSerializer
)


@extend_schema_view(
    list=extend_schema(
        summary="Список фильмов",
        description="Получить список всех фильмов с пагинацией, фильтрацией и сортировкой.",
        parameters=[
            OpenApiParameter(name='genre', description='ID жанра для фильтрации', type=OpenApiTypes.INT),
            OpenApiParameter(name='actor', description='ID актёра для фильтрации', type=OpenApiTypes.INT),
            OpenApiParameter(name='year', description='Год выхода фильма', type=OpenApiTypes.INT),
            OpenApiParameter(name='min_rating', description='Минимальный рейтинг (например: 8.0)', type=OpenApiTypes.FLOAT),
            OpenApiParameter(name='search', description='Поиск по названию и описанию', type=OpenApiTypes.STR),
            OpenApiParameter(name='ordering', description='Сортировка: rating, -rating, release_date, -release_date, vote_count, title', type=OpenApiTypes.STR),
        ],
        tags=['movies']
    ),
    retrieve=extend_schema(
        summary="Детали фильма",
        description="Получить полную информацию о фильме по ID.",
        tags=['movies']
    ),
)
class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для работы с фильмами.
    
    Поддерживает фильтрацию по жанрам, актёрам, году выхода и рейтингу.
    Поиск по названию и описанию. Сортировка по различным полям.
    """
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

    @extend_schema(
        summary="Актёрский состав",
        description="Получить список актёров, снимавшихся в данном фильме.",
        responses={200: MovieCastSerializer(many=True)},
        tags=['movies']
    )
    @action(detail=True, methods=['get'])
    def cast(self, request, pk=None):
        """Получить актёрский состав фильма"""
        movie = self.get_object()
        cast = MovieCast.objects.filter(movie=movie).select_related('actor').order_by('order')
        serializer = MovieCastSerializer(cast, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Поиск фильмов",
        description="Поиск фильмов по названию и описанию.",
        parameters=[
            OpenApiParameter(name='q', description='Поисковый запрос', type=OpenApiTypes.STR, required=True),
        ],
        responses={200: MovieListSerializer(many=True)},
        tags=['movies']
    )
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


@extend_schema_view(
    list=extend_schema(
        summary="Список жанров",
        description="Получить список всех жанров фильмов.",
        tags=['genres']
    ),
    retrieve=extend_schema(
        summary="Детали жанра",
        description="Получить информацию о жанре по ID.",
        tags=['genres']
    ),
)
class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    """API для работы с жанрами фильмов."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    pagination_class = None


@extend_schema_view(
    list=extend_schema(
        summary="Список актёров",
        description="Получить список всех актёров с пагинацией.",
        tags=['actors']
    ),
    retrieve=extend_schema(
        summary="Детали актёра",
        description="Получить информацию об актёре по ID.",
        tags=['actors']
    ),
)
class ActorViewSet(viewsets.ReadOnlyModelViewSet):
    """API для работы с актёрами."""
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']

    @extend_schema(
        summary="Фильмы актёра",
        description="Получить список фильмов, в которых снимался данный актёр.",
        responses={200: MovieListSerializer(many=True)},
        tags=['actors']
    )
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
