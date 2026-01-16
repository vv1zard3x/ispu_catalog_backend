# Movie Catalog Backend

Django REST API бэкенд для мобильного приложения кинокаталога.

## Стек

- Django 6.0
- Django REST Framework
- django-jazzmin (админка)
- django-filter
- django-cors-headers

## Установка

```bash
# Создать виртуальное окружение
python -m venv .venv

# Активировать
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Установить зависимости
pip install Django djangorestframework django-filter django-cors-headers django-jazzmin

# Миграции
python manage.py migrate

# Заполнить тестовыми данными
python manage.py populate_movies

# Создать админа
python manage.py createsuperuser

# Запустить сервер
python manage.py runserver
```

## API Endpoints

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/movies/` | Список фильмов |
| GET | `/api/movies/{id}/` | Детали фильма |
| GET | `/api/movies/{id}/cast/` | Актёрский состав |
| GET | `/api/movies/search/?q=` | Поиск |
| GET | `/api/genres/` | Жанры |

## Фильтры

- `?page=1` — пагинация
- `?genre=1` — фильтр по жанру
- `?ordering=-rating` — сортировка

## Админка

http://127.0.0.1:8000/admin/
