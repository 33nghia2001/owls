"""
Loyalty Serializers for Owls E-commerce Platform
================================================
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import LoyaltyTier, LoyaltyAccount, PointTransaction, Reward, RewardRedemption


class LoyaltyTierSerializer(serializers.ModelSerializer):
    """Serializer for loyalty tiers."""

    class Meta:
        model = LoyaltyTier
        fields = [
            'id', 'name', 'code', 'description',
            'min_points', 'min_spent',
            'points_multiplier', 'discount_percentage',
            'free_shipping', 'priority_support',
            'icon', 'color', 'badge_image'
        ]


class PointTransactionSerializer(serializers.ModelSerializer):
    """Serializer for point transactions."""
    
    order_number = serializers.CharField(source='order.order_number', read_only=True)

    class Meta:
        model = PointTransaction
        fields = [
            'id', 'transaction_type', 'points', 'description',
            'order', 'order_number', 'expires_at', 'is_expired',
            'created_at'
        ]


class LoyaltyAccountSerializer(serializers.ModelSerializer):
    """Serializer for loyalty account."""
    
    tier = LoyaltyTierSerializer(read_only=True)
    points_value = serializers.DecimalField(
        max_digits=15, decimal_places=2,
        source='get_points_value', read_only=True
    )
    recent_transactions = serializers.SerializerMethodField()

    class Meta:
        model = LoyaltyAccount
        fields = [
            'id', 'points_balance', 'points_earned_total',
            'points_spent_total', 'points_expired_total',
            'tier', 'tier_qualified_at',
            'total_orders', 'total_spent',
            'points_value', 'recent_transactions',
            'created_at'
        ]

    def get_recent_transactions(self, obj):
        """Get last 5 transactions."""
        transactions = obj.transactions.all()[:5]
        return PointTransactionSerializer(transactions, many=True).data


class LoyaltyAccountSummarySerializer(serializers.ModelSerializer):
    """Summary serializer for loyalty account."""
    
    tier_name = serializers.CharField(source='tier.name', read_only=True)
    points_value = serializers.DecimalField(
        max_digits=15, decimal_places=2,
        source='get_points_value', read_only=True
    )

    class Meta:
        model = LoyaltyAccount
        fields = [
            'points_balance', 'tier_name', 'points_value'
        ]


class RewardSerializer(serializers.ModelSerializer):
    """Serializer for rewards."""
    
    is_available = serializers.BooleanField(read_only=True)
    min_tier_name = serializers.CharField(source='min_tier.name', read_only=True)

    class Meta:
        model = Reward
        fields = [
            'id', 'name', 'description', 'reward_type',
            'points_required', 'discount_value', 'discount_percentage',
            'min_tier', 'min_tier_name',
            'quantity_available', 'quantity_redeemed',
            'starts_at', 'expires_at',
            'image', 'is_featured', 'is_available'
        ]


class RedeemRewardSerializer(serializers.Serializer):
    """Serializer for redeeming a reward."""
    
    reward_id = serializers.UUIDField()

    def validate_reward_id(self, value):
        """Validate reward exists and is available."""
        try:
            reward = Reward.objects.get(id=value)
        except Reward.DoesNotExist:
            raise serializers.ValidationError(_('Reward not found'))
        
        if not reward.is_available:
            raise serializers.ValidationError(_('This reward is no longer available'))
        
        return value


class RewardRedemptionSerializer(serializers.ModelSerializer):
    """Serializer for reward redemptions."""
    
    reward = RewardSerializer(read_only=True)

    class Meta:
        model = RewardRedemption
        fields = [
            'id', 'reward', 'points_spent', 'status',
            'voucher_code', 'used_at', 'used_on_order',
            'expires_at', 'created_at'
        ]


class EarnPointsSerializer(serializers.Serializer):
    """Serializer for earning points (admin use)."""
    
    user_id = serializers.UUIDField()
    points = serializers.IntegerField(min_value=1)
    description = serializers.CharField(max_length=255)
    transaction_type = serializers.ChoiceField(
        choices=['bonus', 'adjusted'],
        default='bonus'
    )
