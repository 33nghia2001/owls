"""
Coupons Serializers for Owls E-commerce Platform
================================================
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import Coupon, CouponUsage


class CouponSerializer(serializers.ModelSerializer):
    """Public coupon serializer (limited info)."""
    
    is_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = Coupon
        fields = [
            'id',
            'code',
            'name',
            'description',
            'discount_type',
            'discount_value',
            'max_discount',
            'min_order_amount',
            'starts_at',
            'expires_at',
            'is_valid'
        ]


class CouponDetailSerializer(serializers.ModelSerializer):
    """Detailed coupon serializer (for authenticated users)."""
    
    is_valid = serializers.BooleanField(read_only=True)
    user_usage_count = serializers.SerializerMethodField()
    can_use = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = [
            'id',
            'code',
            'name',
            'description',
            'discount_type',
            'discount_value',
            'max_discount',
            'min_order_amount',
            'usage_limit_per_user',
            'starts_at',
            'expires_at',
            'is_valid',
            'user_usage_count',
            'can_use'
        ]

    def get_user_usage_count(self, obj):
        """Get how many times current user has used this coupon."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return CouponUsage.objects.filter(
                coupon=obj,
                user=request.user
            ).count()
        return 0

    def get_can_use(self, obj):
        """Check if current user can use this coupon."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        if not obj.is_valid:
            return False
        
        usage_count = CouponUsage.objects.filter(
            coupon=obj,
            user=request.user
        ).count()
        
        return usage_count < obj.usage_limit_per_user


class ValidateCouponSerializer(serializers.Serializer):
    """Serializer for validating a coupon code."""
    
    code = serializers.CharField(max_length=50)
    subtotal = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)

    def validate_code(self, value):
        """Validate coupon code exists."""
        code = value.upper().strip()
        if not Coupon.objects.filter(code=code).exists():
            raise serializers.ValidationError(_('Invalid coupon code'))
        return code


class ApplyCouponSerializer(serializers.Serializer):
    """Serializer for applying a coupon to cart/order."""
    
    code = serializers.CharField(max_length=50)

    def validate_code(self, value):
        """Validate and return coupon."""
        code = value.upper().strip()
        
        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            raise serializers.ValidationError(_('Invalid coupon code'))
        
        # Check validity
        if not coupon.is_active:
            raise serializers.ValidationError(_('This coupon is no longer active'))
        
        now = timezone.now()
        if coupon.starts_at > now:
            raise serializers.ValidationError(_('This coupon is not yet valid'))
        
        if coupon.expires_at and coupon.expires_at < now:
            raise serializers.ValidationError(_('This coupon has expired'))
        
        if coupon.usage_limit and coupon.times_used >= coupon.usage_limit:
            raise serializers.ValidationError(_('This coupon has reached its usage limit'))
        
        # Check per-user limit
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user_usage = CouponUsage.objects.filter(
                coupon=coupon,
                user=request.user
            ).count()
            
            if user_usage >= coupon.usage_limit_per_user:
                raise serializers.ValidationError(
                    _('You have already used this coupon the maximum number of times')
                )
        
        return code


class CouponUsageSerializer(serializers.ModelSerializer):
    """Serializer for coupon usage history."""
    
    coupon_code = serializers.CharField(source='coupon.code', read_only=True)
    coupon_name = serializers.CharField(source='coupon.name', read_only=True)

    class Meta:
        model = CouponUsage
        fields = [
            'id',
            'coupon_code',
            'coupon_name',
            'discount_amount',
            'order',
            'used_at'
        ]


class CouponCalculationResultSerializer(serializers.Serializer):
    """Serializer for coupon calculation result."""
    
    valid = serializers.BooleanField()
    code = serializers.CharField()
    discount_type = serializers.CharField()
    discount_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    message = serializers.CharField(required=False)
