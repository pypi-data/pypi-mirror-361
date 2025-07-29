from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Device
from rest_framework import status


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