"""
Upload Serializers for Owls E-commerce Platform
===============================================
"""

from rest_framework import serializers
from django.conf import settings
from .models import Upload


class UploadSerializer(serializers.ModelSerializer):
    """Serializer for Upload model."""
    
    url = serializers.ReadOnlyField()
    is_image = serializers.ReadOnlyField()
    file_extension = serializers.ReadOnlyField()
    uploaded_by_name = serializers.CharField(
        source='uploaded_by.full_name',
        read_only=True,
        default=''
    )
    
    class Meta:
        model = Upload
        fields = [
            'id', 'url', 'original_filename', 'file_size', 'content_type',
            'upload_type', 'status', 'width', 'height',
            'is_image', 'file_extension',
            'uploaded_by', 'uploaded_by_name',
            'is_used', 'used_by_model', 'used_by_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'url', 'file_size', 'content_type', 'status',
            'width', 'height', 'uploaded_by', 'created_at', 'updated_at'
        ]


class UploadCreateSerializer(serializers.Serializer):
    """Serializer for creating uploads."""
    
    file = serializers.FileField()
    upload_type = serializers.ChoiceField(
        choices=Upload.UploadType.choices,
        default=Upload.UploadType.OTHER
    )
    
    # Validation settings
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB for images
    
    ALLOWED_IMAGE_TYPES = [
        'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml'
    ]
    ALLOWED_DOCUMENT_TYPES = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    ]
    ALLOWED_VIDEO_TYPES = [
        'video/mp4', 'video/webm', 'video/quicktime'
    ]
    
    def validate_file(self, file):
        """Validate uploaded file."""
        # Get content type
        content_type = file.content_type
        
        # Check file size based on type
        if content_type in self.ALLOWED_IMAGE_TYPES:
            if file.size > self.MAX_IMAGE_SIZE:
                raise serializers.ValidationError(
                    f'Image file size must be under {self.MAX_IMAGE_SIZE // (1024*1024)}MB'
                )
        elif file.size > self.MAX_FILE_SIZE:
            raise serializers.ValidationError(
                f'File size must be under {self.MAX_FILE_SIZE // (1024*1024)}MB'
            )
        
        # Check allowed content types
        all_allowed = (
            self.ALLOWED_IMAGE_TYPES + 
            self.ALLOWED_DOCUMENT_TYPES + 
            self.ALLOWED_VIDEO_TYPES
        )
        if content_type not in all_allowed:
            raise serializers.ValidationError(
                f'File type "{content_type}" is not allowed'
            )
        
        return file
    
    def create(self, validated_data):
        """Create upload record."""
        file = validated_data['file']
        upload_type = validated_data.get('upload_type', Upload.UploadType.OTHER)
        user = self.context['request'].user
        
        # Get image dimensions if applicable
        width, height = None, None
        content_type = file.content_type
        
        if content_type in self.ALLOWED_IMAGE_TYPES:
            try:
                from PIL import Image
                img = Image.open(file)
                width, height = img.size
                file.seek(0)  # Reset file pointer after reading
            except Exception:
                pass  # If can't read dimensions, that's OK
        
        # Create upload record
        upload = Upload.objects.create(
            file=file,
            original_filename=file.name,
            file_size=file.size,
            content_type=content_type,
            upload_type=upload_type,
            status=Upload.Status.COMPLETED,
            width=width,
            height=height,
            uploaded_by=user if user.is_authenticated else None
        )
        
        return upload


class BulkUploadSerializer(serializers.Serializer):
    """Serializer for bulk uploads."""
    
    files = serializers.ListField(
        child=serializers.FileField(),
        min_length=1,
        max_length=10  # Max 10 files at once
    )
    upload_type = serializers.ChoiceField(
        choices=Upload.UploadType.choices,
        default=Upload.UploadType.OTHER
    )
    
    def validate_files(self, files):
        """Validate all files."""
        single_serializer = UploadCreateSerializer()
        for file in files:
            single_serializer.validate_file(file)
        return files
    
    def create(self, validated_data):
        """Create multiple upload records."""
        files = validated_data['files']
        upload_type = validated_data.get('upload_type', Upload.UploadType.OTHER)
        user = self.context['request'].user
        
        uploads = []
        for file in files:
            serializer = UploadCreateSerializer(
                data={'file': file, 'upload_type': upload_type},
                context=self.context
            )
            serializer.is_valid(raise_exception=True)
            uploads.append(serializer.save())
        
        return uploads


class PresignedUrlSerializer(serializers.Serializer):
    """Serializer for generating presigned upload URLs."""
    
    filename = serializers.CharField(max_length=255)
    content_type = serializers.CharField(max_length=100)
    upload_type = serializers.ChoiceField(
        choices=Upload.UploadType.choices,
        default=Upload.UploadType.OTHER
    )
    
    def validate_content_type(self, value):
        """Validate content type."""
        allowed = (
            UploadCreateSerializer.ALLOWED_IMAGE_TYPES +
            UploadCreateSerializer.ALLOWED_DOCUMENT_TYPES +
            UploadCreateSerializer.ALLOWED_VIDEO_TYPES
        )
        if value not in allowed:
            raise serializers.ValidationError(f'Content type "{value}" is not allowed')
        return value


class MarkUsedSerializer(serializers.Serializer):
    """Serializer for marking uploads as used."""
    
    upload_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=50
    )
    model_name = serializers.CharField(max_length=100)
    object_id = serializers.CharField(max_length=100)
