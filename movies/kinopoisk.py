"""
Сервис для импорта фильмов с Кинопоиска
Использует неофициальный API: https://kinopoiskapiunofficial.tech
Теперь поддерживает асинхронные запросы для ускорения работы.
"""
import re
import asyncio
import httpx
from datetime import datetime
from asgiref.sync import async_to_sync
from django.conf import settings
from django.core.files.base import ContentFile
from .models import Genre, Actor, Movie, MovieCast, SiteSettings, Country


class KinopoiskImportError(Exception):
    """Ошибка при импорте с Кинопоиска"""
    pass


class KinopoiskService:
    """Сервис для работы с API Кинопоиска"""
    
    BASE_URL = "https://kinopoiskapiunofficial.tech/api/v2.2"
    
    def __init__(self):
        # Сначала пробуем получить токен из БД (настройки в админке)
        self.api_token = SiteSettings.get_kinopoisk_token()
        
        # Fallback на settings.py
        if not self.api_token:
            self.api_token = getattr(settings, 'KINOPOISK_API_TOKEN', None)
        
        if not self.api_token:
            raise KinopoiskImportError(
                "KINOPOISK_API_TOKEN не настроен. "
                "Перейдите в Админка → Настройки и укажите токен."
            )
    
    def _get_headers(self):
        """Возвращает заголовки для API запросов"""
        return {
            "X-API-KEY": self.api_token,
            "Content-Type": "application/json",
        }
    
    @staticmethod
    def extract_id_from_url(url: str) -> int:
        """Извлекает ID фильма из URL Кинопоиска"""
        patterns = [
            r'kinopoisk\.ru/(?:film|series)/(\d+)',
            r'kinopoisk\.ru/(?:film|series)/(\d+)/',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return int(match.group(1))
        raise KinopoiskImportError(f"Не удалось извлечь ID из URL: {url}")
    
    async def fetch_film_data(self, client: httpx.AsyncClient, film_id: int) -> dict:
        """Асинхронно получает данные о фильме"""
        url = f"{self.BASE_URL}/films/{film_id}"
        response = await client.get(url, headers=self._get_headers(), timeout=15)
        
        if response.status_code == 401:
            raise KinopoiskImportError("Неверный API токен.")
        elif response.status_code == 404:
            raise KinopoiskImportError(f"Фильм с ID {film_id} не найден.")
        elif response.status_code != 200:
            raise KinopoiskImportError(f"API вернул ошибку: {response.status_code}")
            
        return response.json()
    
    async def fetch_film_staff(self, client: httpx.AsyncClient, film_id: int) -> list:
        """Асинхронно получает актёрский состав"""
        url = f"{self.BASE_URL.replace('v2.2', 'v1')}/staff"
        params = {"filmId": film_id}
        try:
            response = await client.get(url, headers=self._get_headers(), params=params, timeout=15)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return []

    def _get_or_create_genres(self, genres_data: list) -> list:
        """Создаёт или получает жанры"""
        genres = []
        for genre_info in genres_data:
            genre_name = genre_info.get('genre', '').strip()
            if genre_name:
                genre, _ = Genre.objects.get_or_create(name=genre_name.capitalize())
                genres.append(genre)
        return genres

    def _get_or_create_countries(self, countries_data: list) -> list:
        """Создаёт или получает страны"""
        countries = []
        for country_info in countries_data:
            name = country_info.get('country', '').strip()
            if name:
                country, _ = Country.objects.get_or_create(name=name)
                countries.append(country)
        return countries
    
    def _get_or_create_actor(self, actor_data: dict) -> Actor | None:
        """Создаёт или получает актёра"""
        kinopoisk_id = actor_data.get('staffId')  # Используем ID если есть
        name = actor_data.get('nameRu') or actor_data.get('nameEn')
        
        if not name and not kinopoisk_id:
            return None

        # Пытаемся найти по ID
        actor = None
        if kinopoisk_id:
            actor = Actor.objects.filter(kinopoisk_id=kinopoisk_id).first()
        
        # Если не нашли по ID, ищем по имени
        if not actor and name:
            actor = Actor.objects.filter(name__iexact=name.strip()).first()
            # Если нашли по имени, проставим ID
            if actor and kinopoisk_id and not actor.kinopoisk_id:
                actor.kinopoisk_id = kinopoisk_id
                actor.save()

        # Если так и не нашли - создаём
        if not actor:
            poster_url = actor_data.get('posterUrl')
            actor = Actor.objects.create(
                name=name.strip() if name else "Неизвестный актёр",
                kinopoisk_id=kinopoisk_id,
                profile_path=poster_url
            )
        else:
            # Обновляем фото если нет
            if not actor.profile_path and not actor.profile_image:
                poster_url = actor_data.get('posterUrl')
                if poster_url:
                    actor.profile_path = poster_url
                    actor.save()
                    
        return actor

    def _parse_age_limit(self, age_str: str | None) -> int | None:
        if not age_str:
            return None
        match = re.search(r'\d+', age_str)
        if match:
            return int(match.group())
        return None

    def parse_date(self, film_data: dict) -> datetime.date:
        year = film_data.get('year')
        try:
            premiere = film_data.get('premiereWorld') or film_data.get('premiereRu')
            if premiere:
                return datetime.strptime(premiere, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            pass
        
        if year:
            return datetime(int(year), 1, 1).date()
        return datetime.now().date()

    async def _import_from_url_async(self, url: str) -> Movie:
        """Асинхронная реализация импорта"""
        film_id = self.extract_id_from_url(url)
        
        async with httpx.AsyncClient() as client:
            # Параллельный запуск запросов
            film_task = self.fetch_film_data(client, film_id)
            staff_task = self.fetch_film_staff(client, film_id)
            
            film_data, staff_data = await asyncio.gather(film_task, staff_task)

        # Обработка данных (синхронная часть, работа с БД)
        return await async_to_sync(self._save_movie_data)(film_id, film_data, staff_data)

    async def _save_movie_data(self, film_id: int, film_data: dict, staff_data: list) -> Movie:
        """Сохранение данных в БД (вызывается из асинхронной функции)"""
        # Эта функция должна быть обычной синхронной, но async_to_sync ждет awaitable?
        # Нет, async_to_sync превращает async в sync.
        # Внутри async функции нельзя вызывать Django ORM без sync_to_async_adapter, или просто вынести в sync функцию.
        # Лучше я сделаю этот метод синхронным и буду вызывать его, но Python async function can't just call sync code directly without blocking loop?
        # В данном случае, мы запускаем loop через async_to_sync в public методе.
        # Значит, внутри _import_from_url_async (которая бежит в loop) я не могу делать блокирующие вызовы ORM напрямую безопасно.
        # Поэтому лучше всю логику сохранения вынести в отдельный синхронный метод и вызвать его через sync_to_async? 
        # Или, раз уж мы используем async_to_sync на верхнем уровне, то loop блокируется? 
        # Нет, async_to_sync запускает loop.
        # Проще всего: получить данные асинхронно, а сохранять синхронно ПОСЛЕ завершения async блока.
        return self._process_and_save(film_id, film_data, staff_data)

    def _process_and_save(self, film_id: int, film_data: dict, staff_data: list) -> Movie:
        """Синхронная обработка и сохранение"""
        
        title = film_data.get('nameRu') or film_data.get('nameOriginal') or film_data.get('nameEn')
        if not title:
            raise KinopoiskImportError("Не удалось получить название фильма")

        release_date = self.parse_date(film_data)
        
        # Подготовка полей
        defaults = {
            'overview': film_data.get('description') or film_data.get('shortDescription') or '',
            'rating': float(film_data.get('ratingKinopoisk') or film_data.get('ratingImdb') or 0.0),
            'vote_count': int(film_data.get('ratingKinopoiskVoteCount') or film_data.get('ratingImdbVoteCount') or 0),
            'poster_path': film_data.get('posterUrl'),
            'backdrop_path': film_data.get('coverUrl'),
            'imdb_id': film_data.get('imdbId'),
            'name_original': film_data.get('nameOriginal'),
            'slogan': film_data.get('slogan'),
            'film_length': film_data.get('filmLength'),
            'age_rating': self._parse_age_limit(film_data.get('ratingAgeLimits')),
            'type': film_data.get('type'),
        }

        # Логика поиска дубликатов:
        # 1. По kinopoisk_id
        movie = Movie.objects.filter(kinopoisk_id=film_id).first()
        
        # 2. По названию и году (если нет kinopoisk_id)
        if not movie:
            movie = Movie.objects.filter(title__iexact=title, release_date__year=release_date.year).first()
            if movie:
                # Нашли дубль -> привязываем ID
                movie.kinopoisk_id = film_id
        
        if movie:
            # Обновляем
            for key, value in defaults.items():
                setattr(movie, key, value)
            movie.save()
        else:
            # Создаём
            defaults['kinopoisk_id'] = film_id
            defaults['title'] = title
            defaults['release_date'] = release_date
            movie = Movie.objects.create(**defaults)

        # Связи M2M
        genres = self._get_or_create_genres(film_data.get('genres', []))
        movie.genres.set(genres)
        
        countries = self._get_or_create_countries(film_data.get('countries', []))
        movie.countries.set(countries)

        # Актёры
        actors_data = [s for s in staff_data if s.get('professionKey') == 'ACTOR'][:20]
        
        # Обновляем каст полностью
        MovieCast.objects.filter(movie=movie).delete()
        
        movie_casts = []
        for order, actor_data in enumerate(actors_data):
            actor = self._get_or_create_actor(actor_data)
            if actor:
                character = actor_data.get('description') or 'Неизвестная роль'
                movie_casts.append(MovieCast(
                    movie=movie,
                    actor=actor,
                    character=character[:255],
                    order=order
                ))
        
        if movie_casts:
            MovieCast.objects.bulk_create(movie_casts)

        return movie

    def import_from_url(self, url: str) -> Movie:
        """
        Публичный метод импорта (синхронная обертка).
        Запускает event loop для выполнения асинхронных запросов.
        """
        film_id = self.extract_id_from_url(url)
        
        # 1. Получаем данные асинхронно
        async def fetch_all():
            async with httpx.AsyncClient() as client:
                film_task = self.fetch_film_data(client, film_id)
                staff_task = self.fetch_film_staff(client, film_id)
                return await asyncio.gather(film_task, staff_task)

        try:
           film_data, staff_data = async_to_sync(fetch_all)()
        except Exception as e:
            # Если async_to_sync не сработает (например внутри другого loop),
            # можно попробовать asyncio.run, но async_to_sync надежнее для Django.
             raise KinopoiskImportError(f"Ошибка получения данных: {e}")

        # 2. Сохраняем синхронно (чтобы не блокировать подключение к БД в async контексте без нужды)
        return self._process_and_save(film_id, film_data, staff_data)
