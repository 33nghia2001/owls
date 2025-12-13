"""
Audit Log Serializers for Owls E-commerce Platform
==================================================
"""

from rest_framework import serializers
from .models import AuditLog, LoginAttempt, DataExportLog, SystemEvent


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for audit logs."""

    user_display = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_display', 'user_email', 'user_role',
            'action', 'action_description',
            'resource_type', 'resource_id', 'resource_name',
            'old_values', 'new_values', 'changed_fields',
            'ip_address', 'request_method', 'request_path',
            'module', 'status', 'error_message',
            'created_at'
        ]

    def get_user_display(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.email
        return obj.user_email or 'System'


class AuditLogListSerializer(serializers.ModelSerializer):
    """Compact serializer for audit log list."""

    user_display = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user_display', 'action', 'resource_type',
            'resource_name', 'status', 'created_at'
        ]

    def get_user_display(self, obj):
        return obj.user_email or 'System'


class LoginAttemptSerializer(serializers.ModelSerializer):
    """Serializer for login attempts."""

    class Meta:
        model = LoginAttempt
        fields = [
            'id', 'email', 'ip_address', 'user_agent',
            'success', 'failure_reason',
            'country', 'city', 'created_at'
        ]


class DataExportLogSerializer(serializers.ModelSerializer):
    """Serializer for data export logs."""

    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = DataExportLog
        fields = [
            'id', 'user', 'user_email',
            'export_type', 'format', 'filters_applied',
            'record_count', 'file_size_bytes',
            'status', 'file_url', 'error_message',
            'created_at'
        ]


class SystemEventSerializer(serializers.ModelSerializer):
    """Serializer for system events."""

    resolved_by_email = serializers.EmailField(source='resolved_by.email', read_only=True)

    class Meta:
        model = SystemEvent
        fields = [
            'id', 'event_type', 'event_level', 'message',
            'source', 'module', 'details',
            'resolved', 'resolved_at', 'resolved_by', 'resolved_by_email',
            'resolution_notes', 'created_at'
        ]


class SystemEventListSerializer(serializers.ModelSerializer):
    """Compact serializer for system event list."""

    class Meta:
        model = SystemEvent
        fields = [
            'id', 'event_type', 'event_level', 'message',
            'source', 'resolved', 'created_at'
        ]


class ResolveEventSerializer(serializers.Serializer):
    """Serializer for resolving system events."""

    resolution_notes = serializers.CharField(required=False, allow_blank=True)
