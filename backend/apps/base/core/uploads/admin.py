"""
Upload Admin for Owls E-commerce Platform
=========================================
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Upload


@admin.register(Upload)
class UploadAdmin(admin.ModelAdmin):
    """Admin interface for Upload model."""
    
    list_display = [
        'id', 'original_filename', 'upload_type', 'status',
        'file_size_display', 'is_used', 'uploaded_by', 'created_at'
    ]
    list_filter = ['upload_type', 'status', 'is_used', 'is_deleted', 'created_at']
    search_fields = ['original_filename', 'used_by_model', 'used_by_id']
    readonly_fields = [
        'id', 'file_size', 'content_type', 'width', 'height',
        'created_at', 'updated_at', 'preview'
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('File Info', {
            'fields': ('id', 'file', 'preview', 'original_filename', 'content_type')
        }),
        ('Metadata', {
            'fields': ('file_size', 'width', 'height', 'upload_type', 'status')
        }),
        ('Usage', {
            'fields': ('is_used', 'used_by_model', 'used_by_id')
        }),
        ('Ownership', {
            'fields': ('uploaded_by',)
        }),
        ('Tracking', {
            'fields': ('created_at', 'updated_at', 'is_deleted', 'deleted_at')
        }),
    )
    
    def file_size_display(self, obj):
        """Display file size in human-readable format."""
        size = obj.file_size
        if size < 1024:
            return f'{size} B'
        elif size < 1024 * 1024:
            return f'{size / 1024:.1f} KB'
        else:
            return f'{size / (1024 * 1024):.2f} MB'
    file_size_display.short_description = 'Size'
    
    def preview(self, obj):
        """Show image preview if applicable."""
        if obj.is_image and obj.url:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px;" />',
                obj.url
            )
        return '-'
    preview.short_description = 'Preview'
    
    def get_queryset(self, request):
        """Include soft-deleted uploads for admin."""
        return Upload.all_objects.all()
    
    actions = ['mark_as_used', 'mark_as_unused', 'hard_delete_selected']
    
    @admin.action(description='Mark selected uploads as used')
    def mark_as_used(self, request, queryset):
        queryset.update(is_used=True)
    
    @admin.action(description='Mark selected uploads as unused')
    def mark_as_unused(self, request, queryset):
        queryset.update(is_used=False, used_by_model='', used_by_id='')
    
    @admin.action(description='Permanently delete selected uploads')
    def hard_delete_selected(self, request, queryset):
        for upload in queryset:
            upload.hard_delete()
        self.message_user(request, f'{queryset.count()} uploads permanently deleted.')
