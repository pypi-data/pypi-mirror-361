from django.urls import path
from .views import UserDeviceListView, DeviceLogoutView

urlpatterns = [
    path('devices/', UserDeviceListView.as_view(), name='device_tracker_list'),
    path('devices/<int:pk>/logout/', DeviceLogoutView.as_view(), name='device_tracker_logout'),
]