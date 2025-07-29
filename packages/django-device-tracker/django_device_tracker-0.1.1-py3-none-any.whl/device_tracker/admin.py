from django.contrib import admin
from .models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_name', 'ip_address', 'last_seen', 'is_active')
    search_fields = ('user__phone', 'ip_address', 'device_name')
