"""
Messaging Views for Owls E-commerce Platform
============================================
"""

from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import (
    Notification, UserNotificationPreference, DeviceToken
)
from .serializers import (
    NotificationSerializer,
    NotificationListSerializer,
    NotificationPreferenceSerializer,
    RegisterDeviceSerializer,
    DeviceTokenSerializer,
    MarkNotificationsReadSerializer,
    NotificationCountSerializer
)


def get_or_create_preferences(user):
    """Get or create user's notification preferences."""
    prefs, _ = UserNotificationPreference.objects.get_or_create(user=user)
    return prefs


@extend_schema(tags=['Notifications'])
class NotificationListView(generics.ListAPIView):
    """
    List user's notifications.
    
    Supports filtering by:
    - type: Filter by notification type
    - unread: Show only unread notifications
    """
    
    serializer_class = NotificationListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Notification.objects.filter(user=self.request.user)
        
        # Filter by type
        notification_type = self.request.query_params.get('type')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        # Filter unread only
        unread = self.request.query_params.get('unread')
        if unread == 'true':
            queryset = queryset.filter(is_read=False)
        
        return queryset.order_by('-created_at')


@extend_schema(tags=['Notifications'])
class NotificationDetailView(generics.RetrieveAPIView):
    """Get notification detail."""
    
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Auto-mark as read when viewing
        instance.mark_as_read()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data
        })


@extend_schema(
    tags=['Notifications'],
    responses={200: NotificationCountSerializer}
)
class NotificationCountView(APIView):
    """Get notification counts."""
    
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)
        
        total = notifications.count()
        unread = notifications.filter(is_read=False).count()
        
        # Count by type
        by_type = {}
        type_counts = notifications.filter(is_read=False).values(
            'notification_type'
        ).annotate(count=Count('id'))
        
        for item in type_counts:
            by_type[item['notification_type']] = item['count']
        
        return Response({
            'success': True,
            'data': {
                'total': total,
                'unread': unread,
                'by_type': by_type
            }
        })


@extend_schema(
    tags=['Notifications'],
    request=MarkNotificationsReadSerializer,
    responses={200: OpenApiResponse(description='Notifications marked as read')}
)
class MarkNotificationsReadView(APIView):
    """Mark notifications as read."""
    
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = MarkNotificationsReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        notification_ids = serializer.validated_data.get('notification_ids', [])
        
        queryset = Notification.objects.filter(
            user=request.user,
            is_read=False
        )
        
        if notification_ids:
            queryset = queryset.filter(id__in=notification_ids)
        
        count = queryset.update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return Response({
            'success': True,
            'message': f'{count} notifications marked as read'
        })


@extend_schema(
    tags=['Notifications'],
    responses={204: OpenApiResponse(description='Notification deleted')}
)
class DeleteNotificationView(APIView):
    """Delete a notification."""
    
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, notification_id):
        notification = get_object_or_404(
            Notification,
            id=notification_id,
            user=request.user
        )
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=['Notifications'],
    responses={204: OpenApiResponse(description='All notifications deleted')}
)
class ClearNotificationsView(APIView):
    """Clear all notifications."""
    
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        Notification.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Notifications'])
class NotificationPreferencesView(generics.RetrieveUpdateAPIView):
    """Get or update notification preferences."""
    
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_or_create_preferences(self.request.user)


@extend_schema(
    tags=['Notifications'],
    request=RegisterDeviceSerializer,
    responses={
        201: DeviceTokenSerializer,
        200: DeviceTokenSerializer
    }
)
class RegisterDeviceView(APIView):
    """Register device for push notifications."""
    
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = RegisterDeviceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        platform = serializer.validated_data['platform']
        device_name = serializer.validated_data.get('device_name', '')
        
        # Update or create device token
        device, created = DeviceToken.objects.update_or_create(
            token=token,
            defaults={
                'user': request.user,
                'platform': platform,
                'device_name': device_name,
                'is_active': True
            }
        )
        
        return Response({
            'success': True,
            'message': 'Device registered' if created else 'Device updated',
            'data': DeviceTokenSerializer(device).data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


@extend_schema(tags=['Notifications'])
class MyDevicesView(generics.ListAPIView):
    """List user's registered devices."""
    
    serializer_class = DeviceTokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DeviceToken.objects.filter(
            user=self.request.user,
            is_active=True
        )


@extend_schema(
    tags=['Notifications'],
    responses={204: OpenApiResponse(description='Device unregistered')}
)
class UnregisterDeviceView(APIView):
    """Unregister a device."""
    
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, device_id):
        device = get_object_or_404(
            DeviceToken,
            id=device_id,
            user=request.user
        )
        device.is_active = False
        device.save(update_fields=['is_active'])
        return Response(status=status.HTTP_204_NO_CONTENT)
