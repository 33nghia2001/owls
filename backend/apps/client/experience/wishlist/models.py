"""
Wishlist Models for Owls E-commerce Platform
=============================================
User product wishlist/favorites functionality.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.base.core.system.models import TimeStampedModel


class Wishlist(TimeStampedModel):
    """
    User's wishlist.
    Each user has one main wishlist.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishlist'
    )
    name = models.CharField(
        _('Name'),
        max_length=255,
        default='My Wishlist'
    )
    is_public = models.BooleanField(
        _('Public'),
        default=False,
        help_text=_('Allow others to view this wishlist')
    )

    class Meta:
        app_label = 'wishlist'
        verbose_name = _('Wishlist')
        verbose_name_plural = _('Wishlists')

    def __str__(self):
        return f"{self.user.email}'s Wishlist"

    @property
    def item_count(self):
        """Return total items in wishlist."""
        return self.items.count()

    def add_product(self, product, variant=None):
        """
        Add product to wishlist.
        
        Args:
            product: Product instance
            variant: Optional ProductVariant instance
            
        Returns:
            WishlistItem instance
        """
        item, created = WishlistItem.objects.get_or_create(
            wishlist=self,
            product=product,
            variant=variant
        )
        return item

    def remove_product(self, product, variant=None):
        """Remove product from wishlist."""
        WishlistItem.objects.filter(
            wishlist=self,
            product=product,
            variant=variant
        ).delete()

    def contains_product(self, product, variant=None):
        """Check if product is in wishlist."""
        return WishlistItem.objects.filter(
            wishlist=self,
            product=product,
            variant=variant
        ).exists()

    def clear(self):
        """Remove all items from wishlist."""
        self.items.all().delete()


class WishlistItem(TimeStampedModel):
    """
    Individual item in a wishlist.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='wishlist_items'
    )
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.CASCADE,
        related_name='wishlist_items',
        blank=True,
        null=True
    )
    # Track price at time of adding (for price drop alerts)
    price_when_added = models.DecimalField(
        _('Price when added'),
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True
    )
    notes = models.TextField(_('Notes'), blank=True)

    class Meta:
        app_label = 'wishlist'
        verbose_name = _('Wishlist Item')
        verbose_name_plural = _('Wishlist Items')
        unique_together = ['wishlist', 'product', 'variant']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} in {self.wishlist}"

    def save(self, *args, **kwargs):
        # Capture price when adding to wishlist
        if not self.price_when_added:
            if self.variant:
                self.price_when_added = self.variant.price or self.product.price
            else:
                self.price_when_added = self.product.price
        super().save(*args, **kwargs)

    @property
    def current_price(self):
        """Get current product price."""
        if self.variant:
            return self.variant.price or self.product.price
        return self.product.price

    @property
    def price_dropped(self):
        """Check if price has dropped since adding."""
        if not self.price_when_added:
            return False
        return self.current_price < self.price_when_added

    @property
    def price_change(self):
        """Calculate price change amount."""
        if not self.price_when_added:
            return 0
        return self.current_price - self.price_when_added
