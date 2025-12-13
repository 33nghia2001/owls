"""
Reviews Models for Owls E-commerce Platform
===========================================
Product reviews and ratings system.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.base.core.system.models import TimeStampedModel


class Review(TimeStampedModel):
    """
    Product review/rating model.
    Users can review products they have purchased.
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending Approval')
        APPROVED = 'approved', _('Approved')
        REJECTED = 'rejected', _('Rejected')
        FLAGGED = 'flagged', _('Flagged for Review')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        related_name='reviews',
        blank=True,
        null=True,
        help_text=_('Order associated with this review')
    )
    
    # Rating (1-5 stars)
    rating = models.PositiveSmallIntegerField(
        _('Rating'),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Review content
    title = models.CharField(_('Title'), max_length=255, blank=True)
    content = models.TextField(_('Review content'))
    
    # Detailed ratings (optional)
    quality_rating = models.PositiveSmallIntegerField(
        _('Quality rating'),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True,
        null=True
    )
    value_rating = models.PositiveSmallIntegerField(
        _('Value for money rating'),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True,
        null=True
    )
    shipping_rating = models.PositiveSmallIntegerField(
        _('Shipping rating'),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True,
        null=True
    )
    
    # Pros and cons
    pros = models.JSONField(_('Pros'), default=list, blank=True)
    cons = models.JSONField(_('Cons'), default=list, blank=True)
    
    # Status
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    
    # Verified purchase
    is_verified_purchase = models.BooleanField(
        _('Verified purchase'),
        default=False,
        help_text=_('User has actually purchased this product')
    )
    
    # Helpfulness
    helpful_count = models.PositiveIntegerField(_('Helpful votes'), default=0)
    not_helpful_count = models.PositiveIntegerField(_('Not helpful votes'), default=0)
    
    # Admin fields
    admin_response = models.TextField(_('Admin/Vendor response'), blank=True)
    admin_response_at = models.DateTimeField(
        _('Response date'),
        blank=True,
        null=True
    )
    moderation_note = models.TextField(_('Moderation note'), blank=True)

    class Meta:
        app_label = 'reviews'
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')
        ordering = ['-created_at']
        # One review per user per product
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.email}'s review of {self.product.name}"

    @property
    def is_approved(self):
        """Check if review is approved."""
        return self.status == self.Status.APPROVED

    def approve(self):
        """Approve this review."""
        self.status = self.Status.APPROVED
        self.save(update_fields=['status', 'updated_at'])
        # Update product rating
        self.product.update_rating()

    def reject(self, note=''):
        """Reject this review."""
        self.status = self.Status.REJECTED
        self.moderation_note = note
        self.save(update_fields=['status', 'moderation_note', 'updated_at'])


class ReviewImage(TimeStampedModel):
    """
    Images attached to reviews.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        _('Image'),
        upload_to='reviews/%Y/%m/'
    )
    caption = models.CharField(_('Caption'), max_length=255, blank=True)
    order = models.PositiveIntegerField(_('Order'), default=0)

    class Meta:
        app_label = 'reviews'
        verbose_name = _('Review Image')
        verbose_name_plural = _('Review Images')
        ordering = ['order']

    def __str__(self):
        return f"Image for review {self.review.id}"


class ReviewVote(TimeStampedModel):
    """
    Track user votes on review helpfulness.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='review_votes'
    )
    is_helpful = models.BooleanField(_('Is helpful'))

    class Meta:
        app_label = 'reviews'
        verbose_name = _('Review Vote')
        verbose_name_plural = _('Review Votes')
        unique_together = ['review', 'user']

    def __str__(self):
        vote_type = 'helpful' if self.is_helpful else 'not helpful'
        return f"{self.user.email} voted {vote_type} on review {self.review.id}"

    def save(self, *args, **kwargs):
        # Check if this is an update
        is_update = self.pk is not None
        old_vote = None
        
        if is_update:
            try:
                old_vote = ReviewVote.objects.get(pk=self.pk)
            except ReviewVote.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Update review vote counts
        if is_update and old_vote:
            # Changing vote
            if old_vote.is_helpful != self.is_helpful:
                if self.is_helpful:
                    self.review.helpful_count += 1
                    self.review.not_helpful_count -= 1
                else:
                    self.review.helpful_count -= 1
                    self.review.not_helpful_count += 1
                self.review.save(update_fields=['helpful_count', 'not_helpful_count'])
        else:
            # New vote
            if self.is_helpful:
                self.review.helpful_count += 1
            else:
                self.review.not_helpful_count += 1
            self.review.save(update_fields=['helpful_count', 'not_helpful_count'])
