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
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='tracks', verbose_name="Альбом")
    title = models.CharField(max_length=255, verbose_name="Название трека")
    description = models.TextField(blank=True, verbose_name="Описание")
    cover = models.ImageField(upload_to='tracks/covers/', blank=True, null=True, verbose_name="Обложка")
    audio_file = models.FileField(upload_to='tracks/audio/', blank=True, null=True, verbose_name="Аудиофайл (MP3)")

    def __str__(self):
        return self.title
