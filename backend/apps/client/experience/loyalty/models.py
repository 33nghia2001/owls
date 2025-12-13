"""
Loyalty Models for Owls E-commerce Platform
===========================================
Customer loyalty points and rewards system.
"""

import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from apps.base.core.system.models import TimeStampedModel


class LoyaltyTier(TimeStampedModel):
    """
    Loyalty membership tiers (Bronze, Silver, Gold, Platinum, etc.)
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(_('Name'), max_length=100, unique=True)
    code = models.CharField(_('Code'), max_length=50, unique=True)
    description = models.TextField(_('Description'), blank=True)
    
    # Tier thresholds
    min_points = models.PositiveIntegerField(
        _('Minimum points required'),
        default=0
    )
    min_spent = models.DecimalField(
        _('Minimum total spent'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    
    # Benefits
    points_multiplier = models.DecimalField(
        _('Points multiplier'),
        max_digits=4,
        decimal_places=2,
        default=1.00,
        help_text=_('Multiply earned points (e.g., 1.5 = 50% bonus)')
    )
    discount_percentage = models.DecimalField(
        _('Discount percentage'),
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text=_('Automatic discount for this tier')
    )
    free_shipping = models.BooleanField(
        _('Free shipping'),
        default=False
    )
    priority_support = models.BooleanField(
        _('Priority support'),
        default=False
    )
    
    # Display
    icon = models.CharField(_('Icon class'), max_length=100, blank=True)
    color = models.CharField(_('Color code'), max_length=20, blank=True)
    badge_image = models.ImageField(
        _('Badge image'),
        upload_to='loyalty/tiers/',
        blank=True,
        null=True
    )
    
    order = models.PositiveIntegerField(_('Display order'), default=0)
    is_active = models.BooleanField(_('Active'), default=True)

    class Meta:
        app_label = 'loyalty'
        verbose_name = _('Loyalty Tier')
        verbose_name_plural = _('Loyalty Tiers')
        ordering = ['order', 'min_points']

    def __str__(self):
        return self.name


class LoyaltyAccount(TimeStampedModel):
    """
    User's loyalty account with points balance.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='loyalty_account'
    )
    
    # Points
    points_balance = models.PositiveIntegerField(
        _('Current points'),
        default=0
    )
    points_earned_total = models.PositiveIntegerField(
        _('Total points earned'),
        default=0
    )
    points_spent_total = models.PositiveIntegerField(
        _('Total points spent'),
        default=0
    )
    points_expired_total = models.PositiveIntegerField(
        _('Total points expired'),
        default=0
    )
    
    # Tier
    tier = models.ForeignKey(
        LoyaltyTier,
        on_delete=models.SET_NULL,
        related_name='accounts',
        blank=True,
        null=True
    )
    tier_qualified_at = models.DateTimeField(
        _('Tier qualified at'),
        blank=True,
        null=True
    )
    
    # Lifetime stats
    total_orders = models.PositiveIntegerField(
        _('Total orders'),
        default=0
    )
    total_spent = models.DecimalField(
        _('Total amount spent'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    
    # Status
    is_active = models.BooleanField(_('Active'), default=True)

    class Meta:
        app_label = 'loyalty'
        verbose_name = _('Loyalty Account')
        verbose_name_plural = _('Loyalty Accounts')

    def __str__(self):
        return f"{self.user.email}'s Loyalty Account"

    def add_points(self, points, description='', order=None, expires_at=None):
        """
        Add points to account.
        
        Args:
            points: Number of points to add
            description: Transaction description
            order: Related order (optional)
            expires_at: Expiry date for these points
        """
        if points <= 0:
            return None
        
        # Apply tier multiplier
        if self.tier and self.tier.points_multiplier > 1:
            points = int(points * self.tier.points_multiplier)
        
        # Set default expiry (1 year)
        if not expires_at:
            expires_at = timezone.now() + timezone.timedelta(days=365)
        
        # Create transaction
        transaction = PointTransaction.objects.create(
            account=self,
            transaction_type=PointTransaction.TransactionType.EARNED,
            points=points,
            description=description,
            order=order,
            expires_at=expires_at
        )
        
        # Update balance
        self.points_balance += points
        self.points_earned_total += points
        self.save(update_fields=['points_balance', 'points_earned_total', 'updated_at'])
        
        # Check tier upgrade
        self._check_tier_upgrade()
        
        return transaction

    def spend_points(self, points, description='', order=None):
        """
        Spend points from account.
        
        Args:
            points: Number of points to spend
            description: Transaction description
            order: Related order (optional)
        """
        if points <= 0 or points > self.points_balance:
            return None
        
        # Create transaction
        transaction = PointTransaction.objects.create(
            account=self,
            transaction_type=PointTransaction.TransactionType.SPENT,
            points=-points,
            description=description,
            order=order
        )
        
        # Update balance
        self.points_balance -= points
        self.points_spent_total += points
        self.save(update_fields=['points_balance', 'points_spent_total', 'updated_at'])
        
        return transaction

    def _check_tier_upgrade(self):
        """Check and upgrade tier if eligible."""
        eligible_tier = LoyaltyTier.objects.filter(
            is_active=True,
            min_points__lte=self.points_earned_total
        ).order_by('-min_points').first()
        
        if eligible_tier and (not self.tier or eligible_tier.min_points > self.tier.min_points):
            self.tier = eligible_tier
            self.tier_qualified_at = timezone.now()
            self.save(update_fields=['tier', 'tier_qualified_at', 'updated_at'])

    def get_points_value(self):
        """Convert points to currency value."""
        owls_config = getattr(settings, 'OWLS_CONFIG', {})
        points_per_vnd = Decimal(str(owls_config.get('POINTS_PER_VND', 0.001)))
        if points_per_vnd > 0:
            return Decimal(self.points_balance) / points_per_vnd
        return Decimal('0')


class PointTransaction(TimeStampedModel):
    """
    Individual point transaction record.
    """
    
    class TransactionType(models.TextChoices):
        EARNED = 'earned', _('Earned')
        SPENT = 'spent', _('Spent')
        EXPIRED = 'expired', _('Expired')
        ADJUSTED = 'adjusted', _('Adjusted')
        BONUS = 'bonus', _('Bonus')
        REFUND = 'refund', _('Refund')
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    account = models.ForeignKey(
        LoyaltyAccount,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    transaction_type = models.CharField(
        _('Type'),
        max_length=20,
        choices=TransactionType.choices
    )
    points = models.IntegerField(
        _('Points'),
        help_text=_('Positive for earned, negative for spent')
    )
    description = models.CharField(_('Description'), max_length=255)
    
    # Related objects
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        related_name='point_transactions',
        blank=True,
        null=True
    )
    
    # Expiry (for earned points)
    expires_at = models.DateTimeField(
        _('Expires at'),
        blank=True,
        null=True
    )
    is_expired = models.BooleanField(_('Is expired'), default=False)

    class Meta:
        app_label = 'loyalty'
        verbose_name = _('Point Transaction')
        verbose_name_plural = _('Point Transactions')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type}: {self.points} points"


class Reward(TimeStampedModel):
    """
    Redeemable rewards in loyalty program.
    """
    
    class RewardType(models.TextChoices):
        DISCOUNT = 'discount', _('Discount Voucher')
        PRODUCT = 'product', _('Free Product')
        SHIPPING = 'shipping', _('Free Shipping')
        GIFT_CARD = 'gift_card', _('Gift Card')
        EXPERIENCE = 'experience', _('Experience')
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(_('Name'), max_length=255)
    description = models.TextField(_('Description'))
    reward_type = models.CharField(
        _('Type'),
        max_length=20,
        choices=RewardType.choices
    )
    
    # Cost
    points_required = models.PositiveIntegerField(_('Points required'))
    
    # Value
    discount_value = models.DecimalField(
        _('Discount value'),
        max_digits=15,
        decimal_places=2,
        default=0
    )
    discount_percentage = models.DecimalField(
        _('Discount percentage'),
        max_digits=5,
        decimal_places=2,
        default=0
    )
    
    # For product rewards
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    
    # Limits
    min_tier = models.ForeignKey(
        LoyaltyTier,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_('Minimum tier required to redeem')
    )
    quantity_available = models.PositiveIntegerField(
        _('Quantity available'),
        blank=True,
        null=True
    )
    quantity_redeemed = models.PositiveIntegerField(
        _('Quantity redeemed'),
        default=0
    )
    redemption_limit_per_user = models.PositiveIntegerField(
        _('Limit per user'),
        default=1
    )
    
    # Validity
    starts_at = models.DateTimeField(_('Starts at'), default=timezone.now)
    expires_at = models.DateTimeField(_('Expires at'), blank=True, null=True)
    
    # Display
    image = models.ImageField(
        _('Image'),
        upload_to='loyalty/rewards/',
        blank=True,
        null=True
    )
    is_featured = models.BooleanField(_('Featured'), default=False)
    is_active = models.BooleanField(_('Active'), default=True)

    class Meta:
        app_label = 'loyalty'
        verbose_name = _('Reward')
        verbose_name_plural = _('Rewards')
        ordering = ['points_required']

    def __str__(self):
        return f"{self.name} ({self.points_required} points)"

    @property
    def is_available(self):
        """Check if reward is currently available."""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.starts_at > now:
            return False
        if self.expires_at and self.expires_at < now:
            return False
        if self.quantity_available and self.quantity_redeemed >= self.quantity_available:
            return False
        return True


class RewardRedemption(TimeStampedModel):
    """
    Record of reward redemptions.
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        COMPLETED = 'completed', _('Completed')
        CANCELLED = 'cancelled', _('Cancelled')
        EXPIRED = 'expired', _('Expired')
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    account = models.ForeignKey(
        LoyaltyAccount,
        on_delete=models.CASCADE,
        related_name='redemptions'
    )
    reward = models.ForeignKey(
        Reward,
        on_delete=models.PROTECT,
        related_name='redemptions'
    )
    
    points_spent = models.PositiveIntegerField(_('Points spent'))
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    # Voucher code generated
    voucher_code = models.CharField(
        _('Voucher code'),
        max_length=50,
        unique=True,
        blank=True,
        null=True
    )
    
    # Usage
    used_at = models.DateTimeField(_('Used at'), blank=True, null=True)
    used_on_order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    
    expires_at = models.DateTimeField(_('Expires at'), blank=True, null=True)

    class Meta:
        app_label = 'loyalty'
        verbose_name = _('Reward Redemption')
        verbose_name_plural = _('Reward Redemptions')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.account.user.email} redeemed {self.reward.name}"

    def save(self, *args, **kwargs):
        # Generate voucher code
        if not self.voucher_code:
            import secrets
            self.voucher_code = f"RWD-{secrets.token_hex(6).upper()}"
        
        # Set expiry (30 days)
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=30)
        
        super().save(*args, **kwargs)
