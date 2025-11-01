from typing import Any

from django.db import models

class Album(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название альбома")
    description = models.TextField(blank=True, verbose_name="Описание")
    cover = models.ImageField(upload_to='albums/covers/', blank=True, null=True, verbose_name="Обложка")
    release_date = models.DateField(verbose_name="Дата выпуска")
    authors = models.CharField(max_length=255, verbose_name="Авторы")

    class Meta:
        verbose_name = '💽 Альбом'
        verbose_name_plural = '💽 Альбомы'

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.tracks_movies = None

    def __str__(self):
        return self.name


class Track(models.Model):
    album = models.ForeignKey('botapp.Album', on_delete=models.CASCADE, related_name='tracks', verbose_name="Альбом")
    title = models.CharField(max_length=255, verbose_name="Название трека")
    description = models.TextField(blank=True, verbose_name="Описание")
    cover = models.ImageField(upload_to='tracks/covers/', blank=True, null=True, verbose_name="Обложка")
    audio_file = models.FileField(upload_to='tracks/audio/', blank=True, null=True, verbose_name="Аудиофайл (MP3)")
    is_main = models.BooleanField(default=True, verbose_name='На главную', blank=True)
    is_popular = models.BooleanField(verbose_name='Популярные', default=False, blank=True)
    is_movies = models.BooleanField(verbose_name='В Кино', default=False, blank=True)
    is_tomorrow = models.BooleanField(verbose_name='Завтра в эфире', default=False, blank=True)
    is_tonight = models.BooleanField(verbose_name='Сегодня в эфире', default=False, blank=True)

    class Meta:
        verbose_name = '🎼 Трек'
        verbose_name_plural = '🎼 Треки'

    def __str__(self):
        return self.title

class News(models.Model):
    title_news = models.CharField(max_length=300, default='News')
    description = models.TextField(blank=True, verbose_name='Описание')
    photo = models.ImageField(upload_to='news/photos/', blank=True, null=True, verbose_name='Фото')
    audio = models.FileField(upload_to='news/audio/', blank=True, null=True, verbose_name='Аудио')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    track = models.ForeignKey(
        'botapp.Track',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='news',
        verbose_name='Аудиотрек'
    )

    class Meta:
        verbose_name = '📰 Новость'
        verbose_name_plural = '📰 Новости'

    def __str__(self):
        return self.title_news


class SongInfo(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название песни")
    lyrics = models.TextField(verbose_name="Текст песни")
    chords = models.TextField(verbose_name="Аккорды песни", help_text="Введите аккорды в текстовом формате")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "🍓 Песня"
        verbose_name_plural = "🍓 Аккорды песен"


class Countdown(models.Model):  # Явно указать id
    end_time = models.DateTimeField("Конечное время", help_text="Дата и время окончания отсчёта")
    name = models.CharField(max_length=100, unique=True, verbose_name="Название счётчика", blank=True, null=True)

    def __str__(self):
        return f"{self.name or 'Отсчёт'} до {self.end_time}"


class Video(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название видео")
    description = models.TextField(verbose_name="Описание")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    video_file = models.FileField(upload_to='videos/', verbose_name="Видео файл")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "📹 Видео"
        verbose_name_plural = "📹 Видео"


class SocialNetwork(models.Model):
    name = models.CharField(max_length=50, unique=True)
    url = models.URLField(max_length=255)
    svg_icon = models.TextField(
        help_text="SVG код иконки соцсети. Например, <svg>...</svg>"
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Социальная сеть"
        verbose_name_plural = "Социальные сети"

    def __str__(self):
        return self.name
