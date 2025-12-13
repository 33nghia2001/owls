"""
Coupon Models for Owls E-commerce Platform
==========================================
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from apps.base.core.system.models import TimeStampedModel


class Coupon(TimeStampedModel):
    """
    Coupon/Promo code model.
    """
    
    class DiscountType(models.TextChoices):
        PERCENTAGE = 'percentage', _('Percentage')
        FIXED = 'fixed', _('Fixed Amount')
        FREE_SHIPPING = 'free_shipping', _('Free Shipping')
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    code = models.CharField(
        _('Code'),
        max_length=50,
        unique=True,
        db_index=True
    )
    name = models.CharField(_('Name'), max_length=255)
    description = models.TextField(_('Description'), blank=True)
    
    # Discount settings
    discount_type = models.CharField(
        _('Discount type'),
        max_length=20,
        choices=DiscountType.choices,
        default=DiscountType.PERCENTAGE
    )
    discount_value = models.DecimalField(
        _('Discount value'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    max_discount = models.DecimalField(
        _('Maximum discount'),
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_('Maximum discount amount for percentage coupons')
    )
    
    # Conditions
    min_order_amount = models.DecimalField(
        _('Minimum order amount'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    
    # Usage limits
    usage_limit = models.PositiveIntegerField(
        _('Total usage limit'),
        blank=True,
        null=True
    )
    usage_limit_per_user = models.PositiveIntegerField(
        _('Usage limit per user'),
        default=1
    )
    times_used = models.PositiveIntegerField(_('Times used'), default=0)
    
    # Validity
    starts_at = models.DateTimeField(_('Starts at'), default=timezone.now)
    expires_at = models.DateTimeField(_('Expires at'), blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(_('Active'), default=True)

    class Meta:
        app_label = 'coupons'
        verbose_name = _('Coupon')
        verbose_name_plural = _('Coupons')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.code} - {self.name}'

    @property
    def is_valid(self):
        """Check if coupon is currently valid."""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.starts_at > now:
            return False
        if self.expires_at and self.expires_at < now:
            return False
        if self.usage_limit and self.times_used >= self.usage_limit:
            return False
        return True

    def calculate_discount(self, subtotal):
        """
        Calculate discount amount based on coupon type.
        
        Args:
            subtotal: Cart/Order subtotal amount
            
        Returns:
            Decimal: Discount amount to apply
        """
        from decimal import Decimal
        
        if not self.is_valid:
            return Decimal('0')
        
        discount = Decimal('0')
        
        if self.discount_type == self.DiscountType.PERCENTAGE:
            # Percentage discount
            discount = subtotal * (self.discount_value / Decimal('100'))
            # Apply max discount cap if set
            if self.max_discount and discount > self.max_discount:
                discount = self.max_discount
                
        elif self.discount_type == self.DiscountType.FIXED:
            # Fixed amount discount
            discount = self.discount_value
            # Don't exceed subtotal
            if discount > subtotal:
                discount = subtotal
                
        elif self.discount_type == self.DiscountType.FREE_SHIPPING:
            # Free shipping - return 0, shipping will be handled separately
            discount = Decimal('0')
        
        return discount

    def increment_usage(self):
        """Increment usage counter after successful order."""
        self.times_used += 1
        self.save(update_fields=['times_used'])
