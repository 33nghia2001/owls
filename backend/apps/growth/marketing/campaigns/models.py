"""
Marketing Campaigns Models for Owls E-commerce Platform
========================================================
Campaign management for promotions, sales, and marketing activities.
"""

import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Campaign(models.Model):
    """
    Marketing campaign for promotions and sales.
    
    Campaigns can have multiple channels, target audiences, and
    track performance metrics.
    """
    
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        SCHEDULED = 'scheduled', 'Scheduled'
        ACTIVE = 'active', 'Active'
        PAUSED = 'paused', 'Paused'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
    
    class CampaignType(models.TextChoices):
        FLASH_SALE = 'flash_sale', 'Flash Sale'
        SEASONAL = 'seasonal', 'Seasonal Promotion'
        CLEARANCE = 'clearance', 'Clearance Sale'
        NEW_ARRIVAL = 'new_arrival', 'New Arrival'
        HOLIDAY = 'holiday', 'Holiday Special'
        LOYALTY = 'loyalty', 'Loyalty Reward'
        REFERRAL = 'referral', 'Referral Campaign'
        EMAIL = 'email', 'Email Campaign'
        SOCIAL = 'social', 'Social Media'
        OTHER = 'other', 'Other'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic info
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    
    # Type and status
    campaign_type = models.CharField(
        max_length=30,
        choices=CampaignType.choices,
        default=CampaignType.OTHER,
        db_index=True
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True
    )
    
    # Schedule
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Target audience
    target_audience = models.JSONField(
        default=dict,
        blank=True,
        help_text='Target audience criteria (segments, locations, etc.)'
    )
    
    # Budget
    budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Campaign budget in VND'
    )
    spent = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Amount spent so far'
    )
    
    # Discount settings (for sales campaigns)
    discount_type = models.CharField(
        max_length=20,
        choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Amount')],
        blank=True
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    max_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Maximum discount amount (for percentage discounts)'
    )
    
    # Associated items
    products = models.ManyToManyField(
        'products.Product',
        blank=True,
        related_name='campaigns'
    )
    categories = models.ManyToManyField(
        'products.Category',
        blank=True,
        related_name='campaigns'
    )
    
    # Associated coupon (optional)
    coupon_code = models.CharField(max_length=50, blank=True)
    
    # Media
    banner_image = models.URLField(blank=True)
    thumbnail_image = models.URLField(blank=True)
    
    # Visibility
    is_featured = models.BooleanField(default=False, db_index=True)
    is_public = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=0, help_text='Higher = more prominent')
    
    # Tracking
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_campaigns'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'campaigns'
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['status', 'start_date', 'end_date']),
            models.Index(fields=['campaign_type', 'is_featured']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def is_active(self):
        """Check if campaign is currently active."""
        now = timezone.now()
        return (
            self.status == self.Status.ACTIVE and
            self.start_date <= now <= self.end_date
        )
    
    @property
    def is_upcoming(self):
        """Check if campaign is scheduled for future."""
        return self.start_date > timezone.now()
    
    @property
    def is_expired(self):
        """Check if campaign has ended."""
        return self.end_date < timezone.now()
    
    @property
    def days_remaining(self):
        """Days until campaign ends."""
        if self.is_expired:
            return 0
        delta = self.end_date - timezone.now()
        return max(0, delta.days)
    
    def activate(self):
        """Activate the campaign."""
        self.status = self.Status.ACTIVE
        self.save(update_fields=['status', 'updated_at'])
    
    def pause(self):
        """Pause the campaign."""
        self.status = self.Status.PAUSED
        self.save(update_fields=['status', 'updated_at'])
    
    def complete(self):
        """Mark campaign as completed."""
        self.status = self.Status.COMPLETED
        self.save(update_fields=['status', 'updated_at'])


class CampaignMetrics(models.Model):
    """
    Track campaign performance metrics.
    
    Updated periodically to track views, clicks, conversions, etc.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.OneToOneField(
        Campaign,
        on_delete=models.CASCADE,
        related_name='metrics'
    )
    
    # Engagement metrics
    impressions = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    unique_visitors = models.PositiveIntegerField(default=0)
    
    # Conversion metrics
    orders = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00')
    )
    discount_given = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Calculated metrics
    @property
    def click_through_rate(self):
        """CTR percentage."""
        if self.impressions == 0:
            return 0
        return round((self.clicks / self.impressions) * 100, 2)
    
    @property
    def conversion_rate(self):
        """Conversion rate percentage."""
        if self.clicks == 0:
            return 0
        return round((self.orders / self.clicks) * 100, 2)
    
    @property
    def average_order_value(self):
        """Average order value."""
        if self.orders == 0:
            return Decimal('0.00')
        return self.revenue / self.orders
    
    @property
    def roi(self):
        """Return on investment."""
        if self.campaign.spent == 0:
            return 0
        return round(((self.revenue - self.campaign.spent) / self.campaign.spent) * 100, 2)
    
    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'campaign_metrics'
        verbose_name_plural = 'Campaign Metrics'
    
    def __str__(self):
        return f'Metrics for {self.campaign.name}'
    
    def increment_impressions(self, count=1):
        """Increment impressions."""
        self.impressions += count
        self.save(update_fields=['impressions', 'updated_at'])
    
    def increment_clicks(self, count=1):
        """Increment clicks."""
        self.clicks += count
        self.save(update_fields=['clicks', 'updated_at'])
    
    def record_order(self, order_amount: Decimal, discount_amount: Decimal = Decimal('0')):
        """Record an order conversion."""
        self.orders += 1
        self.revenue += order_amount
        self.discount_given += discount_amount
        self.save(update_fields=['orders', 'revenue', 'discount_given', 'updated_at'])


class CampaignChannel(models.Model):
    """
    Marketing channels for campaigns.
    """
    
    class ChannelType(models.TextChoices):
        EMAIL = 'email', 'Email'
        SMS = 'sms', 'SMS'
        PUSH = 'push', 'Push Notification'
        FACEBOOK = 'facebook', 'Facebook'
        GOOGLE = 'google', 'Google Ads'
        INSTAGRAM = 'instagram', 'Instagram'
        TIKTOK = 'tiktok', 'TikTok'
        ZALO = 'zalo', 'Zalo'
        WEBSITE = 'website', 'Website Banner'
        APP = 'app', 'In-App'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='channels'
    )
    
    channel_type = models.CharField(
        max_length=20,
        choices=ChannelType.choices
    )
    
    # Channel-specific settings
    settings = models.JSONField(
        default=dict,
        blank=True,
        help_text='Channel-specific configuration'
    )
    
    # Channel budget (portion of campaign budget)
    budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    spent = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Channel-specific metrics
    impressions = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    conversions = models.PositiveIntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'campaign_channels'
        unique_together = ['campaign', 'channel_type']
    
    def __str__(self):
        return f'{self.campaign.name} - {self.channel_type}'
