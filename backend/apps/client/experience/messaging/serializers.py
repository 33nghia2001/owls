"""
Messaging Serializers for Owls E-commerce Platform
==================================================
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import (
    Notification, UserNotificationPreference, DeviceToken
)


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications."""

    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'body', 'notification_type',
            'image', 'icon', 'action_url', 'action_text',
            'related_order', 'related_product',
            'is_read', 'read_at', 'data', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class NotificationListSerializer(serializers.ModelSerializer):
    """Compact serializer for notification list."""

    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'body', 'notification_type',
            'icon', 'action_url', 'is_read', 'created_at'
        ]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for notification preferences."""

    class Meta:
        model = UserNotificationPreference
        fields = [
            'push_enabled', 'push_order_updates', 'push_promotions',
            'push_price_drops', 'push_back_in_stock',
            'email_enabled', 'email_order_updates', 'email_promotions',
            'email_newsletter',
            'sms_enabled', 'sms_order_updates',
            'quiet_hours_enabled', 'quiet_hours_start', 'quiet_hours_end'
        ]


class RegisterDeviceSerializer(serializers.Serializer):
    """Serializer for registering device token."""
    
    token = serializers.CharField(max_length=500)
    platform = serializers.ChoiceField(choices=DeviceToken.Platform.choices)
    device_name = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate_token(self, value):
        """Validate token format."""
        if len(value) < 10:
            raise serializers.ValidationError(_('Invalid token'))
        return value


class DeviceTokenSerializer(serializers.ModelSerializer):
    """Serializer for device tokens."""

    class Meta:
        model = DeviceToken
        fields = [
            'id', 'platform', 'device_name', 'is_active', 'last_used_at'
        ]
        read_only_fields = ['id', 'last_used_at']


class MarkNotificationsReadSerializer(serializers.Serializer):
    """Serializer for marking notifications as read."""
    
    notification_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=True,
        help_text='List of notification IDs to mark as read. Empty = mark all.'
    )


class NotificationCountSerializer(serializers.Serializer):
    """Serializer for notification counts."""
    
    total = serializers.IntegerField()
    unread = serializers.IntegerField()
    by_type = serializers.DictField(child=serializers.IntegerField())
