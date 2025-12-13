"""
Payment Models for Owls E-commerce Platform
============================================
Payment processing and transaction management.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from apps.base.core.system.models import TimeStampedModel, MetaDataModel


def generate_transaction_id():
    """Generate unique transaction ID."""
    import random
    import string
    from datetime import datetime
    
    date_part = datetime.now().strftime('%y%m%d%H%M%S')
    random_part = ''.join(random.choices(string.digits, k=6))
    return f'TXN{date_part}{random_part}'


class PaymentMethod(TimeStampedModel):
    """
    Available payment methods.
    """
    code = models.CharField(_('Code'), max_length=50, unique=True)
    name = models.CharField(_('Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    icon = models.ImageField(
        _('Icon'),
        upload_to='payment_methods/',
        blank=True,
        null=True
    )
    
    # Configuration
    gateway = models.CharField(
        _('Gateway'),
        max_length=50,
        choices=[
            ('vnpay', 'VNPay'),
            ('momo', 'MoMo'),
            ('zalopay', 'ZaloPay'),
            ('bank_transfer', 'Bank Transfer'),
            ('cod', 'Cash on Delivery'),
            ('wallet', 'Owls Wallet'),
            ('stripe', 'Stripe'),
            ('paypal', 'PayPal'),
        ]
    )
    config = models.JSONField(_('Configuration'), default=dict, blank=True)
    
    # Settings
    is_active = models.BooleanField(_('Active'), default=True)
    min_amount = models.DecimalField(
        _('Minimum amount'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    max_amount = models.DecimalField(
        _('Maximum amount'),
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True
    )
    fee_type = models.CharField(
        _('Fee type'),
        max_length=20,
        choices=[
            ('fixed', 'Fixed'),
            ('percentage', 'Percentage'),
            ('both', 'Fixed + Percentage'),
        ],
        default='fixed'
    )
    fee_amount = models.DecimalField(
        _('Fee amount'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    fee_percentage = models.DecimalField(
        _('Fee percentage'),
        max_digits=5,
        decimal_places=4,
        default=0
    )
    
    order = models.PositiveIntegerField(_('Order'), default=0)

    class Meta:
        verbose_name = _('Payment Method')
        verbose_name_plural = _('Payment Methods')
        ordering = ['order']

    def __str__(self):
        return self.name

    def calculate_fee(self, amount):
        """Calculate payment fee."""
        if self.fee_type == 'fixed':
            return self.fee_amount
        elif self.fee_type == 'percentage':
            return amount * self.fee_percentage
        else:  # both
            return self.fee_amount + (amount * self.fee_percentage)


class Payment(TimeStampedModel, MetaDataModel):
    """
    Payment record for orders.
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        PROCESSING = 'processing', _('Processing')
        COMPLETED = 'completed', _('Completed')
        FAILED = 'failed', _('Failed')
        CANCELLED = 'cancelled', _('Cancelled')
        REFUNDED = 'refunded', _('Refunded')
        PARTIALLY_REFUNDED = 'partially_refunded', _('Partially Refunded')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    transaction_id = models.CharField(
        _('Transaction ID'),
        max_length=100,
        unique=True,
        default=generate_transaction_id,
        db_index=True
    )
    
    # Order
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.PROTECT,
        related_name='payments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='payments'
    )
    
    # Payment method
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.PROTECT,
        related_name='payments'
    )
    
    # Amounts
    currency = models.CharField(_('Currency'), max_length=3, default='VND')
    amount = models.DecimalField(
        _('Amount'),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    fee = models.DecimalField(
        _('Fee'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    net_amount = models.DecimalField(
        _('Net amount'),
        max_digits=15,
        decimal_places=2
    )
    
    # Status
    status = models.CharField(
        _('Status'),
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    
    # Gateway response
    gateway_transaction_id = models.CharField(
        _('Gateway transaction ID'),
        max_length=255,
        blank=True
    )
    gateway_response = models.JSONField(
        _('Gateway response'),
        default=dict,
        blank=True
    )
    
    # Error info
    error_code = models.CharField(_('Error code'), max_length=50, blank=True)
    error_message = models.TextField(_('Error message'), blank=True)
    
    # Timestamps
    paid_at = models.DateTimeField(_('Paid at'), blank=True, null=True)
    expires_at = models.DateTimeField(_('Expires at'), blank=True, null=True)
    
    # Tracking
    ip_address = models.GenericIPAddressField(_('IP address'), blank=True, null=True)
    user_agent = models.TextField(_('User agent'), blank=True)

    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['order', 'status']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f'{self.transaction_id} - {self.amount} {self.currency}'

    def save(self, *args, **kwargs):
        if not self.net_amount:
            self.net_amount = self.amount - self.fee
        super().save(*args, **kwargs)


class Refund(TimeStampedModel):
    """
    Refund records.
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        PROCESSING = 'processing', _('Processing')
        COMPLETED = 'completed', _('Completed')
        FAILED = 'failed', _('Failed')
        CANCELLED = 'cancelled', _('Cancelled')
    
    class Reason(models.TextChoices):
        CUSTOMER_REQUEST = 'customer_request', _('Customer Request')
        DEFECTIVE_PRODUCT = 'defective_product', _('Defective Product')
        WRONG_PRODUCT = 'wrong_product', _('Wrong Product')
        LATE_DELIVERY = 'late_delivery', _('Late Delivery')
        ORDER_CANCELLED = 'order_cancelled', _('Order Cancelled')
        OTHER = 'other', _('Other')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    refund_number = models.CharField(
        _('Refund number'),
        max_length=50,
        unique=True,
        db_index=True
    )
    
    # Relations
    payment = models.ForeignKey(
        Payment,
        on_delete=models.PROTECT,
        related_name='refunds'
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.PROTECT,
        related_name='refunds'
    )
    
    # Amount
    amount = models.DecimalField(
        _('Amount'),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Status
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    # Reason
    reason = models.CharField(
        _('Reason'),
        max_length=30,
        choices=Reason.choices
    )
    reason_detail = models.TextField(_('Reason detail'), blank=True)
    
    # Gateway response
    gateway_refund_id = models.CharField(
        _('Gateway refund ID'),
        max_length=255,
        blank=True
    )
    gateway_response = models.JSONField(
        _('Gateway response'),
        default=dict,
        blank=True
    )
    
    # Processing
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='processed_refunds',
        blank=True,
        null=True
    )
    processed_at = models.DateTimeField(_('Processed at'), blank=True, null=True)
    notes = models.TextField(_('Notes'), blank=True)

    class Meta:
        verbose_name = _('Refund')
        verbose_name_plural = _('Refunds')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.refund_number} - {self.amount}'

    def save(self, *args, **kwargs):
        if not self.refund_number:
            import random
            import string
            from datetime import datetime
            
            date_part = datetime.now().strftime('%y%m%d')
            random_part = ''.join(random.choices(string.digits, k=6))
            self.refund_number = f'REF{date_part}{random_part}'
        super().save(*args, **kwargs)


class PaymentLog(TimeStampedModel):
    """
    Payment activity log for audit.
    """
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    action = models.CharField(_('Action'), max_length=50)
    status = models.CharField(_('Status'), max_length=30)
    request_data = models.JSONField(_('Request'), default=dict, blank=True)
    response_data = models.JSONField(_('Response'), default=dict, blank=True)
    ip_address = models.GenericIPAddressField(_('IP'), blank=True, null=True)
    notes = models.TextField(_('Notes'), blank=True)

    class Meta:
        verbose_name = _('Payment Log')
        verbose_name_plural = _('Payment Logs')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.payment.transaction_id} - {self.action}'
