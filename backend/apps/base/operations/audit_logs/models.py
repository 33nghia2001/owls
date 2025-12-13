"""
Audit Log Models for Owls E-commerce Platform
==============================================
Comprehensive activity logging and tracking.
"""

import uuid
from django.db import models
from django.conf import settings
from apps.base.core.users.models import TimeStampedModel


class AuditAction(models.TextChoices):
    """Types of auditable actions."""
    CREATE = 'create', 'Create'
    READ = 'read', 'Read'
    UPDATE = 'update', 'Update'
    DELETE = 'delete', 'Delete'
    LOGIN = 'login', 'Login'
    LOGOUT = 'logout', 'Logout'
    FAILED_LOGIN = 'failed_login', 'Failed Login'
    PASSWORD_CHANGE = 'password_change', 'Password Change'
    PASSWORD_RESET = 'password_reset', 'Password Reset'
    EXPORT = 'export', 'Data Export'
    IMPORT = 'import', 'Data Import'
    APPROVE = 'approve', 'Approve'
    REJECT = 'reject', 'Reject'
    CANCEL = 'cancel', 'Cancel'
    REFUND = 'refund', 'Refund'


class AuditLog(TimeStampedModel):
    """
    Main audit log model.
    Records all significant system activities.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Who performed the action
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='audit_logs'
    )
    user_email = models.EmailField(blank=True)
    user_role = models.CharField(max_length=50, blank=True)

    # Action details
    action = models.CharField(max_length=30, choices=AuditAction.choices)
    action_description = models.CharField(max_length=500, blank=True)

    # Target resource
    resource_type = models.CharField(
        max_length=100,
        help_text='e.g., Order, Product, User'
    )
    resource_id = models.CharField(max_length=100, blank=True)
    resource_name = models.CharField(max_length=255, blank=True)

    # Changes tracking
    old_values = models.JSONField(
        default=dict, blank=True,
        help_text='Previous values before change'
    )
    new_values = models.JSONField(
        default=dict, blank=True,
        help_text='New values after change'
    )
    changed_fields = models.JSONField(
        default=list, blank=True,
        help_text='List of fields that were changed'
    )

    # Request context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_method = models.CharField(max_length=10, blank=True)
    request_path = models.CharField(max_length=500, blank=True)
    request_id = models.CharField(max_length=100, blank=True)

    # Additional context
    module = models.CharField(max_length=100, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)

    # Status
    status = models.CharField(
        max_length=20,
        default='success',
        choices=[
            ('success', 'Success'),
            ('failure', 'Failure'),
            ('warning', 'Warning'),
        ]
    )
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
            models.Index(fields=['resource_type', 'resource_id']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['ip_address']),
        ]

    def __str__(self):
        return f"{self.action} on {self.resource_type} by {self.user_email or 'System'}"

    @classmethod
    def log(cls, action, resource_type, resource_id=None, resource_name=None,
            user=None, old_values=None, new_values=None, request=None, **kwargs):
        """
        Convenience method to create audit logs.
        """
        log = cls(
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else '',
            resource_name=resource_name or '',
            old_values=old_values or {},
            new_values=new_values or {},
            **kwargs
        )

        if user:
            log.user = user
            log.user_email = user.email
            log.user_role = getattr(user, 'role', '')

        if request:
            log.ip_address = cls._get_client_ip(request)
            log.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            log.request_method = request.method
            log.request_path = request.path
            log.request_id = request.META.get('HTTP_X_REQUEST_ID', '')

        if old_values and new_values:
            log.changed_fields = [
                k for k in new_values.keys()
                if old_values.get(k) != new_values.get(k)
            ]

        log.save()
        return log

    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


class LoginAttempt(TimeStampedModel):
    """
    Track login attempts for security monitoring.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='login_attempts'
    )
    email = models.EmailField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)

    success = models.BooleanField(default=False)
    failure_reason = models.CharField(max_length=100, blank=True)

    # Geolocation (optional)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'login_attempts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', '-created_at']),
            models.Index(fields=['ip_address', '-created_at']),
            models.Index(fields=['success', '-created_at']),
        ]

    def __str__(self):
        status = 'Success' if self.success else 'Failed'
        return f"{status} login attempt for {self.email}"


class DataExportLog(TimeStampedModel):
    """
    Track data exports for compliance.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='data_exports'
    )

    export_type = models.CharField(
        max_length=50,
        choices=[
            ('orders', 'Orders'),
            ('products', 'Products'),
            ('customers', 'Customers'),
            ('transactions', 'Transactions'),
            ('reports', 'Reports'),
            ('gdpr', 'GDPR Request'),
            ('other', 'Other'),
        ]
    )
    format = models.CharField(
        max_length=20,
        choices=[
            ('csv', 'CSV'),
            ('xlsx', 'Excel'),
            ('json', 'JSON'),
            ('pdf', 'PDF'),
        ]
    )

    # Export details
    filters_applied = models.JSONField(default=dict)
    record_count = models.PositiveIntegerField(default=0)
    file_size_bytes = models.PositiveIntegerField(default=0)

    # Status
    status = models.CharField(
        max_length=20,
        default='pending',
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ]
    )
    file_url = models.URLField(blank=True)
    error_message = models.TextField(blank=True)

    # Request context
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = 'data_export_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.export_type} export by {self.user}"


class SystemEvent(TimeStampedModel):
    """
    System-level events for monitoring.
    """

    class EventLevel(models.TextChoices):
        DEBUG = 'debug', 'Debug'
        INFO = 'info', 'Info'
        WARNING = 'warning', 'Warning'
        ERROR = 'error', 'Error'
        CRITICAL = 'critical', 'Critical'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=100)
    event_level = models.CharField(
        max_length=20,
        choices=EventLevel.choices,
        default=EventLevel.INFO
    )
    message = models.TextField()

    # Source
    source = models.CharField(max_length=100, blank=True)
    module = models.CharField(max_length=100, blank=True)

    # Details
    details = models.JSONField(default=dict)
    stack_trace = models.TextField(blank=True)

    # Resolution
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='resolved_events'
    )
    resolution_notes = models.TextField(blank=True)

    class Meta:
        db_table = 'system_events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', '-created_at']),
            models.Index(fields=['event_level', '-created_at']),
            models.Index(fields=['resolved', '-created_at']),
        ]

    def __str__(self):
        return f"[{self.event_level.upper()}] {self.event_type}: {self.message[:50]}"
