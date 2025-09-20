from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now

from botapp.models import Album, Track, Countdown


def index(request):

    album = Album.objects.prefetch_related('tracks').first()
    return render(request, 'index.html', {'album': album})


def player(request, album_id=None, track_id=None):
    albums = Album.objects.all()
    countdown = Countdown.objects.first()

    # Получаем треки с is_main=True
    tracks = Track.objects.filter(is_main=True)

    # Если передан трек по id, выбираем его
    if track_id:
        current_track = get_object_or_404(tracks, id=track_id)
        album = current_track.album
    else:
        # Если передан album_id, пытаемся выбрать первый трек из этого альбома
        if album_id:
            album = get_object_or_404(Album, id=album_id)
            # Из всех треков фильтруем те что в кино и относятся к альбому
            tracks = tracks.filter(album=album)
        else:
            album = None

        current_track = tracks.first() if tracks.exists() else None

    return render(request, 'player.html', {
        'albums': albums,
        'album': album,
        'tracks': tracks,
        'current_track': current_track,
        'countdown': countdown,
    })

def music_movies(request, album_id=None, track_id=None):
    albums = Album.objects.all()
    countdown = Countdown.objects.first()

    # Получаем треки с is_movies=True
    tracks = Track.objects.filter(is_movies=True)

    # Если передан трек по id, выбираем его
    if track_id:
        current_track = get_object_or_404(tracks, id=track_id)
        album = current_track.album
    else:
        # Если передан album_id, пытаемся выбрать первый трек из этого альбома
        if album_id:
            album = get_object_or_404(Album, id=album_id)
            # Из всех треков фильтруем те что в кино и относятся к альбому
            tracks = tracks.filter(album=album)
        else:
            album = None

        current_track = tracks.first() if tracks.exists() else None

    return render(request, 'music_movies.html', {
        'albums': albums,
        'album': album,
        'tracks': tracks,
        'current_track': current_track,
        'countdown': countdown,
    })


def videos(request, album_id=None, track_id=None):
    albums = Album.objects.all()
    countdown = Countdown.objects.first()

    # Получаем треки с is_movies=True
    tracks = Track.objects.filter(is_movies=True)

    # Если передан трек по id, выбираем его
    if track_id:
        current_track = get_object_or_404(tracks, id=track_id)
        album = current_track.album
    else:
        # Если передан album_id, пытаемся выбрать первый трек из этого альбома
        if album_id:
            album = get_object_or_404(Album, id=album_id)
            # Из всех треков фильтруем те что в кино и относятся к альбому
            tracks = tracks.filter(album=album)
        else:
            album = None

        current_track = tracks.first() if tracks.exists() else None

    return render(request, 'video.html', {
        'albums': albums,
        'album': album,
        'tracks': tracks,
        'current_track': current_track,
        'countdown': countdown,
    })

