"""
Upload Views for Owls E-commerce Platform
=========================================
API endpoints for file upload management.
"""

import logging
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.throttling import UserRateThrottle
from django.shortcuts import get_object_or_404
from django.db import models, transaction
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Upload
from .serializers import (
    UploadSerializer, UploadCreateSerializer, BulkUploadSerializer,
    PresignedUrlSerializer, MarkUsedSerializer
)

logger = logging.getLogger(__name__)


class IsOwnerOrAdmin(permissions.BasePermission):
    """Permission check for upload owner or admin."""
    
    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.is_staff:
            return True
        # Owner can manage their uploads
        return obj.uploaded_by == request.user


@extend_schema(tags=['Uploads'])
class UploadListView(generics.ListAPIView):
    """
    List uploads for authenticated user.
    
    Admins can see all uploads, regular users see only their own.
    """
    
    serializer_class = UploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Upload.objects.none()
        
        user = self.request.user
        queryset = Upload.objects.all()
        
        # Non-admin users can only see their own uploads
        if not user.is_staff:
            queryset = queryset.filter(uploaded_by=user)
        
        # Filter by upload_type
        upload_type = self.request.query_params.get('type')
        if upload_type:
            queryset = queryset.filter(upload_type=upload_type)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter unused (orphaned) files
        unused = self.request.query_params.get('unused')
        if unused and unused.lower() == 'true':
            queryset = queryset.filter(is_used=False)
        
        return queryset.select_related('uploaded_by')


