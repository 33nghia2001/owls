"""
Upload Tasks for Owls E-commerce Platform
=========================================
Celery tasks for upload management and cleanup.
"""

import logging
from datetime import timedelta
from celery import shared_task
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)


# Cleanup pending uploads older than this (default: 24 hours)
PENDING_UPLOAD_MAX_AGE_HOURS = getattr(settings, 'PENDING_UPLOAD_MAX_AGE_HOURS', 24)

# ClamAV configuration
CLAMAV_ENABLED = getattr(settings, 'CLAMAV_ENABLED', False)
CLAMAV_HOST = getattr(settings, 'CLAMAV_HOST', 'localhost')
CLAMAV_PORT = getattr(settings, 'CLAMAV_PORT', 3310)


@shared_task(name='uploads.scan_file_for_malware')
def scan_file_for_malware_task(upload_id: str) -> dict:
    """
    Scan uploaded file for malware using ClamAV.
    
    SECURITY: This task should be called after file upload but before
    marking the upload as safe/available for use.
    
    Configuration required in settings.py:
    - CLAMAV_ENABLED = True
    - CLAMAV_HOST = 'clamav'  # Docker service name or IP
    - CLAMAV_PORT = 3310
    
    Args:
        upload_id: UUID of the upload to scan
        
    Returns:
        dict: {
            'status': 'clean' | 'infected' | 'error' | 'skipped',
            'virus_name': str | None,
            'message': str
        }
    """
    from .models import Upload
    
    if not CLAMAV_ENABLED:
        logger.debug(f"Malware scanning disabled, skipping upload {upload_id}")
        return {
            'status': 'skipped',
            'virus_name': None,
            'message': 'ClamAV scanning is disabled'
        }
    
    try:
        upload = Upload.objects.get(id=upload_id)
    except Upload.DoesNotExist:
        logger.error(f"Upload not found for malware scan: {upload_id}")
        return {
            'status': 'error',
            'virus_name': None,
            'message': 'Upload not found'
        }
    
    if not upload.file:
        logger.warning(f"No file attached to upload {upload_id}")
        return {
            'status': 'error',
            'virus_name': None,
            'message': 'No file attached'
        }
    
    try:
        import pyclamd
        
        # Connect to ClamAV daemon
        cd = pyclamd.ClamdNetworkSocket(host=CLAMAV_HOST, port=CLAMAV_PORT)
        
        if not cd.ping():
            logger.error("ClamAV daemon is not responding")
            return {
                'status': 'error',
                'virus_name': None,
                'message': 'ClamAV daemon not available'
            }
        
        # Read file content and scan
        upload.file.seek(0)
        file_content = upload.file.read()
        upload.file.seek(0)
        
        scan_result = cd.scan_stream(file_content)
        
        if scan_result is None:
            # File is clean
            logger.info(f"Upload {upload_id} passed malware scan")
            
            # Mark as scanned (you may want to add a field for this)
            upload.metadata = upload.metadata or {}
            upload.metadata['malware_scanned'] = True
            upload.metadata['malware_scan_date'] = timezone.now().isoformat()
            upload.metadata['malware_scan_result'] = 'clean'
            upload.save(update_fields=['metadata', 'updated_at'])
            
            return {
                'status': 'clean',
                'virus_name': None,
                'message': 'No malware detected'
            }
        else:
            # File is infected
            virus_name = scan_result.get('stream', ['UNKNOWN'])[1] if scan_result else 'UNKNOWN'
            
            logger.warning(
                f"MALWARE DETECTED in upload {upload_id}: {virus_name}"
            )
            
            # Mark as infected and quarantine
            upload.status = Upload.Status.FAILED
            upload.metadata = upload.metadata or {}
            upload.metadata['malware_scanned'] = True
            upload.metadata['malware_scan_date'] = timezone.now().isoformat()
            upload.metadata['malware_scan_result'] = 'infected'
            upload.metadata['virus_name'] = virus_name
            upload.save()
            
            # Optionally delete the infected file
            try:
                upload.file.delete(save=False)
                logger.info(f"Deleted infected file for upload {upload_id}")
            except Exception as e:
                logger.error(f"Failed to delete infected file {upload_id}: {e}")
            
            return {
                'status': 'infected',
                'virus_name': virus_name,
                'message': f'Malware detected: {virus_name}'
            }
            
    except ImportError:
        logger.error("pyclamd library not installed. Run: pip install pyclamd")
        return {
            'status': 'error',
            'virus_name': None,
            'message': 'pyclamd library not installed'
        }
    except Exception as e:
        logger.error(f"Error scanning upload {upload_id}: {e}")
        return {
            'status': 'error',
            'virus_name': None,
            'message': str(e)
        }


