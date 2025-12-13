"""
Shipping Serializers for Owls E-commerce Platform
=================================================
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from .models import ShippingProvider, ShippingZone, ShippingRate, ShippingMethod


class ShippingProviderSerializer(serializers.ModelSerializer):
    """Serializer for shipping providers."""
    
    delivery_estimate = serializers.SerializerMethodField()

    class Meta:
        model = ShippingProvider
        fields = [
            'id',
            'code',
            'name',
            'logo',
            'provider_type',
            'is_default',
            'min_delivery_days',
            'max_delivery_days',
            'delivery_estimate'
        ]

    def get_delivery_estimate(self, obj):
        """Get delivery time estimate string."""
        if obj.min_delivery_days == obj.max_delivery_days:
            return f'{obj.min_delivery_days} ngày'
        return f'{obj.min_delivery_days}-{obj.max_delivery_days} ngày'


class ShippingZoneSerializer(serializers.ModelSerializer):
    """Serializer for shipping zones."""

    class Meta:
        model = ShippingZone
        fields = [
            'id',
            'name',
            'provinces',
            'districts'
        ]


class ShippingRateSerializer(serializers.ModelSerializer):
    """Serializer for shipping rates."""
    
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    zone_name = serializers.CharField(source='zone.name', read_only=True)

    class Meta:
        model = ShippingRate
        fields = [
            'id',
            'provider',
            'provider_name',
            'zone',
            'zone_name',
            'service_code',
            'service_name',
            'base_rate',
            'rate_per_kg',
            'rate_per_item',
            'min_charge',
            'max_weight',
            'free_shipping_threshold'
        ]


class ShippingMethodSerializer(serializers.ModelSerializer):
    """Serializer for shipping methods (calculated rates)."""

    class Meta:
        model = ShippingMethod
        fields = [
            'id',
            'order',
            'provider',
            'service_code',
            'service_name',
            'shipping_cost',
            'estimated_delivery',
            'tracking_number',
            'tracking_url'
        ]


class CalculateShippingSerializer(serializers.Serializer):
    """Serializer for shipping calculation request."""
    
    # Destination address
    province = serializers.CharField(max_length=100, required=False)
    province_code = serializers.CharField(max_length=10, required=False)
    district = serializers.CharField(max_length=100, required=False)
    district_id = serializers.IntegerField(required=False)
    ward = serializers.CharField(max_length=100, required=False)
    ward_code = serializers.CharField(max_length=20, required=False)
    
    # Package info
    weight = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        help_text='Total weight in kg'
    )
    total_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        help_text='Total order value'
    )
    item_count = serializers.IntegerField(required=False, default=1)
    
    # Optional dimensions
    length = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    width = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    height = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    def validate(self, attrs):
        """Validate at least some location info is provided."""
        has_location = any([
            attrs.get('province'),
            attrs.get('province_code'),
            attrs.get('district'),
            attrs.get('district_id')
        ])
        
        if not has_location:
            raise serializers.ValidationError(
                _('Please provide destination address information')
            )
        
        return attrs


class ShippingOptionSerializer(serializers.Serializer):
    """Serializer for shipping option returned from calculation."""
    
    provider_code = serializers.CharField()
    provider_name = serializers.CharField()
    provider_logo = serializers.URLField(allow_null=True)
    service_code = serializers.CharField(allow_null=True)
    service_name = serializers.CharField()
    rate = serializers.DecimalField(max_digits=15, decimal_places=2)
    original_rate = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    is_free = serializers.BooleanField()
    delivery_estimate = serializers.CharField()
    min_delivery_days = serializers.IntegerField()
    max_delivery_days = serializers.IntegerField()


class ShippingCalculationResultSerializer(serializers.Serializer):
    """Serializer for shipping calculation result."""
    
    options = ShippingOptionSerializer(many=True)
    default_option = ShippingOptionSerializer(allow_null=True)
    free_shipping_threshold = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        allow_null=True
    )
    amount_for_free_shipping = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        allow_null=True
    )
