"""
Cart Models for Owls E-commerce Platform
=========================================
Shopping cart with session and user-based storage.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from apps.base.core.system.models import TimeStampedModel


class Cart(TimeStampedModel):
    """
    Shopping cart model.
    Supports both guest (session-based) and authenticated users.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # User or session
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart',
        blank=True,
        null=True
    )
    session_key = models.CharField(
        _('Session key'),
        max_length=255,
        blank=True,
        null=True,
        db_index=True
    )
    
    # Totals (cached for performance)
    subtotal = models.DecimalField(
        _('Subtotal'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    discount_amount = models.DecimalField(
        _('Discount amount'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    tax_amount = models.DecimalField(
        _('Tax amount'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    shipping_amount = models.DecimalField(
        _('Shipping amount'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    total = models.DecimalField(
        _('Total'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    
    # Coupon
    coupon = models.ForeignKey(
        'coupons.Coupon',
        on_delete=models.SET_NULL,
        related_name='carts',
        blank=True,
        null=True
    )
    
    # Metadata
    item_count = models.PositiveIntegerField(_('Item count'), default=0)
    currency = models.CharField(_('Currency'), max_length=3, default='VND')
    notes = models.TextField(_('Notes'), blank=True)
    
    # Expires (for guest carts)
    expires_at = models.DateTimeField(_('Expires at'), blank=True, null=True)

    class Meta:
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')
        indexes = [
            models.Index(fields=['session_key']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        if self.user:
            return f'Cart - {self.user.email}'
        return f'Cart - {self.session_key}'

    def recalculate(self):
        """Recalculate cart totals."""
        items = self.items.select_related('product', 'variant')
        
        self.subtotal = sum(item.total_price for item in items)
        self.item_count = sum(item.quantity for item in items)
        
        # Apply coupon discount
        if self.coupon and self.coupon.is_valid:
            self.discount_amount = self.coupon.calculate_discount(self.subtotal)
        else:
            self.discount_amount = 0
        
        # Calculate tax (10% VAT)
        taxable_amount = self.subtotal - self.discount_amount
        self.tax_amount = taxable_amount * settings.OWLS_CONFIG.get('TAX_RATE', 0.10)
        
        # Total
        self.total = self.subtotal - self.discount_amount + self.tax_amount + self.shipping_amount
        
        self.save(update_fields=[
            'subtotal', 'discount_amount', 'tax_amount',
            'total', 'item_count', 'updated_at'
        ])
        return self

    def clear(self):
        """Remove all items from cart."""
        self.items.all().delete()
        self.coupon = None
        self.recalculate()

    def merge_with(self, other_cart):
        """Merge another cart into this one."""
        for item in other_cart.items.all():
            existing_item = self.items.filter(
                product=item.product,
                variant=item.variant
            ).first()
            
            if existing_item:
                existing_item.quantity += item.quantity
                existing_item.save()
            else:
                item.cart = self
                item.save()
        
        other_cart.delete()
        self.recalculate()


class CartItem(TimeStampedModel):
    """
    Individual item in a cart.
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.CASCADE,
        related_name='cart_items',
        blank=True,
        null=True
    )
    
    # Quantity and pricing
    quantity = models.PositiveIntegerField(
        _('Quantity'),
        default=1,
        validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(
        _('Unit price'),
        max_digits=15,
        decimal_places=2
    )
    total_price = models.DecimalField(
        _('Total price'),
        max_digits=15,
        decimal_places=2
    )
    
    # Selected options/attributes
    selected_options = models.JSONField(
        _('Selected options'),
        default=dict,
        blank=True
    )

    class Meta:
        verbose_name = _('Cart Item')
        verbose_name_plural = _('Cart Items')
        unique_together = ['cart', 'product', 'variant']

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    def save(self, *args, **kwargs):
        # Set unit price from product/variant
        if self.variant:
            self.unit_price = self.variant.price
        else:
            self.unit_price = self.product.price
        
        # Calculate total
        self.total_price = self.unit_price * self.quantity
        
        super().save(*args, **kwargs)
        
        # Recalculate cart totals
        self.cart.recalculate()

    def delete(self, *args, **kwargs):
        cart = self.cart
        super().delete(*args, **kwargs)
        cart.recalculate()