@shared_task(name='uploads.cleanup_pending_uploads')
def cleanup_pending_uploads_task():
    """
    Cleanup pending uploads that were never confirmed.
    
    This task removes:
    1. Upload records with PENDING status older than PENDING_UPLOAD_MAX_AGE_HOURS
    2. Associated files from S3/R2 storage
    
    Should be scheduled to run periodically (e.g., every hour).
    
    Security:
    - Prevents storage spam from malicious users who generate presigned URLs
      but never complete the upload
    - Frees up database space from orphaned records
    """
    from .models import Upload
    
    cutoff_time = timezone.now() - timedelta(hours=PENDING_UPLOAD_MAX_AGE_HOURS)
    
    # Get pending uploads older than cutoff
    pending_uploads = Upload.objects.filter(
        status=Upload.Status.PENDING,
        created_at__lt=cutoff_time
    )
    
    count = pending_uploads.count()
    
    if count == 0:
        logger.info("cleanup_pending_uploads: No pending uploads to clean up")
        return {'deleted': 0, 'errors': 0}
    
    logger.info(f"cleanup_pending_uploads: Found {count} pending uploads to clean up")
    
    deleted_count = 0
    error_count = 0
    
    for upload in pending_uploads:
        try:
            # Try to delete file from storage if it exists
            if upload.file:
                try:
                    upload.file.delete(save=False)
                except Exception as e:
                    logger.warning(
                        f"Failed to delete file from storage for upload {upload.id}: {e}"
                    )
            
            # Delete the database record
            upload.delete()
            deleted_count += 1
            
        except Exception as e:
            logger.error(f"Error cleaning up upload {upload.id}: {e}")
            error_count += 1
    
    logger.info(
        f"cleanup_pending_uploads: Deleted {deleted_count} uploads, "
        f"{error_count} errors"
    )
    
    return {
        'deleted': deleted_count,
        'errors': error_count
    }


@shared_task(name='uploads.cleanup_orphaned_uploads')
def cleanup_orphaned_uploads_task(days_old: int = 30):
    """
    Cleanup orphaned uploads that are not used by any model.
    
    This task removes uploads that:
    1. Have is_used=False (not linked to any model)
    2. Are older than the specified days_old parameter
    3. Have COMPLETED status
    
    Args:
        days_old: Number of days to wait before considering an upload orphaned
        
    Should be scheduled to run weekly.
    """
    from .models import Upload
    
    cutoff_time = timezone.now() - timedelta(days=days_old)
    
    # Get orphaned uploads
    orphaned_uploads = Upload.objects.filter(
        is_used=False,
        status=Upload.Status.COMPLETED,
        created_at__lt=cutoff_time
    )
    
    count = orphaned_uploads.count()
    
    if count == 0:
        logger.info("cleanup_orphaned_uploads: No orphaned uploads to clean up")
        return {'deleted': 0, 'errors': 0}
    
    logger.info(f"cleanup_orphaned_uploads: Found {count} orphaned uploads to clean up")
    
    deleted_count = 0
    error_count = 0
    freed_bytes = 0
    
    for upload in orphaned_uploads:
        try:
            freed_bytes += upload.file_size or 0
            
            # Hard delete (removes file from storage)
            upload.hard_delete()
            deleted_count += 1
            
        except Exception as e:
            logger.error(f"Error cleaning up orphaned upload {upload.id}: {e}")
            error_count += 1
    
    freed_mb = round(freed_bytes / (1024 * 1024), 2)
    logger.info(
        f"cleanup_orphaned_uploads: Deleted {deleted_count} uploads "
        f"(freed {freed_mb} MB), {error_count} errors"
    )
    
    return {
        'deleted': deleted_count,
        'freed_mb': freed_mb,
        'errors': error_count
    }


@shared_task(name='uploads.verify_s3_file_exists')
def verify_s3_file_exists_task(upload_id: str) -> bool:
    """
    Verify that a file exists in S3/R2 storage.
    
    Used to validate presigned URL uploads were actually completed.
    
    Args:
        upload_id: UUID of the upload record
        
    Returns:
        bool: True if file exists, False otherwise
    """
    from .models import Upload
    import boto3
    from botocore.config import Config
    
    try:
        upload = Upload.objects.get(id=upload_id)
    except Upload.DoesNotExist:
        logger.error(f"Upload not found: {upload_id}")
        return False
    
    if not getattr(settings, 'AWS_S3_ENDPOINT_URL', None):
        # Local storage - assume exists if record exists
        return bool(upload.file)
    
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'auto'),
            config=Config(signature_version='s3v4')
        )
        
        # Try to get file metadata
        response = s3_client.head_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=str(upload.file)
        )
        
        # Update file size if not set
        if not upload.file_size and response.get('ContentLength'):
            upload.file_size = response['ContentLength']
            upload.save(update_fields=['file_size'])
        
        return True
        
    except s3_client.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            logger.warning(f"File not found in S3 for upload {upload_id}")
            return False
        raise
    except Exception as e:
        logger.error(f"Error verifying S3 file for upload {upload_id}: {e}")
        return False
