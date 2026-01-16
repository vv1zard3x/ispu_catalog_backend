from django.db import models


class Genre(models.Model):
    """Жанр фильма"""
    name = models.CharField(max_length=100, verbose_name="Название")

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ['name']

    def __str__(self):
        return self.name


class Actor(models.Model):
    """Актёр"""
    name = models.CharField(max_length=255, verbose_name="Имя")
    profile_path = models.URLField(blank=True, null=True, verbose_name="Фото")

    class Meta:
        verbose_name = "Актёр"
        verbose_name_plural = "Актёры"
        ordering = ['name']

    def __str__(self):
        return self.name


class Movie(models.Model):
    """Фильм"""
    title = models.CharField(max_length=255, verbose_name="Название")
    overview = models.TextField(verbose_name="Описание")
    poster_path = models.URLField(blank=True, null=True, verbose_name="Постер")
    backdrop_path = models.URLField(blank=True, null=True, verbose_name="Фон")
    rating = models.FloatField(default=0.0, verbose_name="Рейтинг")
    release_date = models.DateField(verbose_name="Дата выхода")
    vote_count = models.IntegerField(default=0, verbose_name="Количество голосов")
    genres = models.ManyToManyField(Genre, related_name='movies', verbose_name="Жанры")

    class Meta:
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"
        ordering = ['-release_date']

    def __str__(self):
        return self.title


class MovieCast(models.Model):
    """Актёрский состав фильма"""
    movie = models.ForeignKey(
        Movie, 
        on_delete=models.CASCADE, 
        related_name='cast',
        verbose_name="Фильм"
    )
    actor = models.ForeignKey(
        Actor, 
        on_delete=models.CASCADE,
        verbose_name="Актёр"
    )
    character = models.CharField(max_length=255, verbose_name="Персонаж")
    order = models.IntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Актёрский состав"
        ordering = ['order']

    def __str__(self):
        return f"{self.actor.name} как {self.character}"
