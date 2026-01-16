from django.contrib import admin
from .models import Genre, Actor, Movie, MovieCast


class MovieCastInline(admin.TabularInline):
    """Inline для актёрского состава в фильме"""
    model = MovieCast
    extra = 1
    autocomplete_fields = ['actor']


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'profile_path']
    search_fields = ['name']


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'rating', 'release_date', 'vote_count']
    list_filter = ['genres', 'release_date']
    search_fields = ['title', 'overview']
    filter_horizontal = ['genres']
    inlines = [MovieCastInline]
    date_hierarchy = 'release_date'


@admin.register(MovieCast)
class MovieCastAdmin(admin.ModelAdmin):
    list_display = ['id', 'movie', 'actor', 'character', 'order']
    list_filter = ['movie']
    search_fields = ['actor__name', 'character', 'movie__title']
    autocomplete_fields = ['movie', 'actor']
