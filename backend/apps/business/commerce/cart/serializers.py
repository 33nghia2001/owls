"""
Cart Serializers for Owls E-commerce Platform
=============================================
"""

from rest_framework import serializers
from .models import Cart, CartItem
from apps.business.commerce.products.serializers import ProductListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """Cart item serializer."""
    
    product = ProductListSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)
    variant_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_id', 'variant_id',
            'quantity', 'unit_price', 'total_price', 'selected_options'
        ]
        read_only_fields = ['id', 'unit_price', 'total_price']


class CartSerializer(serializers.ModelSerializer):
    """Cart serializer."""
    
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = [
            'id', 'subtotal', 'discount_amount', 'tax_amount',
            'shipping_amount', 'total', 'item_count', 'currency',
            'coupon', 'notes', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'subtotal', 'discount_amount', 'tax_amount',
            'total', 'item_count', 'created_at', 'updated_at'
        ]


class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding items to cart."""
    
    product_id = serializers.UUIDField()
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1, default=1)
    selected_options = serializers.JSONField(required=False, default=dict)


class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity."""
    
    quantity = serializers.IntegerField(min_value=0)


class ApplyCouponSerializer(serializers.Serializer):
    """Serializer for applying coupon to cart."""
    
    coupon_code = serializers.CharField(max_length=50)
