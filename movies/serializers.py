from rest_framework import serializers
from .models import Movie, Genre, Actor, MovieCast, Country, MovieSource


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров"""
    class Meta:
        model = Genre
        fields = ['id', 'name']


class CountrySerializer(serializers.ModelSerializer):
    """Сериализатор для стран"""
    class Meta:
        model = Country
        fields = ['id', 'name']


class MovieSourceSerializer(serializers.ModelSerializer):
    """Сериализатор для источников"""
    class Meta:
        model = MovieSource
        fields = ['id', 'name', 'url', 'description']


class ActorSerializer(serializers.ModelSerializer):
    """Сериализатор для актёров"""
    profile_path = serializers.SerializerMethodField()

    class Meta:
        model = Actor
        fields = ['id', 'name', 'profile_path', 'kinopoisk_id']

    def get_profile_path(self, obj):
        return obj.get_profile_url()


class MovieCastSerializer(serializers.ModelSerializer):
    """Сериализатор для актёрского состава"""
    id = serializers.IntegerField(source='actor.id', read_only=True)
    name = serializers.CharField(source='actor.name', read_only=True)
    kinopoisk_id = serializers.IntegerField(source='actor.kinopoisk_id', read_only=True)
    profile_path = serializers.SerializerMethodField()

    class Meta:
        model = MovieCast
        fields = ['id', 'name', 'character', 'profile_path', 'kinopoisk_id']

    def get_profile_path(self, obj):
        return obj.actor.get_profile_url()


class MovieListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка фильмов"""
    genre_ids = serializers.SerializerMethodField()
    poster_path = serializers.SerializerMethodField()
    backdrop_path = serializers.SerializerMethodField()
    countries = CountrySerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'name_original', 'overview', 'poster_path', 'backdrop_path',
            'rating', 'release_date', 'vote_count', 'genre_ids', 'countries', 
            'age_rating', 'film_length', 'type'
        ]

    def get_genre_ids(self, obj):
        return list(obj.genres.values_list('id', flat=True))

    def get_poster_path(self, obj):
        return obj.get_poster_url()

    def get_backdrop_path(self, obj):
        return obj.get_backdrop_url()


class MovieDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для деталей фильма"""
    genres = GenreSerializer(many=True, read_only=True)
    countries = CountrySerializer(many=True, read_only=True)
    sources = MovieSourceSerializer(many=True, read_only=True)
    cast = serializers.SerializerMethodField()
    poster_path = serializers.SerializerMethodField()
    backdrop_path = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'name_original', 'overview', 'poster_path', 'backdrop_path',
            'rating', 'release_date', 'vote_count', 'genres', 'countries',
            'slogan', 'film_length', 'age_rating', 'type', 'imdb_id', 'kinopoisk_id',
            'sources', 'cast'
        ]

    def get_cast(self, obj):
        # Получаем cast отсортированный по order
        cast = MovieCast.objects.filter(movie=obj).select_related('actor').order_by('order')
        return MovieCastSerializer(cast, many=True).data

    def get_poster_path(self, obj):
        return obj.get_poster_url()

    def get_backdrop_path(self, obj):
        return obj.get_backdrop_url()

