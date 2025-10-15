from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views


urlpatterns = [
    # path('', views.index, name='index'),
    path('', views.player, name='player'),
    path('album/<int:album_id>/', views.player, name='album_player'),
    path('track/<int:track_id>/', views.player, name='track_player'),
    path('music-movies/', views.music_movies, name='music_movies'),
    path('videos/', views.videos, name='videos'),
    path('jingle/', views.jingle, name='jingle'),
    path('top/', views.top, name='top'),
    path('new-the-day/', views.new_the_day, name='new_the_day'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
