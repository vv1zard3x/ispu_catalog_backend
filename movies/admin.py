from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.html import format_html
from .models import Genre, Actor, Movie, MovieCast, SiteSettings, Country, MovieSource
from .kinopoisk import KinopoiskService, KinopoiskImportError


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(MovieSource)
class MovieSourceAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'movie', 'name', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'movie__title']


class MovieCastInline(admin.TabularInline):
    """Inline для актёрского состава в фильме"""
    model = MovieCast
    extra = 1
    autocomplete_fields = ['actor']
    readonly_fields = ['actor_preview']

    def actor_preview(self, obj):
        url = obj.actor.get_profile_url() if obj.actor else None
        if url:
            return format_html('<img src="{}" style="max-height: 40px; max-width: 40px; border-radius: 50%;"/>', url)
        return "-"
    actor_preview.short_description = "Фото"


class MovieSourceInline(admin.TabularInline):
    """Inline для источников просмотра"""
    model = MovieSource
    extra = 0


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ['id', 'profile_preview', 'name', 'kinopoisk_id']
    search_fields = ['name', 'kinopoisk_id']
    readonly_fields = ['profile_preview_large']

    def profile_preview(self, obj):
        url = obj.get_profile_url()
        if url:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 50%; object-fit: cover;" />', url)
        return "Нет фото"
    profile_preview.short_description = "Фото"

    def profile_preview_large(self, obj):
        url = obj.get_profile_url()
        if url:
            return format_html('<img src="{}" style="max-height: 300px; max-width: 300px; border-radius: 10px;" />', url)
        return "Нет фото"
    profile_preview_large.short_description = "Превью фото"

    fieldsets = (
        (None, {
            'fields': ('name', 'kinopoisk_id')
        }),
        ('Фото', {
            'fields': ('profile_image', 'profile_path', 'profile_preview_large'),
        }),
    )


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['id', 'poster_preview', 'title', 'rating', 'year_display', 'vote_count']
    list_filter = ['genres', 'release_date', 'countries']
    search_fields = ['title', 'overview', 'kinopoisk_id']
    filter_horizontal = ['genres', 'countries']
    inlines = [MovieSourceInline, MovieCastInline]
    date_hierarchy = 'release_date'
    readonly_fields = ['poster_preview_large', 'backdrop_preview_large']
    change_list_template = "admin/movies/movie/change_list.html"

    def year_display(self, obj):
        return obj.release_date.year if obj.release_date else "-"
    year_display.short_description = "Год"

    def poster_preview(self, obj):
        url = obj.get_poster_url()
        if url:
            return format_html('<img src="{}" style="max-height: 70px; border-radius: 5px;" />', url)
        return "Нет постера"
    poster_preview.short_description = "Постер"

    def poster_preview_large(self, obj):
        url = obj.get_poster_url()
        if url:
            return format_html('<img src="{}" style="max-height: 400px; border-radius: 10px;" />', url)
        return "Нет постера"
    poster_preview_large.short_description = "Постер (Full)"

    def backdrop_preview_large(self, obj):
        url = obj.get_backdrop_url()
        if url:
            return format_html('<img src="{}" style="max-height: 300px; border-radius: 10px;" />', url)
        return "Нет фона"
    backdrop_preview_large.short_description = "Фон"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-kinopoisk/', self.admin_site.admin_view(self.import_kinopoisk_view), name='movies_movie_import_kinopoisk'),
        ]
        return custom_urls + urls

    def import_kinopoisk_view(self, request):
        context = {
            'title': 'Импорт с Кинопоиск'
        }
        
        if request.method == 'POST':
            url = request.POST.get('kinopoisk_url')
            if url:
                try:
                    service = KinopoiskService()
                    movie = service.import_from_url(url)
                    self.message_user(
                        request, 
                        format_html('Фильм "<b>{}</b>" успешно импортирован!', movie.title), 
                        level=messages.SUCCESS
                    )
                    # Не редиректим, а показываем превью
                    context['movie'] = movie
                    context['kinopoisk_url'] = url
                except KinopoiskImportError as e:
                    self.message_user(request, f"Ошибка импорта: {str(e)}", level=messages.ERROR)
                    context['kinopoisk_url'] = url
                except Exception as e:
                    self.message_user(request, f"Неизвестная ошибка: {str(e)}", level=messages.ERROR)
                    context['kinopoisk_url'] = url
        
        return render(request, 'admin/movies/movie/import_kinopoisk.html', context)
    
    fieldsets = (
        (None, {
            'fields': ('title', 'name_original', 'type', 'kinopoisk_id', 'imdb_id')
        }),
        ('Описание', {
            'fields': ('slogan', 'overview', 'countries', 'genres')
        }),
        ('Характеристики', {
            'fields': ('film_length', 'age_rating', 'rating', 'vote_count', 'release_date'),
        }),
        ('Постер', {
            'fields': ('poster_image', 'poster_path', 'poster_preview_large'),
        }),
        ('Фон', {
            'fields': ('backdrop_image', 'backdrop_path', 'backdrop_preview_large'),
        }),
    )


from solo.admin import SingletonModelAdmin

@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonModelAdmin):
    """Админка для настроек сайта"""
    list_display = ['__str__', 'token_status']
    
    def token_status(self, obj):
        if obj.kinopoisk_api_token:
            return "✓ Настроен"
        return "✗ Не настроен"
    token_status.short_description = "Kinopoisk API"
