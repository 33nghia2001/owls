"""
Product Serializers for Owls E-commerce Platform
================================================
"""

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from .models import (
    Category, Brand, Product, ProductImage, ProductVariant,
    ProductAttribute, ProductAttributeValue
)


class CategorySerializer(serializers.ModelSerializer):
    """Category serializer."""
    
    children = serializers.SerializerMethodField()
    full_path = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'image', 'icon',
            'parent', 'level', 'path', 'full_path', 'is_featured',
            'show_in_menu', 'product_count', 'children'
        ]

    @extend_schema_field(list)
    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.filter(is_active=True), many=True).data
        return []

    @extend_schema_field(str)
    def get_full_path(self, obj) -> str:
        return obj.full_path or ''


class CategoryListSerializer(serializers.ModelSerializer):
    """Simplified category serializer for lists."""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'product_count']


class BrandSerializer(serializers.ModelSerializer):
    """Brand serializer."""

    class Meta:
        model = Brand
        fields = [
            'id', 'name', 'slug', 'description', 'logo',
            'website', 'is_featured', 'product_count'
        ]


class ProductImageSerializer(serializers.ModelSerializer):
    """Product image serializer."""

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'order']


class ProductVariantSerializer(serializers.ModelSerializer):
    """Product variant serializer."""

    class Meta:
        model = ProductVariant
        fields = [
            'id', 'name', 'sku', 'price', 'compare_at_price',
            'stock_quantity', 'attributes', 'image', 'is_active'
        ]


class ProductListSerializer(serializers.ModelSerializer):
    """Product list serializer (optimized for listing)."""
    
    category = CategoryListSerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    is_on_sale = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    is_in_stock = serializers.SerializerMethodField()
    vendor_name = serializers.CharField(source='vendor.store_name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'sku',
            'category', 'brand', 'price', 'compare_at_price',
            'primary_image', 'rating', 'review_count', 'sold_count',
            'is_on_sale', 'discount_percentage', 'is_in_stock',
            'is_featured', 'is_bestseller', 'is_new_arrival',
            'vendor_name', 'created_at'
        ]

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_primary_image(self, obj):
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            return ProductImageSerializer(primary).data
        first_image = obj.images.first()
        return ProductImageSerializer(first_image).data if first_image else None

    @extend_schema_field(bool)
    def get_is_on_sale(self, obj) -> bool:
        return obj.is_on_sale

    @extend_schema_field(int)
    def get_discount_percentage(self, obj) -> int:
        return obj.discount_percentage or 0

    @extend_schema_field(bool)
    def get_is_in_stock(self, obj) -> bool:
        return obj.is_in_stock


class ProductDetailSerializer(serializers.ModelSerializer):
    """Product detail serializer (full information)."""
    
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    is_on_sale = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    is_in_stock = serializers.SerializerMethodField()
    effective_price = serializers.SerializerMethodField()
    vendor = serializers.SerializerMethodField()
    related_products = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'description',
            'sku', 'barcode', 'category', 'brand', 'tags',
            'product_type', 'status', 'price', 'compare_at_price',
            'effective_price', 'track_inventory', 'stock_quantity',
            'weight', 'length', 'width', 'height', 'requires_shipping',
            'meta_title', 'meta_description', 'rating', 'review_count',
            'view_count', 'sold_count', 'is_on_sale', 'discount_percentage',
            'is_in_stock', 'is_featured', 'is_bestseller', 'is_new_arrival',
            'images', 'variants', 'vendor', 'related_products',
            'created_at', 'published_at'
        ]

    @extend_schema_field(bool)
    def get_is_on_sale(self, obj) -> bool:
        return obj.is_on_sale

    @extend_schema_field(int)
    def get_discount_percentage(self, obj) -> int:
        return obj.discount_percentage or 0

    @extend_schema_field(bool)
    def get_is_in_stock(self, obj) -> bool:
        return obj.is_in_stock

    @extend_schema_field(OpenApiTypes.DECIMAL)
    def get_effective_price(self, obj):
        return obj.effective_price

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_vendor(self, obj):
        return {
            'id': str(obj.vendor.id),
            'store_name': obj.vendor.store_name,
            'slug': obj.vendor.slug,
            'logo': obj.vendor.logo.url if obj.vendor.logo else None,
            'rating': float(obj.vendor.rating),
            'total_products': obj.vendor.total_products,
        }

    @extend_schema_field(list)
    def get_related_products(self, obj):
        related = Product.objects.filter(
            category=obj.category,
            status=Product.Status.PUBLISHED,
            is_active=True
        ).exclude(id=obj.id)[:8]
        return ProductListSerializer(related, many=True).data


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Product create/update serializer for vendors."""
    
    images = ProductImageSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'short_description', 'description',
            'sku', 'barcode', 'category', 'brand', 'tags',
            'product_type', 'price', 'compare_at_price', 'cost_price',
            'track_inventory', 'stock_quantity', 'low_stock_threshold',
            'allow_backorder', 'weight', 'length', 'width', 'height',
            'requires_shipping', 'meta_title', 'meta_description',
            'is_taxable', 'images'
        ]

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        product = Product.objects.create(**validated_data)
        
        for idx, image_data in enumerate(images_data):
            ProductImage.objects.create(
                product=product,
                is_primary=(idx == 0),
                order=idx,
                **image_data
            )
        
        return product


class ProductAttributeSerializer(serializers.ModelSerializer):
    """Product attribute serializer."""
    
    values = serializers.SerializerMethodField()

    class Meta:
        model = ProductAttribute
        fields = ['id', 'name', 'code', 'attribute_type', 'is_filterable', 'values']

    @extend_schema_field(list)
    def get_values(self, obj):
        return ProductAttributeValueSerializer(obj.values.all(), many=True).data


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    """Product attribute value serializer."""

    class Meta:
        model = ProductAttributeValue
        fields = ['id', 'value', 'code', 'color_code', 'image']
