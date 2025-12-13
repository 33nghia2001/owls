"""
Product Models for Owls E-commerce Platform
============================================
Comprehensive product catalog with categories, variants, and inventory.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.base.core.system.models import (
    OwlsBaseModel, SlugModel, TimeStampedModel, OrderedModel
)


class Category(OwlsBaseModel, SlugModel, OrderedModel):
    """
    Product category with hierarchical structure.
    """
    name = models.CharField(_('Name'), max_length=255)
    description = models.TextField(_('Description'), blank=True)
    image = models.ImageField(
        _('Image'),
        upload_to='categories/%Y/%m/',
        blank=True,
        null=True
    )
    icon = models.CharField(_('Icon class'), max_length=100, blank=True)
    
    # Hierarchical structure
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True
    )
    level = models.PositiveIntegerField(_('Level'), default=0)
    path = models.CharField(_('Path'), max_length=500, blank=True)  # For breadcrumbs
    
    # SEO
    meta_title = models.CharField(_('Meta title'), max_length=255, blank=True)
    meta_description = models.TextField(_('Meta description'), blank=True)
    
    # Stats
    product_count = models.PositiveIntegerField(_('Product count'), default=0)
    
    # Display settings
    is_featured = models.BooleanField(_('Featured'), default=False)
    show_in_menu = models.BooleanField(_('Show in menu'), default=True)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Update level and path
        if self.parent:
            self.level = self.parent.level + 1
            self.path = f'{self.parent.path}/{self.slug}' if self.parent.path else self.slug
        else:
            self.level = 0
            self.path = self.slug
        super().save(*args, **kwargs)

    @property
    def full_path(self):
        """Return full category path."""
        if self.parent:
            return f'{self.parent.full_path} > {self.name}'
        return self.name


class Brand(OwlsBaseModel, SlugModel):
    """
    Product brand.
    """
    name = models.CharField(_('Name'), max_length=255, unique=True)
    description = models.TextField(_('Description'), blank=True)
    logo = models.ImageField(
        _('Logo'),
        upload_to='brands/%Y/%m/',
        blank=True,
        null=True
    )
    website = models.URLField(_('Website'), blank=True)
    is_featured = models.BooleanField(_('Featured'), default=False)
    product_count = models.PositiveIntegerField(_('Product count'), default=0)

    class Meta:
        verbose_name = _('Brand')
        verbose_name_plural = _('Brands')
        ordering = ['name']

    def __str__(self):
        return self.name


class ProductAttribute(TimeStampedModel):
    """
    Product attribute definitions (e.g., Size, Color, Material).
    """
    name = models.CharField(_('Name'), max_length=255, unique=True)
    code = models.CharField(_('Code'), max_length=50, unique=True)
    attribute_type = models.CharField(
        _('Type'),
        max_length=20,
        choices=[
            ('text', _('Text')),
            ('number', _('Number')),
            ('color', _('Color')),
            ('select', _('Select')),
            ('multiselect', _('Multi-select')),
        ],
        default='text'
    )
    is_filterable = models.BooleanField(_('Filterable'), default=True)
    is_visible = models.BooleanField(_('Visible on product page'), default=True)
    order = models.PositiveIntegerField(_('Order'), default=0)

    class Meta:
        verbose_name = _('Product Attribute')
        verbose_name_plural = _('Product Attributes')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class ProductAttributeValue(TimeStampedModel):
    """
    Predefined values for product attributes.
    """
    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.CASCADE,
        related_name='values'
    )
    value = models.CharField(_('Value'), max_length=255)
    code = models.CharField(_('Code'), max_length=50)
    color_code = models.CharField(_('Color code'), max_length=10, blank=True)  # For color attributes
    image = models.ImageField(
        _('Image'),
        upload_to='attributes/%Y/%m/',
        blank=True,
        null=True
    )
    order = models.PositiveIntegerField(_('Order'), default=0)

    class Meta:
        verbose_name = _('Attribute Value')
        verbose_name_plural = _('Attribute Values')
        unique_together = ['attribute', 'code']
        ordering = ['order']

    def __str__(self):
        return f'{self.attribute.name}: {self.value}'


class Product(OwlsBaseModel, SlugModel):
    """
    Main product model.
    """
    
    class Status(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        PENDING = 'pending', _('Pending Review')
        PUBLISHED = 'published', _('Published')
        REJECTED = 'rejected', _('Rejected')
        OUT_OF_STOCK = 'out_of_stock', _('Out of Stock')
        DISCONTINUED = 'discontinued', _('Discontinued')
    
    class ProductType(models.TextChoices):
        SIMPLE = 'simple', _('Simple Product')
        VARIABLE = 'variable', _('Variable Product')
        DIGITAL = 'digital', _('Digital Product')
        SERVICE = 'service', _('Service')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Vendor
    vendor = models.ForeignKey(
        'vendors.Vendor',
        on_delete=models.CASCADE,
        related_name='products'
    )
    
    # Basic Info
    name = models.CharField(_('Name'), max_length=500)
    short_description = models.TextField(_('Short description'), max_length=500, blank=True)
    description = models.TextField(_('Description'))
    
    # SKU & Identification
    sku = models.CharField(
        _('SKU'),
        max_length=100,
        unique=True,
        db_index=True
    )
    barcode = models.CharField(_('Barcode'), max_length=100, blank=True)
    
    # Categorization
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products'
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        related_name='products',
        blank=True,
        null=True
    )
    tags = models.JSONField(_('Tags'), default=list, blank=True)
    
    # Product Type & Status
    product_type = models.CharField(
        _('Product type'),
        max_length=20,
        choices=ProductType.choices,
        default=ProductType.SIMPLE
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True
    )
    
    # Pricing
    price = models.DecimalField(
        _('Price'),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    compare_at_price = models.DecimalField(
        _('Compare at price'),
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_('Original price before discount')
    )
    cost_price = models.DecimalField(
        _('Cost price'),
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True
    )
    
    # Inventory (for simple products)
    track_inventory = models.BooleanField(_('Track inventory'), default=True)
    stock_quantity = models.IntegerField(_('Stock quantity'), default=0)
    low_stock_threshold = models.PositiveIntegerField(_('Low stock threshold'), default=5)
    allow_backorder = models.BooleanField(_('Allow backorder'), default=False)
    
    # Shipping
    weight = models.DecimalField(
        _('Weight (kg)'),
        max_digits=10,
        decimal_places=3,
        blank=True,
        null=True
    )
    length = models.DecimalField(
        _('Length (cm)'),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    width = models.DecimalField(
        _('Width (cm)'),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    height = models.DecimalField(
        _('Height (cm)'),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    requires_shipping = models.BooleanField(_('Requires shipping'), default=True)
    
    # SEO
    meta_title = models.CharField(_('Meta title'), max_length=255, blank=True)
    meta_description = models.TextField(_('Meta description'), blank=True)
    
    # Stats & Performance
    rating = models.DecimalField(
        _('Rating'),
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    review_count = models.PositiveIntegerField(_('Review count'), default=0)
    view_count = models.PositiveIntegerField(_('View count'), default=0)
    sold_count = models.PositiveIntegerField(_('Sold count'), default=0)
    wishlist_count = models.PositiveIntegerField(_('Wishlist count'), default=0)
    
    # Flags
    is_featured = models.BooleanField(_('Featured'), default=False)
    is_bestseller = models.BooleanField(_('Bestseller'), default=False)
    is_new_arrival = models.BooleanField(_('New arrival'), default=False)
    is_taxable = models.BooleanField(_('Taxable'), default=True)
    
    # Timestamps
    published_at = models.DateTimeField(_('Published at'), blank=True, null=True)

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'is_active']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['vendor', 'status']),
            models.Index(fields=['price']),
            models.Index(fields=['rating']),
            models.Index(fields=['-sold_count']),
        ]
        # Database-level constraint to prevent negative stock (Race Condition Protection)
        constraints = [
            models.CheckConstraint(
                check=models.Q(stock_quantity__gte=0),
                name='product_stock_quantity_non_negative'
            ),
        ]

    def __str__(self):
        return self.name

    @property
    def is_on_sale(self):
        """Check if product is on sale."""
        return self.compare_at_price and self.compare_at_price > self.price

    @property
    def discount_percentage(self):
        """Calculate discount percentage."""
        if self.is_on_sale:
            return int(((self.compare_at_price - self.price) / self.compare_at_price) * 100)
        return 0

    @property
    def is_in_stock(self):
        """Check if product is in stock."""
        if not self.track_inventory:
            return True
        return self.stock_quantity > 0 or self.allow_backorder

    @property
    def effective_price(self):
        """Return the current selling price."""
        return self.price


class ProductImage(TimeStampedModel, OrderedModel):
    """
    Product images.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        _('Image'),
        upload_to='products/%Y/%m/'
    )
    alt_text = models.CharField(_('Alt text'), max_length=255, blank=True)
    is_primary = models.BooleanField(_('Primary image'), default=False)

    class Meta:
        verbose_name = _('Product Image')
        verbose_name_plural = _('Product Images')
        ordering = ['-is_primary', 'order']

    def __str__(self):
        return f'{self.product.name} - Image {self.order}'

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductVariant(TimeStampedModel):
    """
    Product variants (combinations of attributes).
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants'
    )
    name = models.CharField(_('Variant name'), max_length=255)
    sku = models.CharField(_('SKU'), max_length=100, unique=True)
    
    # Pricing
    price = models.DecimalField(
        _('Price'),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    compare_at_price = models.DecimalField(
        _('Compare at price'),
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True
    )
    
    # Inventory
    stock_quantity = models.IntegerField(_('Stock quantity'), default=0)
    
    # Attributes (stored as JSON for flexibility)
    attributes = models.JSONField(_('Attributes'), default=dict)
    
    # Image
    image = models.ImageField(
        _('Image'),
        upload_to='products/variants/%Y/%m/',
        blank=True,
        null=True
    )
    
    # Status
    is_active = models.BooleanField(_('Active'), default=True)

    class Meta:
        verbose_name = _('Product Variant')
        verbose_name_plural = _('Product Variants')
        # Database-level constraint to prevent negative stock (Race Condition Protection)
        constraints = [
            models.CheckConstraint(
                check=models.Q(stock_quantity__gte=0),
                name='variant_stock_quantity_non_negative'
            ),
        ]

    def __str__(self):
        return f'{self.product.name} - {self.name}'


class ProductAttributeMapping(TimeStampedModel):
    """
    Link products to their attributes.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='attribute_mappings'
    )
    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.CASCADE
    )
    value = models.ForeignKey(
        ProductAttributeValue,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    custom_value = models.CharField(_('Custom value'), max_length=255, blank=True)

    class Meta:
        verbose_name = _('Product Attribute Mapping')
        verbose_name_plural = _('Product Attribute Mappings')
        unique_together = ['product', 'attribute', 'value']

    def __str__(self):
        return f'{self.product.name} - {self.attribute.name}'
