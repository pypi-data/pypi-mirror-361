from django.urls import path
from .views import UserDeviceListView


urlpatterns = [
    path('devices/', UserDeviceListView.as_view(), name='device_tracker_list'),
]