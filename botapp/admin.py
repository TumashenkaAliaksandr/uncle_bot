from django.contrib import admin
from django.utils.html import format_html
from urllib.parse import quote

from botapp.models import Track, Album, News, SongInfo, Countdown


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
    list_display = ("title", "album", "audio_player", "is_main", "is_popular", "is_movies", "is_tomorrow")
    search_fields = ("title",)
    list_filter = ("album", "is_popular", "is_movies", "is_tomorrow")
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



@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title_news', 'formatted_date', 'track')
    search_fields = ('title_news', 'description')
    list_filter = ('date',)
    readonly_fields = ('date',)

    fieldsets = (
        (None, {
            'fields': ('title_news', 'description', 'photo', 'audio', 'date', 'track')
        }),
    )

    def formatted_date(self, obj):
        return obj.date.strftime('%d.%m.%Y %H:%M')
    formatted_date.short_description = 'Дата публикации'
    formatted_date.admin_order_field = 'date'

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.photo.url)
        return ""
    photo_preview.short_description = 'Фото превью'


@admin.register(SongInfo)
class SongInfoAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)


@admin.register(Countdown)
class CountdownAdmin(admin.ModelAdmin):
    list_display = ('name', 'end_time',)
