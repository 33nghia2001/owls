"""
Marketing Campaigns Admin for Owls E-commerce Platform
======================================================
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Campaign, CampaignMetrics, CampaignChannel


class CampaignChannelInline(admin.TabularInline):
    """Inline for campaign channels."""
    
    model = CampaignChannel
    extra = 0
    fields = ['channel_type', 'budget', 'spent', 'impressions', 'clicks', 'conversions', 'is_active']


class CampaignMetricsInline(admin.StackedInline):
    """Inline for campaign metrics."""
    
    model = CampaignMetrics
    can_delete = False
    readonly_fields = [
        'impressions', 'clicks', 'unique_visitors',
        'orders', 'revenue', 'discount_given', 'updated_at'
    ]


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    """Admin for campaigns."""
    
    list_display = [
        'name', 'campaign_type', 'status_badge', 'date_range',
        'is_featured', 'priority', 'created_at'
    ]
    list_filter = ['status', 'campaign_type', 'is_featured', 'is_public']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['id', 'created_at', 'updated_at', 'spent']
    ordering = ['-priority', '-created_at']
    date_hierarchy = 'created_at'
    inlines = [CampaignMetricsInline, CampaignChannelInline]
    filter_horizontal = ['products', 'categories']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'name', 'slug', 'description')
        }),
        ('Type & Status', {
            'fields': ('campaign_type', 'status')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date')
        }),
        ('Budget', {
            'fields': ('budget', 'spent')
        }),
        ('Discount', {
            'fields': ('discount_type', 'discount_value', 'max_discount', 'coupon_code'),
            'classes': ('collapse',)
        }),
        ('Target', {
            'fields': ('products', 'categories', 'target_audience'),
            'classes': ('collapse',)
        }),
        ('Media', {
            'fields': ('banner_image', 'thumbnail_image')
        }),
        ('Visibility', {
            'fields': ('is_featured', 'is_public', 'priority')
        }),
        ('Tracking', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )
    
    def status_badge(self, obj):
        """Display status with color badge."""
        colors = {
            'draft': 'gray',
            'scheduled': 'blue',
            'active': 'green',
            'paused': 'orange',
            'completed': 'purple',
            'cancelled': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def date_range(self, obj):
        """Display date range."""
        return f"{obj.start_date.strftime('%Y-%m-%d')} → {obj.end_date.strftime('%Y-%m-%d')}"
    date_range.short_description = 'Duration'
    
    actions = ['activate_campaigns', 'pause_campaigns']
    
    @admin.action(description='Activate selected campaigns')
    def activate_campaigns(self, request, queryset):
        queryset.update(status=Campaign.Status.ACTIVE)
    
    @admin.action(description='Pause selected campaigns')
    def pause_campaigns(self, request, queryset):
        queryset.update(status=Campaign.Status.PAUSED)


@admin.register(CampaignMetrics)
class CampaignMetricsAdmin(admin.ModelAdmin):
    """Admin for campaign metrics."""
    
    list_display = [
        'campaign', 'impressions', 'clicks', 'ctr_display',
        'orders', 'revenue', 'roi_display'
    ]
    readonly_fields = [
        'campaign', 'impressions', 'clicks', 'unique_visitors',
        'orders', 'revenue', 'discount_given', 'updated_at'
    ]
    
    def ctr_display(self, obj):
        return f"{obj.click_through_rate}%"
    ctr_display.short_description = 'CTR'
    
    def roi_display(self, obj):
        roi = obj.roi
        color = 'green' if roi > 0 else 'red' if roi < 0 else 'gray'
        return format_html(
            '<span style="color: {};">{:+.1f}%</span>',
            color, roi
        )
    roi_display.short_description = 'ROI'
