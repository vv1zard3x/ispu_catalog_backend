FROM python:3.12-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .

# Собираем статику (если нужно)
RUN python manage.py collectstatic --noinput || true

# Открываем порт
EXPOSE 8000

# Запускаем Daphne
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "movie_backend.asgi:application"]
