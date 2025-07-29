from django.db import models
from django.conf import settings
from django.utils import timezone


class Device(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tracked_devices')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_name = models.CharField(max_length=255, blank=True, null=True)  # User-Agent
    refresh_token_jti = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    last_seen = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-last_seen']

    def __str__(self):
        return f"{self.user} - {self.device_name} ({self.ip_address})"
