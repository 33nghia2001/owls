"""
Payment Serializers for Owls E-commerce Platform
================================================
"""

from rest_framework import serializers
from .models import PaymentMethod, Payment, Refund


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Payment method serializer."""

    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'code', 'name', 'description', 'icon',
            'gateway', 'is_active', 'min_amount', 'max_amount'
        ]


class PaymentSerializer(serializers.ModelSerializer):
    """Payment serializer."""
    
    payment_method = PaymentMethodSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'transaction_id', 'order', 'payment_method',
            'currency', 'amount', 'fee', 'net_amount', 'status',
            'error_message', 'created_at', 'paid_at'
        ]


class CreatePaymentSerializer(serializers.Serializer):
    """Serializer for creating payment."""
    
    order_id = serializers.UUIDField()
    payment_method_code = serializers.CharField(max_length=50)
    return_url = serializers.URLField(required=False)


class VerifyPaymentSerializer(serializers.Serializer):
    """Serializer for verifying payment."""
    
    gateway_data = serializers.JSONField()


class RefundSerializer(serializers.ModelSerializer):
    """Refund serializer."""

    class Meta:
        model = Refund
        fields = [
            'id', 'refund_number', 'payment', 'order',
            'amount', 'status', 'reason', 'reason_detail',
            'created_at', 'processed_at'
        ]


class CreateRefundSerializer(serializers.Serializer):
    """Serializer for creating refund."""
    
    order_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    reason = serializers.ChoiceField(choices=Refund.Reason.choices)
    reason_detail = serializers.CharField(max_length=1000, required=False)
