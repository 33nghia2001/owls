"""
Marketing Campaigns Serializers for Owls E-commerce Platform
============================================================
"""

from rest_framework import serializers
from django.utils.text import slugify
from .models import Campaign, CampaignMetrics, CampaignChannel


class CampaignChannelSerializer(serializers.ModelSerializer):
    """Serializer for CampaignChannel."""
    
    class Meta:
        model = CampaignChannel
        fields = [
            'id', 'channel_type', 'settings', 'budget', 'spent',
            'impressions', 'clicks', 'conversions', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'spent', 'impressions', 'clicks', 'conversions', 'created_at']


class CampaignMetricsSerializer(serializers.ModelSerializer):
    """Serializer for CampaignMetrics."""
    
    click_through_rate = serializers.ReadOnlyField()
    conversion_rate = serializers.ReadOnlyField()
    average_order_value = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    roi = serializers.ReadOnlyField()
    
    class Meta:
        model = CampaignMetrics
        fields = [
            'impressions', 'clicks', 'unique_visitors',
            'orders', 'revenue', 'discount_given',
            'click_through_rate', 'conversion_rate',
            'average_order_value', 'roi', 'updated_at'
        ]


class CampaignListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for campaign lists."""
    
    is_active = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    
    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'slug', 'campaign_type', 'status',
            'start_date', 'end_date', 'banner_image', 'thumbnail_image',
            'is_featured', 'is_active', 'is_upcoming', 'days_remaining',
            'discount_type', 'discount_value', 'priority'
        ]


class CampaignSerializer(serializers.ModelSerializer):
    """Full serializer for Campaign."""
    
    is_active = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    created_by_name = serializers.CharField(
        source='created_by.full_name',
        read_only=True,
        default=''
    )
    
    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'slug', 'description',
            'campaign_type', 'status', 'start_date', 'end_date',
            'target_audience', 'budget', 'spent',
            'discount_type', 'discount_value', 'max_discount', 'coupon_code',
            'banner_image', 'thumbnail_image',
            'is_featured', 'is_public', 'priority',
            'is_active', 'is_upcoming', 'is_expired', 'days_remaining',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'spent', 'created_by', 'created_at', 'updated_at']


class CampaignDetailSerializer(CampaignSerializer):
    """Detailed serializer with metrics and channels."""
    
    metrics = CampaignMetricsSerializer(read_only=True)
    channels = CampaignChannelSerializer(many=True, read_only=True)
    products_count = serializers.IntegerField(source='products.count', read_only=True)
    categories_count = serializers.IntegerField(source='categories.count', read_only=True)
    
    class Meta(CampaignSerializer.Meta):
        fields = CampaignSerializer.Meta.fields + [
            'metrics', 'channels', 'products_count', 'categories_count'
        ]


class CampaignCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating campaigns."""
    
    class Meta:
        model = Campaign
        fields = [
            'name', 'slug', 'description', 'campaign_type',
            'start_date', 'end_date', 'target_audience', 'budget',
            'discount_type', 'discount_value', 'max_discount', 'coupon_code',
            'banner_image', 'thumbnail_image',
            'is_featured', 'is_public', 'priority'
        ]
    
    def validate(self, data):
        # Auto-generate slug if not provided
        if not data.get('slug'):
            data['slug'] = slugify(data['name'])
        
        # Validate dates
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError({
                'end_date': 'End date must be after start date'
            })
        
        # Validate discount
        if data.get('discount_type') == 'percentage':
            if data.get('discount_value') and data['discount_value'] > 100:
                raise serializers.ValidationError({
                    'discount_value': 'Percentage discount cannot exceed 100%'
                })
        
        return data
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class CampaignStatsSerializer(serializers.Serializer):
    """Serializer for campaign statistics."""
    
    by_status = serializers.DictField()
    active_campaigns = serializers.IntegerField()
    total_impressions = serializers.IntegerField()
    total_clicks = serializers.IntegerField()
    total_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_discount_given = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_budget = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_spent = serializers.DecimalField(max_digits=14, decimal_places=2)
