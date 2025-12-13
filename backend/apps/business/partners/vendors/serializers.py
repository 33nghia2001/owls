"""
Vendor Serializers for Owls E-commerce Platform
===============================================
"""

from rest_framework import serializers
from .models import Vendor, VendorDocument, VendorBankAccount


class VendorListSerializer(serializers.ModelSerializer):
    """Vendor list serializer (public)."""

    class Meta:
        model = Vendor
        fields = [
            'id', 'store_name', 'slug', 'description', 'logo',
            'city', 'rating', 'total_reviews', 'total_products'
        ]


class VendorDetailSerializer(serializers.ModelSerializer):
    """Vendor detail serializer (public)."""

    class Meta:
        model = Vendor
        fields = [
            'id', 'store_name', 'slug', 'description', 'logo', 'banner',
            'city', 'country', 'rating', 'total_reviews', 'total_products',
            'total_orders', 'return_policy', 'shipping_policy', 'created_at'
        ]


class VendorProfileSerializer(serializers.ModelSerializer):
    """Vendor profile serializer (for vendor owner)."""
    
    owner_email = serializers.CharField(source='owner.email', read_only=True)

    class Meta:
        model = Vendor
        fields = [
            'id', 'store_name', 'slug', 'description', 'logo', 'banner',
            'email', 'phone', 'website', 'address', 'ward', 'district',
            'city', 'country', 'vendor_type', 'business_license', 'tax_id',
            'status', 'is_verified', 'commission_rate', 'rating',
            'total_reviews', 'total_products', 'total_orders', 'total_sales',
            'return_policy', 'shipping_policy', 'auto_confirm_orders',
            'owner_email', 'created_at', 'approved_at'
        ]
        read_only_fields = [
            'id', 'slug', 'status', 'is_verified', 'commission_rate',
            'rating', 'total_reviews', 'total_products', 'total_orders',
            'total_sales', 'created_at', 'approved_at'
        ]


class VendorRegistrationSerializer(serializers.ModelSerializer):
    """Vendor registration serializer."""

    class Meta:
        model = Vendor
        fields = [
            'store_name', 'description', 'logo', 'email', 'phone',
            'website', 'address', 'ward', 'district', 'city',
            'vendor_type', 'business_license', 'tax_id'
        ]

    def validate_store_name(self, value):
        if Vendor.objects.filter(store_name__iexact=value).exists():
            raise serializers.ValidationError('A store with this name already exists.')
        return value


class VendorDocumentSerializer(serializers.ModelSerializer):
    """Vendor document serializer."""

    class Meta:
        model = VendorDocument
        fields = [
            'id', 'document_type', 'title', 'file',
            'is_verified', 'verified_at', 'created_at'
        ]
        read_only_fields = ['id', 'is_verified', 'verified_at', 'created_at']


class VendorBankAccountSerializer(serializers.ModelSerializer):
    """Vendor bank account serializer."""

    class Meta:
        model = VendorBankAccount
        fields = [
            'id', 'bank_name', 'account_name', 'account_number',
            'branch', 'swift_code', 'is_default', 'is_verified'
        ]
        read_only_fields = ['id', 'is_verified']


class VendorDashboardSerializer(serializers.Serializer):
    """Vendor dashboard statistics serializer."""
    
    total_products = serializers.IntegerField()
    total_orders = serializers.IntegerField()
    total_sales = serializers.DecimalField(max_digits=15, decimal_places=2)
    pending_orders = serializers.IntegerField()
    rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    total_reviews = serializers.IntegerField()
    recent_orders = serializers.ListField()
    top_products = serializers.ListField()
