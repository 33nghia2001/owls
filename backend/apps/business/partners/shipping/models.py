"""
Shipping Models for Owls E-commerce Platform
=============================================
Shipping provider and rate management.
"""

import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from apps.base.core.system.models import TimeStampedModel


class ShippingProvider(TimeStampedModel):
    """
    Shipping provider/carrier model.
    Supports both API-based providers (GHN, GHTK) and manual providers.
    """
    
    class ProviderType(models.TextChoices):
        GHN = 'ghn', _('Giao Hàng Nhanh')
        GHTK = 'ghtk', _('Giao Hàng Tiết Kiệm')
        VIETTEL_POST = 'viettel_post', _('Viettel Post')
        VNPOST = 'vnpost', _('Vietnam Post')
        J_T = 'jt', _('J&T Express')
        BEST = 'best', _('BEST Express')
        MANUAL = 'manual', _('Tự vận chuyển')
    
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
    name = models.CharField(_('Name'), max_length=100)
    logo = models.ImageField(
        _('Logo'),
        upload_to='shipping_providers/',
        blank=True,
        null=True
    )
    
    # Provider type and API config
    provider_type = models.CharField(
        _('Provider type'),
        max_length=50,
        choices=ProviderType.choices,
        default=ProviderType.MANUAL
    )
    api_config = models.JSONField(
        _('API Configuration'),
        default=dict,
        blank=True,
        help_text=_('API keys, endpoints, etc.')
    )
    
    # Settings
    is_active = models.BooleanField(_('Active'), default=True)
    is_default = models.BooleanField(_('Default provider'), default=False)
    
    # Coverage
    supported_countries = models.JSONField(
        _('Supported countries'),
        default=list,
        blank=True
    )
    
    # Delivery time estimates
    min_delivery_days = models.PositiveIntegerField(
        _('Min delivery days'),
        default=1
    )
    max_delivery_days = models.PositiveIntegerField(
        _('Max delivery days'),
        default=5
    )
    
    order = models.PositiveIntegerField(_('Display order'), default=0)

    class Meta:
        verbose_name = _('Shipping Provider')
        verbose_name_plural = _('Shipping Providers')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class ShippingZone(TimeStampedModel):
    """
    Geographic shipping zones for rate calculation.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(_('Zone name'), max_length=100)
    
    # Coverage (province/city codes)
    provinces = models.JSONField(
        _('Provinces'),
        default=list,
        help_text=_('List of province codes in this zone')
    )
    districts = models.JSONField(
        _('Districts'),
        default=list,
        blank=True,
        help_text=_('Specific district codes (optional)')
    )
    
    is_active = models.BooleanField(_('Active'), default=True)

    class Meta:
        verbose_name = _('Shipping Zone')
        verbose_name_plural = _('Shipping Zones')
        ordering = ['name']

    def __str__(self):
        return self.name


class ShippingRate(TimeStampedModel):
    """
    Shipping rate for a provider and zone combination.
    Supports weight-based and value-based pricing.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    provider = models.ForeignKey(
        ShippingProvider,
        on_delete=models.CASCADE,
        related_name='rates'
    )
    zone = models.ForeignKey(
        ShippingZone,
        on_delete=models.CASCADE,
        related_name='rates'
    )
    name = models.CharField(_('Rate name'), max_length=100)
    
    # Base rate
    base_rate = models.DecimalField(
        _('Base rate'),
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Weight-based pricing
    min_weight = models.DecimalField(
        _('Min weight (kg)'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    max_weight = models.DecimalField(
        _('Max weight (kg)'),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    rate_per_kg = models.DecimalField(
        _('Rate per kg'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    # Value-based conditions
    min_order_value = models.DecimalField(
        _('Min order value'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    max_order_value = models.DecimalField(
        _('Max order value'),
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True
    )
    
    # Free shipping threshold
    free_shipping_threshold = models.DecimalField(
        _('Free shipping threshold'),
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True
    )
    
    is_active = models.BooleanField(_('Active'), default=True)

    class Meta:
        verbose_name = _('Shipping Rate')
        verbose_name_plural = _('Shipping Rates')
        ordering = ['provider', 'zone', 'min_weight']
        unique_together = [['provider', 'zone', 'min_weight']]

    def __str__(self):
        return f'{self.provider.name} - {self.zone.name} - {self.name}'
    
    def calculate_rate(
        self, 
        weight: Decimal, 
        order_value: Decimal
    ) -> Decimal:
        """
        Calculate shipping rate based on weight and order value.
        
        Args:
            weight: Total weight in kg
            order_value: Order subtotal
            
        Returns:
            Decimal: Calculated shipping cost
        """
        # Free shipping check
        if self.free_shipping_threshold and order_value >= self.free_shipping_threshold:
            return Decimal('0')
        
        # Base rate + weight-based rate
        if weight <= 0:
            weight = Decimal('0.5')  # Minimum weight
        
        shipping_cost = self.base_rate + (self.rate_per_kg * weight)
        
        return shipping_cost.quantize(Decimal('0.01'))


class ShippingMethod(TimeStampedModel):
    """
    Shipping method (Express, Standard, Economy, etc.)
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    provider = models.ForeignKey(
        ShippingProvider,
        on_delete=models.CASCADE,
        related_name='methods'
    )
    code = models.CharField(_('Code'), max_length=50)
    name = models.CharField(_('Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    
    # API service code (for external providers)
    api_service_code = models.CharField(
        _('API service code'),
        max_length=50,
        blank=True
    )
    
    # Delivery time
    min_delivery_days = models.PositiveIntegerField(
        _('Min delivery days'),
        default=1
    )
    max_delivery_days = models.PositiveIntegerField(
        _('Max delivery days'),
        default=3
    )
    
    # Rate multiplier (e.g., 1.5x for express)
    rate_multiplier = models.DecimalField(
        _('Rate multiplier'),
        max_digits=5,
        decimal_places=2,
        default=Decimal('1.00')
    )
    
    is_active = models.BooleanField(_('Active'), default=True)
    order = models.PositiveIntegerField(_('Display order'), default=0)

    class Meta:
        verbose_name = _('Shipping Method')
        verbose_name_plural = _('Shipping Methods')
        ordering = ['provider', 'order']
        unique_together = [['provider', 'code']]

    def __str__(self):
        return f'{self.provider.name} - {self.name}'
