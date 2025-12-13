"""
Messaging Models for Owls E-commerce Platform
=============================================
User notifications and in-app messaging system.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from apps.base.core.system.models import TimeStampedModel


class NotificationTemplate(TimeStampedModel):
    """
    Templates for notifications.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    code = models.CharField(
        _('Code'),
        max_length=100,
        unique=True,
        help_text=_('e.g., order_confirmed, payment_received')
    )
    name = models.CharField(_('Name'), max_length=255)
    
    # Content
    title_template = models.CharField(
        _('Title template'),
        max_length=255,
        help_text=_('Use {variable} for placeholders')
    )
    body_template = models.TextField(
        _('Body template'),
        help_text=_('Use {variable} for placeholders')
    )
    
    # Channels
    send_push = models.BooleanField(_('Send push notification'), default=True)
    send_email = models.BooleanField(_('Send email'), default=False)
    send_sms = models.BooleanField(_('Send SMS'), default=False)
    
    # Category for grouping
    category = models.CharField(
        _('Category'),
        max_length=50,
        choices=[
            ('order', _('Order')),
            ('payment', _('Payment')),
            ('shipping', _('Shipping')),
            ('promotion', _('Promotion')),
            ('account', _('Account')),
            ('system', _('System')),
        ],
        default='system'
    )
    
    is_active = models.BooleanField(_('Active'), default=True)

    class Meta:
        app_label = 'messaging'
        verbose_name = _('Notification Template')
        verbose_name_plural = _('Notification Templates')

    def __str__(self):
        return f"{self.code} - {self.name}"

    def render(self, context: dict):
        """Render template with context."""
        title = self.title_template
        body = self.body_template
        
        for key, value in context.items():
            title = title.replace(f'{{{key}}}', str(value))
            body = body.replace(f'{{{key}}}', str(value))
        
        return title, body


class Notification(TimeStampedModel):
    """
    User notification model.
    """
    
    class NotificationType(models.TextChoices):
        ORDER = 'order', _('Order')
        PAYMENT = 'payment', _('Payment')
        SHIPPING = 'shipping', _('Shipping')
        PROMOTION = 'promotion', _('Promotion')
        ACCOUNT = 'account', _('Account')
        SYSTEM = 'system', _('System')
        LOYALTY = 'loyalty', _('Loyalty')
        REVIEW = 'review', _('Review')
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    # Content
    title = models.CharField(_('Title'), max_length=255)
    body = models.TextField(_('Body'))
    notification_type = models.CharField(
        _('Type'),
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
        db_index=True
    )
    
    # Optional image/icon
    image = models.URLField(_('Image URL'), blank=True)
    icon = models.CharField(_('Icon class'), max_length=100, blank=True)
    
    # Action link
    action_url = models.CharField(_('Action URL'), max_length=500, blank=True)
    action_text = models.CharField(_('Action text'), max_length=100, blank=True)
    
    # Related objects
    related_order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    related_product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    
    # Status
    is_read = models.BooleanField(_('Read'), default=False, db_index=True)
    read_at = models.DateTimeField(_('Read at'), blank=True, null=True)
    
    # Push status
    push_sent = models.BooleanField(_('Push sent'), default=False)
    push_sent_at = models.DateTimeField(_('Push sent at'), blank=True, null=True)
    
    # Extra data
    data = models.JSONField(_('Extra data'), default=dict, blank=True)

    class Meta:
        app_label = 'messaging'
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.email}"

    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at', 'updated_at'])


class UserNotificationPreference(TimeStampedModel):
    """
    User's notification preferences.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # Push notifications
    push_enabled = models.BooleanField(_('Push notifications enabled'), default=True)
    push_order_updates = models.BooleanField(_('Order updates'), default=True)
    push_promotions = models.BooleanField(_('Promotions'), default=True)
    push_price_drops = models.BooleanField(_('Price drops'), default=True)
    push_back_in_stock = models.BooleanField(_('Back in stock'), default=True)
    
    # Email notifications
    email_enabled = models.BooleanField(_('Email notifications enabled'), default=True)
    email_order_updates = models.BooleanField(_('Order updates via email'), default=True)
    email_promotions = models.BooleanField(_('Promotional emails'), default=False)
    email_newsletter = models.BooleanField(_('Newsletter'), default=False)
    
    # SMS notifications
    sms_enabled = models.BooleanField(_('SMS notifications enabled'), default=False)
    sms_order_updates = models.BooleanField(_('Order updates via SMS'), default=False)
    
    # Quiet hours
    quiet_hours_enabled = models.BooleanField(_('Quiet hours enabled'), default=False)
    quiet_hours_start = models.TimeField(_('Quiet hours start'), default='22:00')
    quiet_hours_end = models.TimeField(_('Quiet hours end'), default='08:00')

    class Meta:
        app_label = 'messaging'
        verbose_name = _('Notification Preference')
        verbose_name_plural = _('Notification Preferences')

    def __str__(self):
        return f"{self.user.email}'s notification preferences"


class DeviceToken(TimeStampedModel):
    """
    User device tokens for push notifications.
    """
    
    class Platform(models.TextChoices):
        IOS = 'ios', _('iOS')
        ANDROID = 'android', _('Android')
        WEB = 'web', _('Web')
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='device_tokens'
    )
    token = models.CharField(_('Token'), max_length=500, unique=True)
    platform = models.CharField(
        _('Platform'),
        max_length=20,
        choices=Platform.choices
    )
    device_name = models.CharField(_('Device name'), max_length=255, blank=True)
    
    is_active = models.BooleanField(_('Active'), default=True)
    last_used_at = models.DateTimeField(_('Last used'), auto_now=True)

    class Meta:
        app_label = 'messaging'
        verbose_name = _('Device Token')
        verbose_name_plural = _('Device Tokens')

    def __str__(self):
        return f"{self.user.email} - {self.platform}"
