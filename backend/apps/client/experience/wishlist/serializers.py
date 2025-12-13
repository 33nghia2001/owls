"""
Wishlist Serializers for Owls E-commerce Platform
=================================================
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Wishlist, WishlistItem
from apps.business.commerce.products.serializers import ProductListSerializer


class WishlistItemSerializer(serializers.ModelSerializer):
    """Serializer for wishlist items."""
    
    product = ProductListSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)
    variant_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    current_price = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    price_dropped = serializers.BooleanField(read_only=True)
    price_change = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = WishlistItem
        fields = [
            'id',
            'product',
            'product_id',
            'variant_id',
            'price_when_added',
            'current_price',
            'price_dropped',
            'price_change',
            'notes',
            'created_at'
        ]
        read_only_fields = ['id', 'price_when_added', 'created_at']


class AddToWishlistSerializer(serializers.Serializer):
    """Serializer for adding product to wishlist."""
    
    product_id = serializers.UUIDField()
    variant_id = serializers.UUIDField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate_product_id(self, value):
        """Validate product exists and is published."""
        from apps.business.commerce.products.models import Product
        
        try:
            product = Product.objects.get(
                id=value,
                status=Product.Status.PUBLISHED
            )
        except Product.DoesNotExist:
            raise serializers.ValidationError(_('Product not found or unavailable'))
        
        return value

    def validate(self, attrs):
        """Validate variant belongs to product if provided."""
        product_id = attrs.get('product_id')
        variant_id = attrs.get('variant_id')
        
        if variant_id:
            from apps.business.commerce.products.models import ProductVariant
            
            if not ProductVariant.objects.filter(
                id=variant_id,
                product_id=product_id,
                is_active=True
            ).exists():
                raise serializers.ValidationError({
                    'variant_id': _('Variant not found or does not belong to this product')
                })
        
        return attrs


class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for wishlist."""
    
    items = WishlistItemSerializer(many=True, read_only=True)
    item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Wishlist
        fields = [
            'id',
            'name',
            'is_public',
            'item_count',
            'items',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WishlistSummarySerializer(serializers.ModelSerializer):
    """Summary serializer for wishlist (without items)."""
    
    item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'name', 'is_public', 'item_count']
