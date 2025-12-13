"""
Fraud Detection Admin for Owls E-commerce Platform
==================================================
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    FraudRule, RiskAssessment, TriggeredRule,
    IPBlacklist, DeviceFingerprint, VelocityCounter
)


@admin.register(FraudRule)
class FraudRuleAdmin(admin.ModelAdmin):
    """Admin for fraud detection rules."""
    
    list_display = [
        'name', 'rule_type', 'action', 'risk_score', 'priority', 'is_active'
    ]
    list_filter = ['rule_type', 'action', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['priority', 'name']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'description', 'rule_type')
        }),
        ('Configuration', {
            'fields': ('conditions', 'action', 'risk_score', 'priority')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


class TriggeredRuleInline(admin.TabularInline):
    """Inline for triggered rules in assessment."""
    
    model = TriggeredRule
    extra = 0
    readonly_fields = ['rule', 'matched_value', 'details', 'created_at']
    can_delete = False


@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    """Admin for risk assessments."""
    
    list_display = [
        'id', 'order_link', 'user_link', 'risk_score_display',
        'risk_level', 'status', 'created_at'
    ]
    list_filter = ['risk_level', 'status', 'created_at']
    search_fields = ['order__order_number', 'user__email', 'ip_address']
    readonly_fields = [
        'id', 'order', 'user', 'risk_score', 'risk_level',
        'analysis_data', 'created_at', 'updated_at'
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    inlines = [TriggeredRuleInline]
    
    fieldsets = (
        ('Assessment', {
            'fields': ('id', 'order', 'user', 'risk_score', 'risk_level', 'status')
        }),
        ('Context', {
            'fields': ('ip_address', 'user_agent', 'device_fingerprint',
                      'country_code', 'city', 'order_amount', 'payment_method')
        }),
        ('Analysis', {
            'fields': ('analysis_data',),
            'classes': ('collapse',)
        }),
        ('Review', {
            'fields': ('reviewed_by', 'reviewed_at', 'review_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def order_link(self, obj):
        if obj.order:
            return format_html(
                '<a href="/admin/orders/order/{}/change/">{}</a>',
                obj.order.id, obj.order.order_number
            )
        return '-'
    order_link.short_description = 'Order'
    
    def user_link(self, obj):
        if obj.user:
            return format_html(
                '<a href="/admin/users/user/{}/change/">{}</a>',
                obj.user.id, obj.user.email
            )
        return '-'
    user_link.short_description = 'User'
    
    def risk_score_display(self, obj):
        color = 'green'
        if obj.risk_score >= 80:
            color = 'red'
        elif obj.risk_score >= 60:
            color = 'orange'
        elif obj.risk_score >= 30:
            color = '#DAA520'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.risk_score
        )
    risk_score_display.short_description = 'Score'


@admin.register(IPBlacklist)
class IPBlacklistAdmin(admin.ModelAdmin):
    """Admin for IP blacklist."""
    
    list_display = ['ip_address', 'reason', 'is_active_display', 'expires_at', 'created_at']
    list_filter = ['reason', 'created_at']
    search_fields = ['ip_address', 'notes']
    readonly_fields = ['created_at']
    
    def is_active_display(self, obj):
        if obj.is_active:
            return format_html('<span style="color: red;">⬤ Active</span>')
        return format_html('<span style="color: gray;">○ Expired</span>')
    is_active_display.short_description = 'Status'


@admin.register(DeviceFingerprint)
class DeviceFingerprintAdmin(admin.ModelAdmin):
    """Admin for device fingerprints."""
    
    list_display = [
        'fingerprint_short', 'user', 'device_type', 'is_trusted',
        'is_blocked', 'order_count', 'last_seen'
    ]
    list_filter = ['is_trusted', 'is_blocked', 'device_type']
    search_fields = ['fingerprint', 'user__email']
    readonly_fields = ['fingerprint', 'first_seen', 'last_seen', 'login_count', 'order_count']
    
    def fingerprint_short(self, obj):
        return f'{obj.fingerprint[:20]}...'
    fingerprint_short.short_description = 'Fingerprint'


@admin.register(VelocityCounter)
class VelocityCounterAdmin(admin.ModelAdmin):
    """Admin for velocity counters."""
    
    list_display = [
        'counter_type', 'identifier', 'count', 'total_amount',
        'window_start', 'window_end'
    ]
    list_filter = ['counter_type', 'window_start']
    search_fields = ['identifier']
    readonly_fields = ['window_start', 'window_end']
