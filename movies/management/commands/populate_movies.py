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
        # База URL для статики
        POSTER_BASE = '/static/movies/posters/'
        BACKDROP_BASE = '/static/movies/backdrops/'
        ACTOR_BASE = '/static/movies/actors/'

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

        # Создаём актёров с фото
        actors_data = [
            ('Леонардо ДиКаприо', f'{ACTOR_BASE}dicaprio.png'),
            ('Кристиан Бэйл', f'{ACTOR_BASE}bale.png'),
            ('Мэттью МакКонахи', f'{ACTOR_BASE}mcconaughey.png'),
            ('Киану Ривз', f'{ACTOR_BASE}reeves.png'),
            ('Рассел Кроу', f'{ACTOR_BASE}crowe.png'),
            ('Том Хэнкс', f'{ACTOR_BASE}hanks.png'),
            ('Брэд Питт', f'{ACTOR_BASE}pitt.png'),
            ('Морган Фриман', f'{ACTOR_BASE}freeman.png'),
            ('Энн Хэтэуэй', f'{ACTOR_BASE}hathaway.png'),
            ('Хоакин Феникс', f'{ACTOR_BASE}phoenix.png'),
        ]

        actors = {}
        for name, profile_path in actors_data:
            actor, created = Actor.objects.get_or_create(
                name=name,
                defaults={'profile_path': profile_path}
            )
            if not created and actor.profile_path != profile_path:
                actor.profile_path = profile_path
                actor.save()
            actors[name] = actor
            self.stdout.write(f"Актёр: {name}")

        # Создаём фильмы
        movies_data = [
            {
                'title': 'Начало',
                'overview': 'Кобб — талантливый вор, лучший в опасном искусстве извлечения: кражи ценных секретов из глубин подсознания во время сна.',
                'poster_path': f'{POSTER_BASE}inception.png',
                'backdrop_path': f'{BACKDROP_BASE}inception.png',
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
                'backdrop_path': None,
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
                'backdrop_path': None,
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
                'backdrop_path': None,
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
                'backdrop_path': None,
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
                'backdrop_path': None,
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
                'backdrop_path': None,
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
                'backdrop_path': None,
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
                'backdrop_path': None,
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
                'backdrop_path': None,
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
                    'backdrop_path': movie_data['backdrop_path'],
                    'rating': movie_data['rating'],
                    'release_date': movie_data['release_date'],
                    'vote_count': movie_data['vote_count'],
                }
            )
            
            # Обновляем пути если фильм уже существует
            if not created:
                movie.poster_path = movie_data['poster_path']
                movie.backdrop_path = movie_data['backdrop_path']
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
