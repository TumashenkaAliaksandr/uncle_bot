from .models import Track

def current_track_processor(request):
    # Можно настроить, например, чтобы всегда брать первый трек или по id из сессии/куки, если есть
    track = Track.objects.filter(is_tonight=True).first()
    return {
        'current_track': track,
    }
