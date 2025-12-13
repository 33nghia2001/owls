"""
Location Models for Owls E-commerce Platform
=============================================
Countries, regions, cities, and address management.
"""

import uuid
from django.db import models
from django.conf import settings
from apps.base.core.users.models import TimeStampedModel


class Country(TimeStampedModel):
    """
    Country model with shipping and tax information.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    name_native = models.CharField(max_length=100, blank=True)
    code = models.CharField(max_length=2, unique=True, help_text='ISO 3166-1 alpha-2')
    code_alpha3 = models.CharField(max_length=3, blank=True, help_text='ISO 3166-1 alpha-3')
    phone_code = models.CharField(max_length=10, blank=True)
    currency_code = models.CharField(max_length=3, blank=True)
    flag_emoji = models.CharField(max_length=10, blank=True)

    # Shipping settings
    is_shipping_available = models.BooleanField(default=True)
    shipping_zone = models.CharField(max_length=50, blank=True)

    # Display
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'countries'
        verbose_name_plural = 'Countries'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Region(TimeStampedModel):
    """
    Region/State/Province within a country.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name='regions'
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, blank=True)

    # Tax settings
    tax_rate = models.DecimalField(
        max_digits=5, decimal_places=2,
        null=True, blank=True,
        help_text='Regional tax rate override'
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'regions'
        ordering = ['name']
        unique_together = ['country', 'code']

    def __str__(self):
        return f"{self.name}, {self.country.code}"


class City(TimeStampedModel):
    """
    City within a region.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name='cities'
    )
    name = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)

    # Geolocation
    latitude = models.DecimalField(
        max_digits=10, decimal_places=7,
        null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=10, decimal_places=7,
        null=True, blank=True
    )

    # Delivery settings
    is_delivery_available = models.BooleanField(default=True)
    delivery_days = models.PositiveSmallIntegerField(
        default=3,
        help_text='Estimated delivery days to this city'
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'cities'
        verbose_name_plural = 'Cities'
        ordering = ['name']

    def __str__(self):
        return f"{self.name}, {self.region.name}"


class District(TimeStampedModel):
    """
    District/Ward within a city (for Vietnamese addresses).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name='districts'
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'districts'
        ordering = ['name']

    def __str__(self):
        return f"{self.name}, {self.city.name}"


class Ward(TimeStampedModel):
    """
    Ward within a district (for Vietnamese addresses).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        related_name='wards'
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'wards'
        ordering = ['name']

    def __str__(self):
        return f"{self.name}, {self.district.name}"


class Address(TimeStampedModel):
    """
    User address model.
    """

    class AddressType(models.TextChoices):
        SHIPPING = 'shipping', 'Shipping'
        BILLING = 'billing', 'Billing'
        BOTH = 'both', 'Both'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='location_addresses'
    )

    # Type
    address_type = models.CharField(
        max_length=20,
        choices=AddressType.choices,
        default=AddressType.BOTH
    )
    label = models.CharField(
        max_length=50, blank=True,
        help_text='e.g., Home, Office'
    )

    # Contact
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)

    # Location
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name='addresses'
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='addresses'
    )
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='addresses'
    )
    district = models.ForeignKey(
        District,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='addresses'
    )
    ward = models.ForeignKey(
        Ward,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='addresses'
    )

    # Address details
    street_address = models.CharField(max_length=500)
    street_address_2 = models.CharField(max_length=500, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)

    # Geolocation (for delivery optimization)
    latitude = models.DecimalField(
        max_digits=10, decimal_places=7,
        null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=10, decimal_places=7,
        null=True, blank=True
    )

    # Preferences
    is_default = models.BooleanField(default=False)
    delivery_instructions = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'addresses'
        verbose_name_plural = 'Addresses'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.street_address}"

    def save(self, *args, **kwargs):
        # Ensure only one default address per user per type
        if self.is_default:
            Address.objects.filter(
                user=self.user,
                address_type=self.address_type,
                is_default=True
            ).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)

    @property
    def full_address(self):
        """Get formatted full address."""
        parts = [self.street_address]
        if self.street_address_2:
            parts.append(self.street_address_2)
        if self.ward:
            parts.append(self.ward.name)
        if self.district:
            parts.append(self.district.name)
        if self.city:
            parts.append(self.city.name)
        if self.region:
            parts.append(self.region.name)
        parts.append(self.country.name)
        if self.postal_code:
            parts.append(self.postal_code)
        return ', '.join(parts)


class ShippingZone(TimeStampedModel):
    """
    Shipping zones for rate calculation.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Zone coverage
    countries = models.ManyToManyField(Country, blank=True, related_name='shipping_zones')
    regions = models.ManyToManyField(Region, blank=True, related_name='shipping_zones')

    # Default rates
    base_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    per_kg_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    free_shipping_threshold = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True
    )

    # Delivery time
    min_delivery_days = models.PositiveSmallIntegerField(default=3)
    max_delivery_days = models.PositiveSmallIntegerField(default=7)

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'shipping_zones'
        ordering = ['name']

    def __str__(self):
        return self.name
