"""
Vendor Models for Owls E-commerce Platform
==========================================
Comprehensive vendor/seller management system.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.base.core.system.models import OwlsBaseModel, SlugModel, TimeStampedModel


class Vendor(OwlsBaseModel, SlugModel):
    """
    Vendor/Seller model for marketplace.
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending Approval')
        APPROVED = 'approved', _('Approved')
        SUSPENDED = 'suspended', _('Suspended')
        REJECTED = 'rejected', _('Rejected')
        CLOSED = 'closed', _('Closed')
    
    class Type(models.TextChoices):
        INDIVIDUAL = 'individual', _('Individual Seller')
        BUSINESS = 'business', _('Business')
        BRAND = 'brand', _('Official Brand Store')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Owner
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='vendor_profile'
    )
    
    # Basic Info
    store_name = models.CharField(_('Store name'), max_length=255, unique=True)
    description = models.TextField(_('Description'), blank=True)
    logo = models.ImageField(
        _('Logo'),
        upload_to='vendors/logos/%Y/%m/',
        blank=True,
        null=True
    )
    banner = models.ImageField(
        _('Banner'),
        upload_to='vendors/banners/%Y/%m/',
        blank=True,
        null=True
    )
    
    # Contact Info
    email = models.EmailField(_('Business email'))
    phone = models.CharField(_('Phone'), max_length=20)
    website = models.URLField(_('Website'), blank=True)
    
    # Business Address
    address = models.CharField(_('Address'), max_length=500)
    ward = models.CharField(_('Ward'), max_length=100, blank=True)
    district = models.CharField(_('District'), max_length=100)
    city = models.CharField(_('City'), max_length=100)
    country = models.CharField(_('Country'), max_length=100, default='Vietnam')
    
    # Business Info
    vendor_type = models.CharField(
        _('Vendor type'),
        max_length=20,
        choices=Type.choices,
        default=Type.INDIVIDUAL
    )
    business_license = models.CharField(
        _('Business license number'),
        max_length=100,
        blank=True
    )
    tax_id = models.CharField(_('Tax ID'), max_length=50, blank=True)
    
    # Status & Verification
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    is_verified = models.BooleanField(_('Verified'), default=False)
    verified_at = models.DateTimeField(_('Verified at'), blank=True, null=True)
    
    # Commission & Financial
    commission_rate = models.DecimalField(
        _('Commission rate'),
        max_digits=5,
        decimal_places=4,
        default=0.15,  # 15% default
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    
    # Rating & Performance
    rating = models.DecimalField(
        _('Rating'),
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    total_reviews = models.PositiveIntegerField(_('Total reviews'), default=0)
    total_products = models.PositiveIntegerField(_('Total products'), default=0)
    total_orders = models.PositiveIntegerField(_('Total orders'), default=0)
    total_sales = models.DecimalField(
        _('Total sales'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    
    # Settings
    auto_confirm_orders = models.BooleanField(
        _('Auto confirm orders'),
        default=False
    )
    return_policy = models.TextField(_('Return policy'), blank=True)
    shipping_policy = models.TextField(_('Shipping policy'), blank=True)
    
    # Timestamps
    approved_at = models.DateTimeField(_('Approved at'), blank=True, null=True)

    class Meta:
        verbose_name = _('Vendor')
        verbose_name_plural = _('Vendors')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'is_active']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return self.store_name

    @property
    def is_approved(self):
        return self.status == self.Status.APPROVED

    def update_stats(self):
        """Update vendor statistics."""
        from apps.business.commerce.products.models import Product
        from apps.business.commerce.orders.models import OrderItem
        
        self.total_products = Product.objects.filter(vendor=self, is_active=True).count()
        # Add more stats calculation
        self.save(update_fields=['total_products', 'updated_at'])


class VendorDocument(TimeStampedModel):
    """
    Vendor verification documents.
    """
    
    class DocumentType(models.TextChoices):
        BUSINESS_LICENSE = 'business_license', _('Business License')
        TAX_CERTIFICATE = 'tax_certificate', _('Tax Certificate')
        ID_CARD = 'id_card', _('ID Card')
        BANK_STATEMENT = 'bank_statement', _('Bank Statement')
        OTHER = 'other', _('Other')

    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(
        _('Document type'),
        max_length=30,
        choices=DocumentType.choices
    )
    title = models.CharField(_('Title'), max_length=255)
    file = models.FileField(
        _('File'),
        upload_to='vendors/documents/%Y/%m/'
    )
    is_verified = models.BooleanField(_('Verified'), default=False)
    verified_at = models.DateTimeField(_('Verified at'), blank=True, null=True)
    notes = models.TextField(_('Notes'), blank=True)

    class Meta:
        verbose_name = _('Vendor Document')
        verbose_name_plural = _('Vendor Documents')

    def __str__(self):
        return f'{self.vendor.store_name} - {self.title}'


class VendorBankAccount(TimeStampedModel):
    """
    Vendor bank account for payouts.
    """
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='bank_accounts'
    )
    bank_name = models.CharField(_('Bank name'), max_length=255)
    account_name = models.CharField(_('Account name'), max_length=255)
    account_number = models.CharField(_('Account number'), max_length=50)
    branch = models.CharField(_('Branch'), max_length=255, blank=True)
    swift_code = models.CharField(_('SWIFT code'), max_length=20, blank=True)
    is_default = models.BooleanField(_('Default account'), default=False)
    is_verified = models.BooleanField(_('Verified'), default=False)

    class Meta:
        verbose_name = _('Vendor Bank Account')
        verbose_name_plural = _('Vendor Bank Accounts')

    def __str__(self):
        return f'{self.vendor.store_name} - {self.bank_name}'

    def save(self, *args, **kwargs):
        if self.is_default:
            VendorBankAccount.objects.filter(
                vendor=self.vendor,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class VendorPayout(TimeStampedModel):
    """
    Vendor payout records.
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        PROCESSING = 'processing', _('Processing')
        COMPLETED = 'completed', _('Completed')
        FAILED = 'failed', _('Failed')
        CANCELLED = 'cancelled', _('Cancelled')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.PROTECT,
        related_name='payouts'
    )
    bank_account = models.ForeignKey(
        VendorBankAccount,
        on_delete=models.PROTECT,
        related_name='payouts'
    )
    amount = models.DecimalField(
        _('Amount'),
        max_digits=15,
        decimal_places=2
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
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    reference = models.CharField(_('Reference'), max_length=255, blank=True)
    notes = models.TextField(_('Notes'), blank=True)
    processed_at = models.DateTimeField(_('Processed at'), blank=True, null=True)

    class Meta:
        verbose_name = _('Vendor Payout')
        verbose_name_plural = _('Vendor Payouts')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.vendor.store_name} - {self.amount}'
