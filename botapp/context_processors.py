from .models import Track, SocialNetwork


def current_track_processor(request):
    # Можно настроить, например, чтобы всегда брать первый трек или по id из сессии/куки, если есть
    track = Track.objects.filter(is_tonight=True).first()
    return {
        'current_track': track,
    }

def social_networks_context(request):
    social_networks = SocialNetwork.objects.all()
    return {'social_networks': social_networks}

