from django.contrib import admin
from django.utils.html import format_html
from .models import Genre, Actor, Movie, MovieCast


class MovieCastInline(admin.TabularInline):
    """Inline для актёрского состава в фильме"""
    model = MovieCast
    extra = 1
    autocomplete_fields = ['actor']
    readonly_fields = ['actor_preview']

    def actor_preview(self, obj):
        url = obj.actor.get_profile_url() if obj.actor else None
        if url:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 50%;"/>', url)
        return "-"
    actor_preview.short_description = "Фото"


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'profile_preview']
    search_fields = ['name']
    readonly_fields = ['profile_preview_large']

    def profile_preview(self, obj):
        url = obj.get_profile_url()
        if url:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 50%;"/>', url)
        return "-"
    profile_preview.short_description = "Фото"

    def profile_preview_large(self, obj):
        url = obj.get_profile_url()
        if url:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 200px; border-radius: 8px;"/>', url)
        return "Нет изображения"
    profile_preview_large.short_description = "Превью фото"

    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Фото', {
            'fields': ('profile_image', 'profile_path', 'profile_preview_large'),
        }),
    )


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['id', 'poster_preview', 'title', 'rating', 'release_date', 'vote_count']
    list_filter = ['genres', 'release_date']
    search_fields = ['title', 'overview']
    filter_horizontal = ['genres']
    inlines = [MovieCastInline]
    date_hierarchy = 'release_date'
    readonly_fields = ['poster_preview_large', 'backdrop_preview_large']

    def poster_preview(self, obj):
        url = obj.get_poster_url()
        if url:
            return format_html('<img src="{}" style="max-height: 60px; border-radius: 4px;"/>', url)
        return "-"
    poster_preview.short_description = "Постер"

    def poster_preview_large(self, obj):
        url = obj.get_poster_url()
        if url:
            return format_html('<img src="{}" style="max-height: 300px; border-radius: 8px;"/>', url)
        return "Нет изображения"
    poster_preview_large.short_description = "Превью постера"

    def backdrop_preview_large(self, obj):
        url = obj.get_backdrop_url()
        if url:
            return format_html('<img src="{}" style="max-width: 100%; max-height: 200px; border-radius: 8px;"/>', url)
        return "Нет изображения"
    backdrop_preview_large.short_description = "Превью фона"

    fieldsets = (
        (None, {
            'fields': ('title', 'overview', 'genres')
        }),
        ('Рейтинг и дата', {
            'fields': ('rating', 'vote_count', 'release_date'),
        }),
        ('Постер', {
            'fields': ('poster_image', 'poster_path', 'poster_preview_large'),
        }),
        ('Фон', {
            'fields': ('backdrop_image', 'backdrop_path', 'backdrop_preview_large'),
        }),
    )


@admin.register(MovieCast)
class MovieCastAdmin(admin.ModelAdmin):
    list_display = ['id', 'actor_preview', 'movie', 'actor', 'character', 'order']
    list_filter = ['movie']
    search_fields = ['actor__name', 'character', 'movie__title']
    autocomplete_fields = ['movie', 'actor']

    def actor_preview(self, obj):
        url = obj.actor.get_profile_url() if obj.actor else None
        if url:
            return format_html('<img src="{}" style="max-height: 40px; max-width: 40px; border-radius: 50%;"/>', url)
        return "-"
    actor_preview.short_description = "Фото"
