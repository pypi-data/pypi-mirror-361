from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from .models import Device
from .utils import get_client_ip


class DeviceLastSeenMiddleware(MiddlewareMixin):
    """
    Middleware to automatically update the `last_seen` timestamp
    of the current device used by the authenticated user.

    This assumes that a device has been registered already via `track_device`,
    and that the current request contains a matching user and User-Agent.
    """

    def process_request(self, request):
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
            ip = get_client_ip(request)
            Device.objects.filter(
                user=user,
                device_name=user_agent,
                ip_address=ip,
                is_active=True
            ).update(last_seen=timezone.now())
