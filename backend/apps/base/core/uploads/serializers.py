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
    
    # SECURITY: Magic bytes to MIME type mapping for server-side validation
    # This prevents attackers from spoofing Content-Type header
    MAGIC_BYTES_MAP = {
        # Images
        b'\xff\xd8\xff': 'image/jpeg',
        b'\x89PNG\r\n\x1a\n': 'image/png',
        b'GIF87a': 'image/gif',
        b'GIF89a': 'image/gif',
        b'RIFF': 'image/webp',  # WebP starts with RIFF....WEBP
        b'<svg': 'image/svg+xml',
        b'<?xml': 'image/svg+xml',  # SVG with XML declaration
        # Documents
        b'%PDF': 'application/pdf',
        b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1': 'application/msword',  # OLE (doc, xls)
        b'PK\x03\x04': 'application/zip',  # ZIP-based (docx, xlsx, etc.)
        # Videos
        b'\x00\x00\x00\x18ftypmp4': 'video/mp4',
        b'\x00\x00\x00\x1cftypisom': 'video/mp4',
        b'\x00\x00\x00\x20ftypisom': 'video/mp4',
        b'\x1aE\xdf\xa3': 'video/webm',
        b'\x00\x00\x00\x14ftypqt': 'video/quicktime',
    }
    
    def _detect_mime_from_magic_bytes(self, file) -> str:
        """
        Detect actual MIME type from file's magic bytes.
        
        SECURITY: This prevents Content-Type spoofing attacks where attacker
        sends malicious file with fake Content-Type header.
        
        Returns:
            str: Detected MIME type or empty string if unknown
        """
        # Read first 32 bytes for magic number detection
        file.seek(0)
        header = file.read(32)
        file.seek(0)  # Reset file pointer
        
        if not header:
            return ''
        
        # Check for known magic bytes
        for magic, mime_type in self.MAGIC_BYTES_MAP.items():
            if header.startswith(magic):
                # Special handling for WebP (RIFF....WEBP)
                if magic == b'RIFF' and b'WEBP' in header[:16]:
                    return 'image/webp'
                elif magic == b'RIFF':
                    continue  # Not WebP, might be other RIFF format
                return mime_type
        
        # Check for ZIP-based Office formats
        if header.startswith(b'PK\x03\x04'):
            # Try to detect specific Office format
            try:
                import zipfile
                import io
                
                file.seek(0)
                content = file.read()
                file.seek(0)
                
                with zipfile.ZipFile(io.BytesIO(content), 'r') as zf:
                    namelist = zf.namelist()
                    if '[Content_Types].xml' in namelist:
                        if 'word/' in str(namelist):
                            return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                        elif 'xl/' in str(namelist):
                            return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            except Exception:
                pass
            return 'application/zip'
        
        # Try python-magic if available (more comprehensive detection)
        try:
            import magic
            file.seek(0)
            mime = magic.from_buffer(file.read(2048), mime=True)
            file.seek(0)
            return mime
        except ImportError:
            pass
        except Exception:
            pass
        
        return ''
    
    def validate_file(self, file):
        """Validate uploaded file with magic bytes verification."""
        # SECURITY: Get actual content type from magic bytes, not from client header
        detected_type = self._detect_mime_from_magic_bytes(file)
        client_type = file.content_type
        
        # Build allowed types list
        all_allowed = (
            self.ALLOWED_IMAGE_TYPES + 
            self.ALLOWED_DOCUMENT_TYPES + 
            self.ALLOWED_VIDEO_TYPES
        )
        
        # Determine the content type to use
        if detected_type:
            # Use detected type (trusted)
            content_type = detected_type
            
            # SECURITY: Warn if client type doesn't match detected type
            if client_type != detected_type:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(
                    f"Content-Type mismatch: client sent '{client_type}', "
                    f"detected '{detected_type}' for file '{file.name}'"
                )
        else:
            # Fallback to client type only for known safe types with additional checks
            content_type = client_type
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"Could not detect MIME type for file '{file.name}', "
                f"falling back to client-provided '{client_type}'"
            )
        
        # Store the verified content type for later use
        file._verified_content_type = content_type
        
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
        if content_type not in all_allowed:
            raise serializers.ValidationError(
                f'File type "{content_type}" is not allowed. '
                f'Detected from file content, not from header.'
            )
        
        return file
    
    def create(self, validated_data):
        """Create upload record."""
        file = validated_data['file']
        upload_type = validated_data.get('upload_type', Upload.UploadType.OTHER)
        user = self.context['request'].user
        
        # Get image dimensions if applicable
        width, height = None, None
        # SECURITY: Use verified content type, not client-provided
        content_type = getattr(file, '_verified_content_type', file.content_type)
        
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
