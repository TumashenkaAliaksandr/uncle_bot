from django.contrib import admin
from django.utils.html import format_html
from urllib.parse import quote
from .models import Album, Track

class TrackInline(admin.TabularInline):
    model = Track
    extra = 1
    readonly_fields = ("audio_player",)
    fields = ("title", "description", "cover", "audio_file", "audio_player")

    def audio_player(self, obj):
        if obj.audio_file:
            url = quote(obj.audio_file.url, safe="/:%")
            return format_html(
                '<audio controls style="width: 300px;">'
                '<source src="{}" type="audio/mpeg">'
                'Ваш браузер не поддерживает аудио.'
                '</audio>',
                url
            )
        return "(Аудиофайл не загружен)"
    audio_player.short_description = "Прослушать трек"

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ("name", "release_date", "authors")
    search_fields = ("name", "authors")
    inlines = [TrackInline]

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ("title", "album", "audio_player")
    search_fields = ("title",)
    list_filter = ("album",)
    readonly_fields = ("audio_player",)

    def audio_player(self, obj):
        if obj.audio_file:
            url = quote(obj.audio_file.url, safe="/:%")
            return format_html(
                '<audio controls style="width: 300px;">'
                '<source src="{}" type="audio/mpeg">'
                'Ваш браузер не поддерживает аудио.'
                '</audio>',
                url
            )
        return "(Аудиофайл не загружен)"
    audio_player.short_description = "Прослушать трек"
