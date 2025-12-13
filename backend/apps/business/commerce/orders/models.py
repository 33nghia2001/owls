"""
Order Models for Owls E-commerce Platform
==========================================
Complete order management system with support for multi-vendor orders.
"""

import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator
from apps.base.core.system.models import TimeStampedModel, MetaDataModel


def generate_order_number():
    """
    Generate cryptographically secure unique order number.
    Uses secrets module instead of random for better entropy.
    
    Format: {PREFIX}{YYMMDD}{6-digit-alphanumeric}
    Example: OWL231213A3B5C9
    """
    import secrets
    import string
    from datetime import datetime
    
    prefix = settings.OWLS_CONFIG.get('ORDER_ID_PREFIX', 'OWL')
    date_part = datetime.now().strftime('%y%m%d')
    
    # Use secrets module for cryptographically secure random
    # Generate 6 alphanumeric characters (uppercase + digits)
    alphabet = string.ascii_uppercase + string.digits
    random_part = ''.join(secrets.choice(alphabet) for _ in range(6))
    
    return f'{prefix}{date_part}{random_part}'


class Order(TimeStampedModel, MetaDataModel):
    """
    Main order model.
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending Payment')
        PAID = 'paid', _('Paid')
        PROCESSING = 'processing', _('Processing')
        SHIPPED = 'shipped', _('Shipped')
        DELIVERED = 'delivered', _('Delivered')
        COMPLETED = 'completed', _('Completed')
        CANCELLED = 'cancelled', _('Cancelled')
        REFUNDED = 'refunded', _('Refunded')
        FAILED = 'failed', _('Failed')
    
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        PROCESSING = 'processing', _('Processing')
        PAID = 'paid', _('Paid')
        FAILED = 'failed', _('Failed')
        REFUNDED = 'refunded', _('Refunded')
        PARTIALLY_REFUNDED = 'partially_refunded', _('Partially Refunded')

    # Primary identifiers
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    order_number = models.CharField(
        _('Order number'),
        max_length=50,
        unique=True,
        default=generate_order_number,
        db_index=True
    )
    
    # Customer
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders'
    )
    email = models.EmailField(_('Email'))  # Stored for record keeping
    phone = models.CharField(_('Phone'), max_length=20)
    
    # Status
    status = models.CharField(
        _('Status'),
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    payment_status = models.CharField(
        _('Payment status'),
        max_length=30,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    
    # Pricing
    currency = models.CharField(_('Currency'), max_length=3, default='VND')
    subtotal = models.DecimalField(
        _('Subtotal'),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    discount_amount = models.DecimalField(
        _('Discount'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    shipping_amount = models.DecimalField(
        _('Shipping'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    tax_amount = models.DecimalField(
        _('Tax'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    total = models.DecimalField(
        _('Total'),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Coupon
    coupon = models.ForeignKey(
        'coupons.Coupon',
        on_delete=models.SET_NULL,
        related_name='orders',
        blank=True,
        null=True
    )
    coupon_code = models.CharField(_('Coupon code'), max_length=50, blank=True)
    
    # Shipping Address
    shipping_address = models.ForeignKey(
        'users.UserAddress',
        on_delete=models.SET_NULL,
        related_name='shipping_orders',
        blank=True,
        null=True
    )
    # Denormalized shipping info (in case address is deleted)
    shipping_name = models.CharField(_('Shipping name'), max_length=255)
    shipping_phone = models.CharField(_('Shipping phone'), max_length=20)
    shipping_address_line = models.TextField(_('Shipping address'))
    shipping_city = models.CharField(_('Shipping city'), max_length=100)
    shipping_country = models.CharField(_('Shipping country'), max_length=100, default='Vietnam')
    
    # Billing Address (optional)
    billing_address = models.ForeignKey(
        'users.UserAddress',
        on_delete=models.SET_NULL,
        related_name='billing_orders',
        blank=True,
        null=True
    )
    
    # Notes
    customer_note = models.TextField(_('Customer note'), blank=True)
    staff_note = models.TextField(_('Staff note'), blank=True)
    
    # Tracking
    ip_address = models.GenericIPAddressField(_('IP address'), blank=True, null=True)
    user_agent = models.TextField(_('User agent'), blank=True)
    source = models.CharField(_('Source'), max_length=50, blank=True)  # web, app, etc.
    
    # Timestamps
    paid_at = models.DateTimeField(_('Paid at'), blank=True, null=True)
    shipped_at = models.DateTimeField(_('Shipped at'), blank=True, null=True)
    delivered_at = models.DateTimeField(_('Delivered at'), blank=True, null=True)
    completed_at = models.DateTimeField(_('Completed at'), blank=True, null=True)
    cancelled_at = models.DateTimeField(_('Cancelled at'), blank=True, null=True)
    cancellation_reason = models.TextField(_('Cancellation reason'), blank=True)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'payment_status']),
            models.Index(fields=['order_number']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.order_number

    @property
    def can_cancel(self):
        """Check if order can be cancelled."""
        return self.status in [
            self.Status.PENDING,
            self.Status.PAID,
            self.Status.PROCESSING
        ]

    @property
    def can_refund(self):
        """Check if order can be refunded."""
        return self.status in [
            self.Status.PAID,
            self.Status.PROCESSING,
            self.Status.SHIPPED,
            self.Status.DELIVERED,
            self.Status.COMPLETED
        ]

    def update_status(self, new_status, note=''):
        """Update order status with timestamp."""
        old_status = self.status
        self.status = new_status
        
        # Update relevant timestamps
        now = timezone.now()
        if new_status == self.Status.PAID:
            self.paid_at = now
            self.payment_status = self.PaymentStatus.PAID
        elif new_status == self.Status.SHIPPED:
            self.shipped_at = now
        elif new_status == self.Status.DELIVERED:
            self.delivered_at = now
        elif new_status == self.Status.COMPLETED:
            self.completed_at = now
        elif new_status == self.Status.CANCELLED:
            self.cancelled_at = now
            self.cancellation_reason = note
        
        self.save()
        
        # Create status history
        OrderStatusHistory.objects.create(
            order=self,
            old_status=old_status,
            new_status=new_status,
            note=note
        )


class OrderItem(TimeStampedModel):
    """
    Individual item in an order.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    vendor = models.ForeignKey(
        'vendors.Vendor',
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.PROTECT,
        related_name='order_items',
        blank=True,
        null=True
    )
    
    # Product snapshot (denormalized)
    product_name = models.CharField(_('Product name'), max_length=500)
    product_sku = models.CharField(_('SKU'), max_length=100)
    product_image = models.URLField(_('Product image'), blank=True)
    variant_name = models.CharField(_('Variant'), max_length=255, blank=True)
    selected_options = models.JSONField(_('Options'), default=dict, blank=True)
    
    # Quantity & Pricing
    quantity = models.PositiveIntegerField(
        _('Quantity'),
        validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(
        _('Unit price'),
        max_digits=15,
        decimal_places=2
    )
    discount_amount = models.DecimalField(
        _('Discount'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    total_price = models.DecimalField(
        _('Total'),
        max_digits=15,
        decimal_places=2
    )
    
    # Vendor commission
    commission_rate = models.DecimalField(
        _('Commission rate'),
        max_digits=5,
        decimal_places=4,
        default=0.15
    )
    commission_amount = models.DecimalField(
        _('Commission'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    vendor_amount = models.DecimalField(
        _('Vendor amount'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    
    # Item status
    status = models.CharField(
        _('Status'),
        max_length=30,
        choices=[
            ('pending', _('Pending')),
            ('confirmed', _('Confirmed')),
            ('preparing', _('Preparing')),
            ('shipped', _('Shipped')),
            ('delivered', _('Delivered')),
            ('cancelled', _('Cancelled')),
            ('refunded', _('Refunded')),
        ],
        default='pending'
    )

    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')

    def __str__(self):
        return f'{self.product_name} x {self.quantity}'

    def save(self, *args, **kwargs):
        # Calculate totals
        self.total_price = (self.unit_price * self.quantity) - self.discount_amount
        self.commission_amount = self.total_price * self.commission_rate
        self.vendor_amount = self.total_price - self.commission_amount
        super().save(*args, **kwargs)


class OrderStatusHistory(TimeStampedModel):
    """
    Track order status changes.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    old_status = models.CharField(_('Old status'), max_length=30)
    new_status = models.CharField(_('New status'), max_length=30)
    note = models.TextField(_('Note'), blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='order_status_changes',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _('Order Status History')
        verbose_name_plural = _('Order Status Histories')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.order.order_number}: {self.old_status} -> {self.new_status}'


class OrderShipment(TimeStampedModel):
    """
    Shipment tracking for orders.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='shipments'
    )
    tracking_number = models.CharField(_('Tracking number'), max_length=100)
    carrier = models.CharField(_('Carrier'), max_length=100)
    carrier_code = models.CharField(_('Carrier code'), max_length=50, blank=True)
    tracking_url = models.URLField(_('Tracking URL'), blank=True)
    
    # Status
    status = models.CharField(
        _('Status'),
        max_length=30,
        choices=[
            ('pending', _('Pending')),
            ('picked_up', _('Picked Up')),
            ('in_transit', _('In Transit')),
            ('out_for_delivery', _('Out for Delivery')),
            ('delivered', _('Delivered')),
            ('failed', _('Failed')),
            ('returned', _('Returned')),
        ],
        default='pending'
    )
    
    # Dates
    shipped_at = models.DateTimeField(_('Shipped at'), blank=True, null=True)
    estimated_delivery = models.DateTimeField(_('Estimated delivery'), blank=True, null=True)
    delivered_at = models.DateTimeField(_('Delivered at'), blank=True, null=True)
    
    # Weight & dimensions
    weight = models.DecimalField(
        _('Weight (kg)'),
        max_digits=10,
        decimal_places=3,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _('Order Shipment')
        verbose_name_plural = _('Order Shipments')

    def __str__(self):
        return f'{self.order.order_number} - {self.tracking_number}'
