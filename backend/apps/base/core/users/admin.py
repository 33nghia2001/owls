"""
User Admin Configuration for Owls E-commerce Platform
======================================================
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserAddress, UserVerification, UserSession


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for custom User model."""
    
    list_display = [
        'email', 'first_name', 'last_name', 'role', 'is_verified', 
        'is_active', 'date_joined', 'last_login'
    ]
    list_filter = ['role', 'is_verified', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name', 'phone_number']
    ordering = ['-date_joined']
    readonly_fields = ['id', 'date_joined', 'last_login']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {
            'fields': ('first_name', 'last_name', 'phone_number', 'avatar', 'date_of_birth')
        }),
        (_('Role & Status'), {
            'fields': ('role', 'is_verified', 'is_active')
        }),
        (_('Permissions'), {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        (_('Important Dates'), {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'role'),
        }),
    )


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    """Admin configuration for UserAddress model."""
    
    list_display = ['user', 'address_type', 'recipient_name', 'city', 'is_default', 'created_at']
    list_filter = ['address_type', 'is_default', 'city']
    search_fields = ['user__email', 'recipient_name', 'phone_number', 'address_line_1']
    raw_id_fields = ['user']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(UserVerification)
class UserVerificationAdmin(admin.ModelAdmin):
    """Admin configuration for UserVerification model."""
    
    list_display = ['user', 'verification_type', 'is_used', 'expires_at', 'created_at']
    list_filter = ['verification_type', 'is_used']
    search_fields = ['user__email']
    raw_id_fields = ['user']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """Admin configuration for UserSession model."""
    
    list_display = ['user', 'device_type', 'ip_address', 'is_active', 'last_activity', 'created_at']
    list_filter = ['device_type', 'is_active', 'created_at']
    search_fields = ['user__email', 'ip_address', 'device_name']
    raw_id_fields = ['user']
    readonly_fields = ['id', 'session_key', 'created_at', 'last_activity']
    
    def has_add_permission(self, request):
        return False
