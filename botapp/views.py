from django.shortcuts import render

from botapp.models import Album


def index(request):

    album = Album.objects.prefetch_related('tracks').first()
    return render(request, 'index.html', {'album': album})
