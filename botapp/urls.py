from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views


urlpatterns = [
    # path('', views.index, name='index'),
    path('', views.player, name='player'),
    path('album/<int:album_id>/', views.player, name='album_player'),
    path('track/<int:track_id>/', views.player, name='track_player'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
