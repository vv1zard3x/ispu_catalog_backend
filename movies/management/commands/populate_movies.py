"""
Management command для заполнения базы данных тестовыми фильмами
Запуск: python manage.py populate_movies
"""
from datetime import date
from django.core.management.base import BaseCommand
from movies.models import Genre, Actor, Movie, MovieCast


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми фильмами, жанрами и актёрами'

    def handle(self, *args, **options):
        # База URL для постеров (статика Django)
        POSTER_BASE = '/static/movies/posters/'

        # Создаём жанры
        genres_data = [
            'Боевик', 'Фантастика', 'Триллер', 'Драма', 'Приключения',
            'Криминал', 'Комедия', 'Мелодрама', 'Ужасы', 'Исторический'
        ]

        genres = {}
        for name in genres_data:
            genre, _ = Genre.objects.get_or_create(name=name)
            genres[name] = genre
            self.stdout.write(f"Жанр: {name}")

        # Создаём актёров
        actors_data = [
            'Леонардо ДиКаприо', 'Кристиан Бэйл', 'Мэттью МакКонахи', 
            'Киану Ривз', 'Рассел Кроу', 'Том Хэнкс', 'Брэд Питт', 
            'Морган Фриман', 'Энн Хэтэуэй', 'Хоакин Феникс'
        ]

        actors = {}
        for name in actors_data:
            actor, _ = Actor.objects.get_or_create(name=name)
            actors[name] = actor
            self.stdout.write(f"Актёр: {name}")

        # Создаём фильмы
        movies_data = [
            {
                'title': 'Начало',
                'overview': 'Кобб — талантливый вор, лучший в опасном искусстве извлечения: кражи ценных секретов из глубин подсознания во время сна.',
                'poster_path': f'{POSTER_BASE}inception.png',
                'rating': 8.8,
                'release_date': date(2010, 7, 16),
                'vote_count': 34521,
                'genres': ['Фантастика', 'Боевик', 'Триллер'],
                'cast': [('Леонардо ДиКаприо', 'Кобб', 0)]
            },
            {
                'title': 'Тёмный рыцарь',
                'overview': 'Бэтмен поднимает ставки в войне с криминалом. С помощью лейтенанта Гордона и прокурора Харви Дента он намерен очистить улицы Готэма.',
                'poster_path': f'{POSTER_BASE}dark_knight.png',
                'rating': 9.0,
                'release_date': date(2008, 7, 18),
                'vote_count': 30891,
                'genres': ['Боевик', 'Криминал', 'Драма'],
                'cast': [('Кристиан Бэйл', 'Брюс Уэйн / Бэтмен', 0), ('Морган Фриман', 'Люциус Фокс', 1)]
            },
            {
                'title': 'Интерстеллар',
                'overview': 'Когда засуха, пыльные бури и вымирание растений приводят человечество к продовольственному кризису, команда исследователей отправляется через червоточину.',
                'poster_path': f'{POSTER_BASE}interstellar.png',
                'rating': 8.7,
                'release_date': date(2014, 11, 7),
                'vote_count': 32456,
                'genres': ['Фантастика', 'Драма', 'Приключения'],
                'cast': [('Мэттью МакКонахи', 'Купер', 0), ('Энн Хэтэуэй', 'Амелия Бренд', 1)]
            },
            {
                'title': 'Матрица',
                'overview': 'Хакер Нео узнаёт, что его мир — виртуальная реальность, созданная машинами для порабощения людей. Ему предстоит стать избранным.',
                'poster_path': f'{POSTER_BASE}matrix.png',
                'rating': 8.7,
                'release_date': date(1999, 3, 31),
                'vote_count': 24567,
                'genres': ['Фантастика', 'Боевик'],
                'cast': [('Киану Ривз', 'Нео', 0)]
            },
            {
                'title': 'Гладиатор',
                'overview': 'Генерал Максимус, преданный императором, становится рабом и гладиатором. Его единственная цель — месть.',
                'poster_path': f'{POSTER_BASE}gladiator.png',
                'rating': 8.5,
                'release_date': date(2000, 5, 5),
                'vote_count': 16789,
                'genres': ['Боевик', 'Драма', 'Исторический'],
                'cast': [('Рассел Кроу', 'Максимус', 0), ('Хоакин Феникс', 'Коммод', 1)]
            },
            {
                'title': 'Форрест Гамп',
                'overview': 'Сидя на скамейке, Форрест Гамп рассказывает случайным встречным историю своей необыкновенной жизни.',
                'poster_path': f'{POSTER_BASE}forrest_gump.png',
                'rating': 8.8,
                'release_date': date(1994, 7, 6),
                'vote_count': 25678,
                'genres': ['Драма', 'Мелодрама', 'Комедия'],
                'cast': [('Том Хэнкс', 'Форрест Гамп', 0)]
            },
            {
                'title': 'Бойцовский клуб',
                'overview': 'Офисный работник страдает от бессонницы. Случайная встреча с продавцом мыла меняет его жизнь навсегда.',
                'poster_path': f'{POSTER_BASE}fight_club.png',
                'rating': 8.8,
                'release_date': date(1999, 10, 15),
                'vote_count': 27890,
                'genres': ['Драма', 'Триллер'],
                'cast': [('Брэд Питт', 'Тайлер Дёрден', 0)]
            },
            {
                'title': 'Джокер',
                'overview': 'Готэм, начало 1980-х. Комик Артур Флек живёт с больной матерью. Однажды он оказывается втянут в череду трагических событий.',
                'poster_path': f'{POSTER_BASE}joker.png',
                'rating': 8.4,
                'release_date': date(2019, 10, 4),
                'vote_count': 23456,
                'genres': ['Криминал', 'Драма', 'Триллер'],
                'cast': [('Хоакин Феникс', 'Артур Флек / Джокер', 0)]
            },
            {
                'title': 'Побег из Шоушенка',
                'overview': 'Бухгалтер Энди Дюфрейн обвинён в убийстве собственной жены и её любовника. Несмотря на невиновность, он приговорён к пожизненному заключению.',
                'poster_path': f'{POSTER_BASE}shawshank.png',
                'rating': 9.3,
                'release_date': date(1994, 9, 23),
                'vote_count': 25789,
                'genres': ['Драма', 'Криминал'],
                'cast': [('Том Хэнкс', 'Энди Дюфрейн', 0), ('Морган Фриман', 'Ред', 1)]
            },
            {
                'title': 'Леон',
                'overview': 'Профессиональный убийца Леон берёт под опеку 12-летнюю Матильду, семью которой убили коррумпированные полицейские.',
                'poster_path': f'{POSTER_BASE}leon.png',
                'rating': 8.5,
                'release_date': date(1994, 9, 14),
                'vote_count': 12345,
                'genres': ['Боевик', 'Криминал', 'Драма'],
                'cast': []
            },
        ]

        for movie_data in movies_data:
            movie, created = Movie.objects.get_or_create(
                title=movie_data['title'],
                defaults={
                    'overview': movie_data['overview'],
                    'poster_path': movie_data['poster_path'],
                    'rating': movie_data['rating'],
                    'release_date': movie_data['release_date'],
                    'vote_count': movie_data['vote_count'],
                }
            )
            
            # Обновляем poster_path если фильм уже существует
            if not created and movie.poster_path != movie_data['poster_path']:
                movie.poster_path = movie_data['poster_path']
                movie.save()
            
            for genre_name in movie_data['genres']:
                movie.genres.add(genres[genre_name])
            
            for actor_name, character, order in movie_data['cast']:
                MovieCast.objects.get_or_create(
                    movie=movie,
                    actor=actors[actor_name],
                    defaults={'character': character, 'order': order}
                )
            
            status = "создан" if created else "обновлён"
            self.stdout.write(f"Фильм: {movie.title} - {status}")

        self.stdout.write(self.style.SUCCESS(f"\n✅ База данных заполнена!"))
        self.stdout.write(f"Жанров: {Genre.objects.count()}")
        self.stdout.write(f"Актёров: {Actor.objects.count()}")
        self.stdout.write(f"Фильмов: {Movie.objects.count()}")
