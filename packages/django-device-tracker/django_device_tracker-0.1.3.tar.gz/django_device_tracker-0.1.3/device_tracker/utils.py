from .models import Device
from django.utils import timezone


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def track_device(request, user, refresh_token=None):
    ip = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
    jti = refresh_token.get('jti') if refresh_token else None

    Device.objects.create(
        user=user,
        ip_address=ip,
        device_name=user_agent,
        refresh_token_jti=jti,
        last_seen=timezone.now(),
        is_active=True
    )
