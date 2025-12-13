"""
Custom Storage Backends for Owls E-commerce Platform
====================================================
Cloudflare R2 compatible storage with optimized settings.
"""

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class CloudflareR2Storage(S3Boto3Storage):
    """
    Custom storage backend for Cloudflare R2.
    R2 is S3-compatible but has some differences.
    """
    
    # R2 doesn't support ACLs
    default_acl = None
    
    # Don't append random strings to filenames
    file_overwrite = False
    
    # Use unsigned URLs for public access
    querystring_auth = False
    
    # Signature version
    signature_version = 's3v4'
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('bucket_name', settings.AWS_STORAGE_BUCKET_NAME)
        kwargs.setdefault('endpoint_url', settings.AWS_S3_ENDPOINT_URL)
        kwargs.setdefault('region_name', getattr(settings, 'AWS_S3_REGION_NAME', 'auto'))
        super().__init__(*args, **kwargs)
    
    def url(self, name):
        """
        Generate public URL for the file.
        If custom domain is set, use it; otherwise use R2 public URL.
        """
        custom_domain = getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', '')
        
        if custom_domain:
            # Use custom domain (e.g., cdn.owls.asia)
            return f'https://{custom_domain}/{name}'
        else:
            # Use R2 public URL format
            # You need to enable public access in R2 dashboard
            bucket = settings.AWS_STORAGE_BUCKET_NAME
            account_id = settings.AWS_S3_ENDPOINT_URL.split('//')[1].split('.')[0]
            return f'https://pub-{account_id}.r2.dev/{name}'


class MediaStorage(CloudflareR2Storage):
    """Storage for user-uploaded media files."""
    
    location = 'media'
    
    def get_available_name(self, name, max_length=None):
        """
        Generate unique filename to prevent overwrites.
        """
        import os
        import uuid
        
        # Split filename and extension
        base, ext = os.path.splitext(name)
        
        # Add UUID to ensure uniqueness
        unique_name = f'{base}_{uuid.uuid4().hex[:8]}{ext}'
        
        return super().get_available_name(unique_name, max_length)


class ProductImageStorage(CloudflareR2Storage):
    """Storage specifically for product images."""
    
    location = 'media/products'


class UserAvatarStorage(CloudflareR2Storage):
    """Storage specifically for user avatars."""
    
    location = 'media/avatars'


class VendorStorage(CloudflareR2Storage):
    """Storage for vendor logos and documents."""
    
    location = 'media/vendors'


class DocumentStorage(CloudflareR2Storage):
    """Storage for documents (invoices, receipts, etc.)."""
    
    location = 'media/documents'


def get_upload_path(instance, filename, folder='uploads'):
    """
    Generate upload path with organized structure.
    Format: media/{folder}/{year}/{month}/{day}/{uuid}_{filename}
    """
    import os
    import uuid
    from datetime import datetime
    
    now = datetime.now()
    ext = os.path.splitext(filename)[1].lower()
    new_filename = f'{uuid.uuid4().hex}{ext}'
    
    return f'{folder}/{now.year}/{now.month:02d}/{now.day:02d}/{new_filename}'


def product_image_path(instance, filename):
    """Upload path for product images."""
    return get_upload_path(instance, filename, 'products')


def user_avatar_path(instance, filename):
    """Upload path for user avatars."""
    return get_upload_path(instance, filename, 'avatars')


def vendor_logo_path(instance, filename):
    """Upload path for vendor logos."""
    return get_upload_path(instance, filename, 'vendors/logos')


def vendor_document_path(instance, filename):
    """Upload path for vendor documents."""
    return get_upload_path(instance, filename, 'vendors/documents')


def category_image_path(instance, filename):
    """Upload path for category images."""
    return get_upload_path(instance, filename, 'categories')


def banner_image_path(instance, filename):
    """Upload path for banner images."""
    return get_upload_path(instance, filename, 'banners')
