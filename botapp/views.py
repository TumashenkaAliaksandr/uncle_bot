from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now

from botapp.models import Album, Track, Countdown


def index(request):

    album = Album.objects.prefetch_related('tracks').first()
    return render(request, 'index.html', {'album': album})


def player(request, album_id=None, track_id=None):
    albums = Album.objects.all()
    countdown = Countdown.objects.first()
    if track_id:
        track = get_object_or_404(Track, id=track_id)
    else:
        album = get_object_or_404(Album, id=album_id) if album_id else albums.first()
        track = album.tracks.first() if album else None

    tracks = Track.objects.all()
    return render(request, 'player.html', {
        'albums': albums,
        'tracks': tracks,
        'current_track': track,
        'countdown': countdown,
    })
