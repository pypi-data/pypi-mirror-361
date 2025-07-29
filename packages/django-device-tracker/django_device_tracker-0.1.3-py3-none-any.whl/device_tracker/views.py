from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Device
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken


class UserDeviceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        devices = Device.objects.filter(user=request.user)
        data = [
            {
                'id': d.id,
                'device_name': d.device_name,
                'ip_address': d.ip_address,
                'refresh_token_jti': d.refresh_token_jti,
                'last_seen': d.last_seen,
                'created_at': d.created_at,
                'is_active': d.is_active
            }
            for d in devices
        ]
        return Response(data, status=status.HTTP_200_OK)


class DeviceLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        device = get_object_or_404(Device, pk=pk, user=request.user)

        if device.refresh_token_jti:
            try:
                token = OutstandingToken.objects.get(jti=device.refresh_token_jti)
                BlacklistedToken.objects.get_or_create(token=token)
            except OutstandingToken.DoesNotExist:
                pass  # توکن منقضی شده یا حذف شده

        device.is_active = False
        device.save()

        return Response({'detail': 'Device logged out'}, status=status.HTTP_200_OK)
