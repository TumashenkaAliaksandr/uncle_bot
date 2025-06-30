from django.db import models

class Album(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название альбома")
    description = models.TextField(blank=True, verbose_name="Описание")
    cover = models.ImageField(upload_to='albums/covers/', blank=True, null=True, verbose_name="Обложка")
    release_date = models.DateField(verbose_name="Дата выпуска")
    authors = models.CharField(max_length=255, verbose_name="Авторы")

    def __str__(self):
        return self.name

class Track(models.Model):
    album = models.ForeignKey('botapp.Album', on_delete=models.CASCADE, related_name='tracks', verbose_name="Альбом")
    title = models.CharField(max_length=255, verbose_name="Название трека")
    description = models.TextField(blank=True, verbose_name="Описание")
    cover = models.ImageField(upload_to='tracks/covers/', blank=True, null=True, verbose_name="Обложка")
    audio_file = models.FileField(upload_to='tracks/audio/', blank=True, null=True, verbose_name="Аудиофайл (MP3)")

    def __str__(self):
        return self.title


class News(models.Model):
    title_news = models.CharField(max_length=300, default='News')
    description = models.TextField(blank=True, verbose_name='Описание')
    photo = models.ImageField(upload_to='news/photos/', blank=True, null=True, verbose_name='Фото')
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
        verbose_name = 'Новости'
        verbose_name_plural = 'Новости'

    def __str__(self):
        return self.title_news
