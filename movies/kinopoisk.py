"""
Сервис для импорта фильмов с Кинопоиска
Использует неофициальный API: https://kinopoiskapiunofficial.tech
"""
import re
import os
import requests
from datetime import datetime
from django.conf import settings
from django.core.files.base import ContentFile
from .models import Genre, Actor, Movie, MovieCast


class KinopoiskImportError(Exception):
    """Ошибка при импорте с Кинопоиска"""
    pass


class KinopoiskService:
    """Сервис для работы с API Кинопоиска"""
    
    BASE_URL = "https://kinopoiskapiunofficial.tech/api/v2.2"
    
    def __init__(self):
        self.api_token = getattr(settings, 'KINOPOISK_API_TOKEN', None) or os.environ.get('KINOPOISK_API_TOKEN')
        if not self.api_token:
            raise KinopoiskImportError(
                "KINOPOISK_API_TOKEN не настроен. "
                "Получите токен на https://kinopoiskapiunofficial.tech и добавьте в .env"
            )
    
    def _get_headers(self):
        """Возвращает заголовки для API запросов"""
        return {
            "X-API-KEY": self.api_token,
            "Content-Type": "application/json",
        }
    
    @staticmethod
    def extract_id_from_url(url: str) -> int:
        """
        Извлекает ID фильма из URL Кинопоиска
        
        Поддерживаемые форматы:
        - https://www.kinopoisk.ru/film/435/
        - https://www.kinopoisk.ru/series/6058297/
        - https://kinopoisk.ru/film/435
        """
        # Паттерн для извлечения числового ID
        patterns = [
            r'kinopoisk\.ru/(?:film|series)/(\d+)',
            r'kinopoisk\.ru/(?:film|series)/(\d+)/',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return int(match.group(1))
        
        raise KinopoiskImportError(
            f"Не удалось извлечь ID из URL: {url}. "
            "Ожидается формат: https://www.kinopoisk.ru/film/435/ или https://www.kinopoisk.ru/series/6058297/"
        )
    
    def get_film_data(self, film_id: int) -> dict:
        """Получает данные о фильме по ID"""
        url = f"{self.BASE_URL}/films/{film_id}"
        
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=10)
        except requests.RequestException as e:
            raise KinopoiskImportError(f"Ошибка при запросе к API: {e}")
        
        if response.status_code == 401:
            raise KinopoiskImportError("Неверный API токен. Проверьте KINOPOISK_API_TOKEN")
        elif response.status_code == 404:
            raise KinopoiskImportError(f"Фильм с ID {film_id} не найден на Кинопоиске")
        elif response.status_code != 200:
            raise KinopoiskImportError(f"API вернул ошибку: {response.status_code}")
        
        return response.json()
    
    def get_film_staff(self, film_id: int) -> list:
        """Получает актёрский состав фильма"""
        url = f"{self.BASE_URL.replace('v2.2', 'v1')}/staff"
        params = {"filmId": film_id}
        
        try:
            response = requests.get(url, headers=self._get_headers(), params=params, timeout=10)
        except requests.RequestException as e:
            # Не критичная ошибка - фильм можно создать без актёров
            return []
        
        if response.status_code != 200:
            return []
        
        return response.json()
    
    def _download_image(self, url: str) -> ContentFile | None:
        """Скачивает изображение по URL"""
        if not url:
            return None
        
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                # Извлекаем имя файла из URL
                filename = url.split('/')[-1]
                if not filename or '.' not in filename:
                    filename = "image.jpg"
                return ContentFile(response.content, name=filename)
        except requests.RequestException:
            pass
        
        return None
    
    def _get_or_create_genres(self, genres_data: list) -> list:
        """Создаёт или получает жанры"""
        genres = []
        for genre_info in genres_data:
            genre_name = genre_info.get('genre', '').strip()
            if genre_name:
                # Первая буква заглавная
                genre_name = genre_name.capitalize()
                genre, _ = Genre.objects.get_or_create(name=genre_name)
                genres.append(genre)
        return genres
    
    def _get_or_create_actor(self, actor_data: dict) -> Actor | None:
        """Создаёт или получает актёра"""
        name = actor_data.get('nameRu') or actor_data.get('nameEn')
        if not name:
            return None
        
        actor, created = Actor.objects.get_or_create(
            name=name.strip(),
            defaults={'profile_path': actor_data.get('posterUrl')}
        )
        
        # Если актёр уже существует, но нет фото — обновляем
        if not created and not actor.profile_path and not actor.profile_image:
            poster_url = actor_data.get('posterUrl')
            if poster_url:
                actor.profile_path = poster_url
                actor.save()
        
        return actor
    
    def import_from_url(self, url: str) -> Movie:
        """
        Импортирует фильм из URL Кинопоиска
        
        Args:
            url: URL фильма на Кинопоиске
            
        Returns:
            Созданный или обновлённый объект Movie
        """
        # Извлекаем ID
        film_id = self.extract_id_from_url(url)
        
        # Получаем данные о фильме
        film_data = self.get_film_data(film_id)
        
        # Подготавливаем данные
        title = film_data.get('nameRu') or film_data.get('nameOriginal') or film_data.get('nameEn')
        if not title:
            raise KinopoiskImportError("Не удалось получить название фильма")
        
        overview = film_data.get('description') or film_data.get('shortDescription') or ''
        
        # Дата выхода
        release_date = None
        if film_data.get('year'):
            try:
                # Пробуем получить полную дату
                premiere_world = film_data.get('premiereWorld')
                premiere_ru = film_data.get('premiereRu')
                
                if premiere_world:
                    release_date = datetime.strptime(premiere_world, '%Y-%m-%d').date()
                elif premiere_ru:
                    release_date = datetime.strptime(premiere_ru, '%Y-%m-%d').date()
                else:
                    # Используем только год
                    release_date = datetime(int(film_data['year']), 1, 1).date()
            except (ValueError, TypeError):
                release_date = datetime(int(film_data['year']), 1, 1).date()
        else:
            release_date = datetime.now().date()
        
        # Рейтинг
        rating = film_data.get('ratingKinopoisk') or film_data.get('ratingImdb') or 0.0
        if rating is None:
            rating = 0.0
        
        vote_count = film_data.get('ratingKinopoiskVoteCount') or film_data.get('ratingImdbVoteCount') or 0
        if vote_count is None:
            vote_count = 0
        
        # Создаём или обновляем фильм
        movie, created = Movie.objects.update_or_create(
            title=title,
            defaults={
                'overview': overview,
                'rating': float(rating),
                'release_date': release_date,
                'vote_count': int(vote_count),
                'poster_path': film_data.get('posterUrl'),
                'backdrop_path': film_data.get('coverUrl'),
            }
        )
        
        # Добавляем жанры
        genres = self._get_or_create_genres(film_data.get('genres', []))
        movie.genres.set(genres)
        
        # Получаем актёрский состав
        staff_data = self.get_film_staff(film_id)
        
        # Фильтруем только актёров
        actors_data = [s for s in staff_data if s.get('professionKey') == 'ACTOR'][:15]  # Берём первых 15
        
        # Удаляем старый актёрский состав если фильм обновляется
        if not created:
            MovieCast.objects.filter(movie=movie).delete()
        
        # Добавляем актёров
        for order, actor_data in enumerate(actors_data):
            actor = self._get_or_create_actor(actor_data)
            if actor:
                character = actor_data.get('description') or 'Неизвестная роль'
                MovieCast.objects.create(
                    movie=movie,
                    actor=actor,
                    character=character[:255],  # Ограничиваем длину
                    order=order
                )
        
        return movie


def import_movie_from_kinopoisk(url: str) -> Movie:
    """
    Удобная функция для импорта фильма
    
    Args:
        url: URL фильма на Кинопоиске
        
    Returns:
        Созданный объект Movie
    """
    service = KinopoiskService()
    return service.import_from_url(url)
