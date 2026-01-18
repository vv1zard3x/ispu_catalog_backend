from django.db import models
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO
import os


def compress_image(image_field, max_size_mb=5, max_resolution=2048):
    """
    Сжимает изображение до указанного размера и разрешения.
    max_size_mb: максимальный размер файла в МБ
    max_resolution: максимальное разрешение (ширина или высота)
    """
    if not image_field:
        return image_field
    
    img = Image.open(image_field)
    
    # Конвертируем в RGB если нужно (для JPEG)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    
    # Уменьшаем размер если превышает max_resolution
    if img.width > max_resolution or img.height > max_resolution:
        ratio = min(max_resolution / img.width, max_resolution / img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    # Сжимаем до нужного размера файла
    max_size_bytes = max_size_mb * 1024 * 1024
    quality = 95
    
    while quality > 10:
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        size = buffer.tell()
        
        if size <= max_size_bytes:
            break
        quality -= 5
    
    buffer.seek(0)
    
    # Меняем расширение на .jpg
    name = os.path.splitext(image_field.name)[0] + '.jpg'
    
    return ContentFile(buffer.read(), name=name)


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
    profile_image = models.ImageField(
        upload_to='actors/', 
        blank=True, 
        null=True, 
        verbose_name="Фото (загрузка)"
    )
    profile_path = models.CharField(
        max_length=500, 
        blank=True, 
        null=True, 
        verbose_name="Фото (URL или путь)"
    )

    class Meta:
        verbose_name = "Актёр"
        verbose_name_plural = "Актёры"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Сжимаем изображение при сохранении
        if self.profile_image:
            self.profile_image = compress_image(self.profile_image)
        super().save(*args, **kwargs)

    def get_profile_url(self):
        """Возвращает URL фото: загруженное или указанный путь"""
        if self.profile_image:
            return self.profile_image.url
        return self.profile_path


class Movie(models.Model):
    """Фильм"""
    title = models.CharField(max_length=255, verbose_name="Название")
    overview = models.TextField(verbose_name="Описание")
    poster_image = models.ImageField(
        upload_to='posters/', 
        blank=True, 
        null=True, 
        verbose_name="Постер (загрузка)"
    )
    poster_path = models.CharField(
        max_length=500, 
        blank=True, 
        null=True, 
        verbose_name="Постер (URL или путь)"
    )
    backdrop_image = models.ImageField(
        upload_to='backdrops/', 
        blank=True, 
        null=True, 
        verbose_name="Фон (загрузка)"
    )
    backdrop_path = models.CharField(
        max_length=500, 
        blank=True, 
        null=True, 
        verbose_name="Фон (URL или путь)"
    )
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

    def save(self, *args, **kwargs):
        # Сжимаем изображения при сохранении
        if self.poster_image:
            self.poster_image = compress_image(self.poster_image)
        if self.backdrop_image:
            self.backdrop_image = compress_image(self.backdrop_image)
        super().save(*args, **kwargs)

    def get_poster_url(self):
        """Возвращает URL постера: загруженное или указанный путь"""
        if self.poster_image:
            return self.poster_image.url
        return self.poster_path

    def get_backdrop_url(self):
        """Возвращает URL фона: загруженное или указанный путь"""
        if self.backdrop_image:
            return self.backdrop_image.url
        return self.backdrop_path


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


class SiteSettings(models.Model):
    """Настройки сайта (singleton)"""
    kinopoisk_api_token = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Kinopoisk API токен",
        help_text="Получите токен на https://kinopoiskapiunofficial.tech"
    )

    class Meta:
        verbose_name = "Настройки"
        verbose_name_plural = "Настройки"

    def __str__(self):
        return "Настройки сайта"

    def save(self, *args, **kwargs):
        # Singleton pattern - всегда используем id=1
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Получает или создаёт единственный экземпляр настроек"""
        settings, _ = cls.objects.get_or_create(pk=1)
        return settings

    @classmethod
    def get_kinopoisk_token(cls):
        """Возвращает токен Kinopoisk API"""
        settings = cls.get_settings()
        return settings.kinopoisk_api_token