@extend_schema(
    tags=['Uploads'],
    request=UploadCreateSerializer,
    responses={
        201: UploadSerializer,
        400: OpenApiResponse(description='Invalid file or validation error')
    }
)
class UploadCreateView(APIView):
    """
    Upload a single file.
    
    Supports images (jpg, png, gif, webp, svg), documents (pdf, doc, docx, xls, xlsx),
    and videos (mp4, webm, mov).
    
    Max file size: 10MB (5MB for images)
    """
    
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        serializer = UploadCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        upload = serializer.save()
        
        # SECURITY: Sanitize filename in log to prevent log injection attacks
        from apps.base.core.system.security import sanitize_for_logging
        safe_filename = sanitize_for_logging(upload.original_filename, max_length=100)
        logger.info(f"File uploaded: {safe_filename} by user {request.user.id}")
        
        return Response({
            'success': True,
            'message': 'File uploaded successfully',
            'data': UploadSerializer(upload).data
        }, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=['Uploads'],
    request=BulkUploadSerializer,
    responses={
        201: OpenApiResponse(description='Files uploaded successfully'),
        400: OpenApiResponse(description='Invalid files or validation error')
    }
)
class BulkUploadView(APIView):
    """
    Upload multiple files at once.
    
    Max 10 files per request.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        serializer = BulkUploadSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            uploads = serializer.save()
        
        logger.info(f"Bulk upload: {len(uploads)} files by user {request.user.id}")
        
        return Response({
            'success': True,
            'message': f'{len(uploads)} files uploaded successfully',
            'data': UploadSerializer(uploads, many=True).data
        }, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=['Uploads'],
    responses={
        200: UploadSerializer,
        404: OpenApiResponse(description='Upload not found')
    }
)
class UploadDetailView(generics.RetrieveAPIView):
    """Get upload details."""
    
    serializer_class = UploadSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    lookup_field = 'id'
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Upload.objects.none()
        return Upload.objects.select_related('uploaded_by')


@extend_schema(
    tags=['Uploads'],
    responses={
        204: OpenApiResponse(description='Upload deleted'),
        404: OpenApiResponse(description='Upload not found')
    }
)
class UploadDeleteView(APIView):
    """
    Delete an upload.
    
    Performs soft delete by default. Use ?hard=true for permanent deletion.
    """
    
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def delete(self, request, id):
        upload = get_object_or_404(Upload.objects.all(), id=id)
        self.check_object_permissions(request, upload)
        
        hard_delete = request.query_params.get('hard', '').lower() == 'true'
        
        if hard_delete and request.user.is_staff:
            # Permanent deletion (admin only)
            # SECURITY: Sanitize filename in log to prevent log injection
            from apps.base.core.system.security import sanitize_for_logging
            safe_filename = sanitize_for_logging(upload.original_filename, max_length=100)
            upload.hard_delete()
            logger.warning(f"Hard delete: {safe_filename} by admin {request.user.id}")
            message = 'File permanently deleted'
        else:
            # Soft delete
            from apps.base.core.system.security import sanitize_for_logging
            safe_filename = sanitize_for_logging(upload.original_filename, max_length=100)
            upload.soft_delete()
            logger.info(f"Soft delete: {safe_filename} by user {request.user.id}")
            message = 'File deleted'
        
        return Response({
            'success': True,
            'message': message
        }, status=status.HTTP_200_OK)


# Maximum pending uploads per user (prevents storage spam)
MAX_PENDING_UPLOADS_PER_USER = 20

# Content type whitelist per upload type (prevents malicious file uploads)
CONTENT_TYPE_WHITELIST = {
    'avatar': ['image/jpeg', 'image/png', 'image/webp'],
    'product': ['image/jpeg', 'image/png', 'image/webp', 'image/gif'],
    'banner': ['image/jpeg', 'image/png', 'image/webp'],
    'document': [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    ],
    'video': ['video/mp4', 'video/webm', 'video/quicktime'],
    'other': [
        'image/jpeg', 'image/png', 'image/webp', 'image/gif',
        'application/pdf',
    ],
}


class PresignedUrlThrottle(UserRateThrottle):
    """Stricter rate limiting for presigned URL generation."""
    rate = '10/minute'  # Max 10 presigned URLs per minute per user


@extend_schema(
    tags=['Uploads'],
    request=PresignedUrlSerializer,
    responses={
        200: OpenApiResponse(description='Presigned URL generated'),
        400: OpenApiResponse(description='Invalid request'),
        429: OpenApiResponse(description='Too many requests')
    }
)
class PresignedUploadUrlView(APIView):
    """
    Generate a presigned URL for direct upload to R2/S3.
    
    This allows large file uploads directly to storage without passing through
    the application server, reducing server load.
    
    Security measures:
    - Rate limited to 10 requests/minute per user
    - Maximum 20 pending uploads per user
    - Content-type whitelist per upload_type
    
    Flow:
    1. Client requests presigned URL
    2. Server returns URL + upload_id
    3. Client uploads directly to R2/S3
    4. Client confirms upload completion
    """
    
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [PresignedUrlThrottle]
    
    def post(self, request):
        serializer = PresignedUrlSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        filename = serializer.validated_data['filename']
        content_type = serializer.validated_data['content_type']
        upload_type = serializer.validated_data['upload_type']
        
        # SECURITY: Validate content_type against whitelist for the upload_type
        allowed_types = CONTENT_TYPE_WHITELIST.get(upload_type, CONTENT_TYPE_WHITELIST['other'])
        if content_type not in allowed_types:
            logger.warning(
                f"Blocked presigned URL request: content_type '{content_type}' "
                f"not allowed for upload_type '{upload_type}' by user {request.user.id}"
            )
            return Response({
                'success': False,
                'error': {
                    'message': f"Content type '{content_type}' is not allowed for {upload_type} uploads",
                    'allowed_types': allowed_types
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # SECURITY: Check pending uploads limit to prevent storage spam
        pending_count = Upload.objects.filter(
            uploaded_by=request.user,
            status=Upload.Status.PENDING
        ).count()
        
        if pending_count >= MAX_PENDING_UPLOADS_PER_USER:
            logger.warning(
                f"User {request.user.id} exceeded max pending uploads limit ({pending_count})"
            )
            return Response({
                'success': False,
                'error': {
                    'message': f'Too many pending uploads. Please complete or cancel existing uploads first.',
                    'pending_count': pending_count,
                    'max_allowed': MAX_PENDING_UPLOADS_PER_USER
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if R2/S3 is configured
        if not getattr(settings, 'AWS_S3_ENDPOINT_URL', None):
            return Response({
                'success': False,
                'error': {'message': 'Direct upload not available in development mode'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create pending upload record
        from .storage import get_upload_path
        
        upload = Upload.objects.create(
            original_filename=filename,
            file_size=0,  # Will be updated after upload
            content_type=content_type,
            upload_type=upload_type,
            status=Upload.Status.PENDING,
            uploaded_by=request.user
        )
        
        # Generate the key (path) for the file
        key = get_upload_path(upload, filename, upload_type)
        
        try:
            import boto3
            from botocore.config import Config
            
            # Create S3 client
            s3_client = boto3.client(
                's3',
                endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'auto'),
                config=Config(signature_version='s3v4')
            )
            
            # Generate presigned URL (1 hour expiry)
            presigned_url = s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                    'Key': key,
                    'ContentType': content_type,
                },
                ExpiresIn=3600  # 1 hour
            )
            
            # SECURITY: Sanitize filename in log to prevent log injection
            from apps.base.core.system.security import sanitize_for_logging
            safe_filename = sanitize_for_logging(filename, max_length=100)
            logger.info(f"Presigned URL generated for {safe_filename} by user {request.user.id}")
            
            return Response({
                'success': True,
                'data': {
                    'upload_id': str(upload.id),
                    'presigned_url': presigned_url,
                    'key': key,
                    'expires_in': 3600
                }
            })
            
        except Exception as e:
            # Clean up the pending record
            upload.delete()
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            return Response({
                'success': False,
                'error': {'message': 'Failed to generate upload URL'}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=['Uploads'],
    responses={
        200: UploadSerializer,
        404: OpenApiResponse(description='Upload not found')
    }
)
class ConfirmUploadView(APIView):
    """
    Confirm that a presigned URL upload has completed.
    
    Updates the upload record with actual file info from storage.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, id):
        upload = get_object_or_404(
            Upload.objects.filter(uploaded_by=request.user),
            id=id
        )
        
        if upload.status != Upload.Status.PENDING:
            return Response({
                'success': False,
                'error': {'message': 'Upload already confirmed or failed'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update upload status
        upload.status = Upload.Status.COMPLETED
        upload.save(update_fields=['status', 'updated_at'])
        
        # SECURITY: Sanitize filename in log to prevent log injection
        from apps.base.core.system.security import sanitize_for_logging
        safe_filename = sanitize_for_logging(upload.original_filename, max_length=100)
        logger.info(f"Upload confirmed: {safe_filename}")
        
        return Response({
            'success': True,
            'message': 'Upload confirmed',
            'data': UploadSerializer(upload).data
        })


@extend_schema(
    tags=['Uploads'],
    request=MarkUsedSerializer,
    responses={
        200: OpenApiResponse(description='Uploads marked as used'),
        400: OpenApiResponse(description='Invalid request')
    }
)
class MarkUploadsUsedView(APIView):
    """
    Mark uploads as being used by another model.
    
    This helps track which files are in use and which are orphaned.
    Used internally when creating products, users, etc.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = MarkUsedSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        upload_ids = serializer.validated_data['upload_ids']
        model_name = serializer.validated_data['model_name']
        object_id = serializer.validated_data['object_id']
        
        # Get uploads (must belong to user or user is admin)
        user = request.user
        queryset = Upload.objects.filter(id__in=upload_ids)
        if not user.is_staff:
            queryset = queryset.filter(uploaded_by=user)
        
        uploads = list(queryset)
        if len(uploads) != len(upload_ids):
            return Response({
                'success': False,
                'error': {'message': 'Some uploads not found or not accessible'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Mark all as used
        with transaction.atomic():
            for upload in uploads:
                upload.mark_as_used(model_name, object_id)
        
        return Response({
            'success': True,
            'message': f'{len(uploads)} uploads marked as used',
            'data': UploadSerializer(uploads, many=True).data
        })


@extend_schema(
    tags=['Uploads'],
    responses={
        200: OpenApiResponse(description='Storage statistics')
    }
)
class StorageStatsView(APIView):
    """
    Get storage usage statistics.
    
    Admin only endpoint for monitoring storage usage.
    """
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        from django.db.models import Sum, Count, Q
        
        # Overall stats
        total_stats = Upload.objects.aggregate(
            total_files=Count('id'),
            total_size=Sum('file_size'),
            used_files=Count('id', filter=Q(is_used=True)),
            orphaned_files=Count('id', filter=Q(is_used=False))
        )
        
        # Stats by type
        by_type = Upload.objects.values('upload_type').annotate(
            count=Count('id'),
            size=Sum('file_size')
        ).order_by('-size')
        
        # Recent uploads
        recent_count = Upload.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        return Response({
            'success': True,
            'data': {
                'total_files': total_stats['total_files'] or 0,
                'total_size_bytes': total_stats['total_size'] or 0,
                'total_size_mb': round((total_stats['total_size'] or 0) / (1024 * 1024), 2),
                'used_files': total_stats['used_files'] or 0,
                'orphaned_files': total_stats['orphaned_files'] or 0,
                'recent_uploads_7d': recent_count,
                'by_type': list(by_type)
            }
        })
