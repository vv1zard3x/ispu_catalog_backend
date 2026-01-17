from rest_framework import serializers
from .models import Movie, Genre, Actor, MovieCast


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров"""
    class Meta:
        model = Genre
        fields = ['id', 'name']


class ActorSerializer(serializers.ModelSerializer):
    """Сериализатор для актёров"""
    profile_path = serializers.SerializerMethodField()

    class Meta:
        model = Actor
        fields = ['id', 'name', 'profile_path']

    def get_profile_path(self, obj):
        return obj.get_profile_url()


class MovieCastSerializer(serializers.ModelSerializer):
    """Сериализатор для актёрского состава"""
    id = serializers.IntegerField(source='actor.id', read_only=True)
    name = serializers.CharField(source='actor.name', read_only=True)
    profile_path = serializers.SerializerMethodField()

    class Meta:
        model = MovieCast
        fields = ['id', 'name', 'character', 'profile_path']

    def get_profile_path(self, obj):
        return obj.actor.get_profile_url()


class MovieListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка фильмов"""
    genre_ids = serializers.SerializerMethodField()
    poster_path = serializers.SerializerMethodField()
    backdrop_path = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'overview', 'poster_path', 'backdrop_path',
            'rating', 'release_date', 'vote_count', 'genre_ids'
        ]

    def get_genre_ids(self, obj):
        return list(obj.genres.values_list('id', flat=True))

    def get_poster_path(self, obj):
        return obj.get_poster_url()

    def get_backdrop_path(self, obj):
        return obj.get_backdrop_url()


class MovieDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для деталей фильма"""
    genre_ids = serializers.SerializerMethodField()
    poster_path = serializers.SerializerMethodField()
    backdrop_path = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'overview', 'poster_path', 'backdrop_path',
            'rating', 'release_date', 'vote_count', 'genre_ids'
        ]

    def get_genre_ids(self, obj):
        return list(obj.genres.values_list('id', flat=True))

    def get_poster_path(self, obj):
        return obj.get_poster_url()

    def get_backdrop_path(self, obj):
        return obj.get_backdrop_url()
