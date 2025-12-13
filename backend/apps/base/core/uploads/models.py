"""
Upload Models for Owls E-commerce Platform
==========================================
Centralized file upload management with metadata tracking.
"""

import os
import uuid
from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from .storage import get_upload_path


def upload_to_path(instance, filename):
    """Generate upload path based on upload type."""
    folder = instance.upload_type or 'general'
    return get_upload_path(instance, filename, folder)


class Upload(models.Model):
    """
    Centralized upload model to track all uploaded files.
    
    Benefits:
    - Track upload history and metadata
    - Easy cleanup of orphaned files
    - Centralized validation and processing
    - Analytics on storage usage
    """
    
    class UploadType(models.TextChoices):
        PRODUCT_IMAGE = 'products', 'Product Image'
        USER_AVATAR = 'avatars', 'User Avatar'
        VENDOR_LOGO = 'vendors/logos', 'Vendor Logo'
        VENDOR_DOCUMENT = 'vendors/documents', 'Vendor Document'
        CATEGORY_IMAGE = 'categories', 'Category Image'
        BANNER_IMAGE = 'banners', 'Banner Image'
        BLOG_IMAGE = 'blog', 'Blog Image'
        DOCUMENT = 'documents', 'Document'
        OTHER = 'other', 'Other'
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # File info
    file = models.FileField(
        upload_to=upload_to_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg',  # Images
                    'pdf', 'doc', 'docx', 'xls', 'xlsx',  # Documents
                    'mp4', 'webm', 'mov',  # Videos
                ]
            )
        ]
    )
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text='File size in bytes')
    content_type = models.CharField(max_length=100)
    
    # Categorization
    upload_type = models.CharField(
        max_length=50,
        choices=UploadType.choices,
        default=UploadType.OTHER,
        db_index=True
    )
    
    # Processing status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    # Image metadata (for images only)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    
    # Ownership
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploads'
    )
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Soft delete
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    # Usage tracking
    is_used = models.BooleanField(
        default=False,
        help_text='Whether file is referenced by another model'
    )
    used_by_model = models.CharField(
        max_length=100,
        blank=True,
        help_text='Model that references this upload (e.g., "Product", "User")'
    )
    used_by_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='ID of the object that references this upload'
    )
    
    class Meta:
        db_table = 'uploads'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['upload_type', 'status']),
            models.Index(fields=['uploaded_by', 'created_at']),
            models.Index(fields=['is_used', 'is_deleted']),
        ]
    
    def __str__(self):
        return f'{self.original_filename} ({self.upload_type})'
    
    @property
    def url(self):
        """Get public URL of the file."""
        if self.file:
            return self.file.url
        return None
    
    @property
    def is_image(self):
        """Check if the upload is an image."""
        image_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml']
        return self.content_type in image_types
    
    @property
    def file_extension(self):
        """Get file extension."""
        if self.original_filename:
            return os.path.splitext(self.original_filename)[1].lower()
        return ''
    
    def mark_as_used(self, model_name: str, object_id: str):
        """Mark this upload as being used by another model."""
        self.is_used = True
        self.used_by_model = model_name
        self.used_by_id = str(object_id)
        self.save(update_fields=['is_used', 'used_by_model', 'used_by_id', 'updated_at'])
    
    def mark_as_unused(self):
        """Mark this upload as no longer being used."""
        self.is_used = False
        self.used_by_model = ''
        self.used_by_id = ''
        self.save(update_fields=['is_used', 'used_by_model', 'used_by_id', 'updated_at'])
    
    def soft_delete(self):
        """Soft delete the upload."""
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])
    
    def hard_delete(self):
        """Permanently delete the upload and its file."""
        # Delete the actual file
        if self.file:
            self.file.delete(save=False)
        # Delete the record
        self.delete()


class UploadManager(models.Manager):
    """Custom manager for Upload model."""
    
    def get_queryset(self):
        """Exclude soft-deleted uploads by default."""
        return super().get_queryset().filter(is_deleted=False)
    
    def with_deleted(self):
        """Include soft-deleted uploads."""
        return super().get_queryset()
    
    def orphaned(self):
        """Get uploads that are not used by any model."""
        return self.get_queryset().filter(is_used=False)
    
    def by_type(self, upload_type):
        """Filter by upload type."""
        return self.get_queryset().filter(upload_type=upload_type)
    
    def by_user(self, user):
        """Filter by uploader."""
        return self.get_queryset().filter(uploaded_by=user)


# Add custom manager to Upload model
Upload.objects = UploadManager()
Upload.all_objects = models.Manager()  # Include deleted
