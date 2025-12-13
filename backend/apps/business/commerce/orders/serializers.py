"""
Order Serializers for Owls E-commerce Platform
==============================================
"""

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Order, OrderItem, OrderStatusHistory, OrderShipment
from apps.business.commerce.products.serializers import ProductListSerializer
from apps.base.core.users.serializers import UserAddressSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """Order item serializer."""

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_name', 'product_sku', 'product_image',
            'variant_name', 'selected_options', 'quantity',
            'unit_price', 'discount_amount', 'total_price',
            'vendor', 'status'
        ]


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    """Order status history serializer."""

    class Meta:
        model = OrderStatusHistory
        fields = ['id', 'old_status', 'new_status', 'note', 'created_at']


class OrderShipmentSerializer(serializers.ModelSerializer):
    """Order shipment serializer."""

    class Meta:
        model = OrderShipment
        fields = [
            'id', 'tracking_number', 'carrier', 'carrier_code',
            'tracking_url', 'status', 'shipped_at',
            'estimated_delivery', 'delivered_at'
        ]


class OrderListSerializer(serializers.ModelSerializer):
    """Order list serializer (simplified)."""
    
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'payment_status',
            'total', 'item_count', 'created_at'
        ]

    @extend_schema_field(int)
    def get_item_count(self, obj) -> int:
        return obj.items.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    """Order detail serializer (full information)."""
    
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    shipments = OrderShipmentSerializer(many=True, read_only=True)
    can_cancel = serializers.SerializerMethodField()
    can_refund = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'payment_status',
            'currency', 'subtotal', 'discount_amount', 'shipping_amount',
            'tax_amount', 'total', 'coupon_code',
            'shipping_name', 'shipping_phone', 'shipping_address_line',
            'shipping_city', 'shipping_country',
            'customer_note', 'items', 'status_history', 'shipments',
            'can_cancel', 'can_refund',
            'created_at', 'paid_at', 'shipped_at', 'delivered_at'
        ]

    @extend_schema_field(bool)
    def get_can_cancel(self, obj) -> bool:
        return obj.can_cancel

    @extend_schema_field(bool)
    def get_can_refund(self, obj) -> bool:
        return obj.can_refund


class CreateOrderSerializer(serializers.Serializer):
    """Serializer for creating order from cart."""
    
    shipping_address_id = serializers.IntegerField()
    billing_address_id = serializers.IntegerField(required=False, allow_null=True)
    payment_method = serializers.CharField(max_length=50)
    customer_note = serializers.CharField(max_length=1000, required=False, allow_blank=True)


class CancelOrderSerializer(serializers.Serializer):
    """Serializer for cancelling order."""
    
    reason = serializers.CharField(max_length=500)
