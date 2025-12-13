"""
Base Models for Owls E-commerce Platform
=========================================
Abstract base classes that provide common functionality for all models.
"""

import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """
    Abstract base model with created/updated timestamps.
    All models should inherit from this for audit purposes.
    """
    created_at = models.DateTimeField(
        _('Created at'),
        auto_now_add=True,
        db_index=True
    )
    updated_at = models.DateTimeField(
        _('Updated at'),
        auto_now=True
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']


class UUIDModel(models.Model):
    """
    Abstract model that uses UUID as primary key.
    Good for security-sensitive models to avoid sequential ID exposure.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    """Manager that excludes soft-deleted objects by default."""
    
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
    
    def with_deleted(self):
        """Include deleted objects in queryset."""
        return super().get_queryset()
    
    def only_deleted(self):
        """Return only deleted objects."""
        return super().get_queryset().filter(is_deleted=True)


class SoftDeleteModel(models.Model):
    """
    Abstract model for soft deletion.
    Objects are marked as deleted instead of being removed from database.
    """
    is_deleted = models.BooleanField(
        _('Is deleted'),
        default=False,
        db_index=True
    )
    deleted_at = models.DateTimeField(
        _('Deleted at'),
        null=True,
        blank=True
    )
    
    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Manager that includes deleted objects

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, hard_delete=False):
        """Soft delete by default, hard delete if specified."""
        if hard_delete:
            return super().delete(using=using, keep_parents=keep_parents)
        
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

    def restore(self):
        """Restore a soft-deleted object."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])


class ActiveManager(models.Manager):
    """Manager that returns only active objects."""
    
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class StatusModel(models.Model):
    """
    Abstract model for objects that can be activated/deactivated.
    """
    is_active = models.BooleanField(
        _('Is active'),
        default=True,
        db_index=True
    )
    
    objects = models.Manager()
    active_objects = ActiveManager()

    class Meta:
        abstract = True

    def activate(self):
        """Activate the object."""
        self.is_active = True
        self.save(update_fields=['is_active', 'updated_at'])

    def deactivate(self):
        """Deactivate the object."""
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])


class SlugModel(models.Model):
    """
    Abstract model with slug field for SEO-friendly URLs.
    """
    slug = models.SlugField(
        _('Slug'),
        max_length=255,
        unique=True,
        db_index=True,
        help_text=_('URL-friendly identifier')
    )

    class Meta:
        abstract = True


class OrderedModel(models.Model):
    """
    Abstract model for objects that need ordering.
    """
    order = models.PositiveIntegerField(
        _('Order'),
        default=0,
        db_index=True
    )

    class Meta:
        abstract = True
        ordering = ['order']


class MetaDataModel(models.Model):
    """
    Abstract model for storing additional metadata as JSON.
    Useful for flexible, schema-less data.
    """
    metadata = models.JSONField(
        _('Metadata'),
        default=dict,
        blank=True
    )

    class Meta:
        abstract = True

    def get_meta(self, key, default=None):
        """Get a value from metadata."""
        return self.metadata.get(key, default)

    def set_meta(self, key, value):
        """Set a value in metadata."""
        self.metadata[key] = value
        self.save(update_fields=['metadata', 'updated_at'])


class OwlsBaseModel(TimeStampedModel, SoftDeleteModel, StatusModel, MetaDataModel):
    """
    Complete base model combining all common functionality.
    Use this for most business models in Owls platform.
    """

    class Meta:
        abstract = True


class OwlsUUIDModel(UUIDModel, OwlsBaseModel):
    """
    Base model with UUID primary key.
    Use for security-sensitive models like Users, Orders, Payments.
    """

    class Meta:
        abstract = True
