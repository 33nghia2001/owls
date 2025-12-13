"""
Reviews Serializers for Owls E-commerce Platform
================================================
"""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Review, ReviewImage, ReviewVote


class ReviewImageSerializer(serializers.ModelSerializer):
    """Serializer for review images."""

    class Meta:
        model = ReviewImage
        fields = ['id', 'image', 'caption', 'order']
        read_only_fields = ['id']


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for reviews."""
    
    images = ReviewImageSerializer(many=True, read_only=True)
    user_name = serializers.SerializerMethodField()
    user_avatar = serializers.SerializerMethodField()
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id',
            'user_name',
            'user_avatar',
            'product',
            'product_name',
            'rating',
            'title',
            'content',
            'quality_rating',
            'value_rating',
            'shipping_rating',
            'pros',
            'cons',
            'is_verified_purchase',
            'helpful_count',
            'not_helpful_count',
            'admin_response',
            'admin_response_at',
            'images',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 'is_verified_purchase', 'helpful_count',
            'not_helpful_count', 'admin_response', 'admin_response_at',
            'created_at', 'updated_at'
        ]

    def get_user_name(self, obj):
        """Get user display name (anonymized)."""
        name = obj.user.get_full_name() or obj.user.email
        # Partially hide email/name
        if '@' in name:
            parts = name.split('@')
            return f"{parts[0][:2]}***@{parts[1]}"
        return f"{name[:2]}***"

    def get_user_avatar(self, obj):
        """Get user avatar URL."""
        if hasattr(obj.user, 'profile') and obj.user.profile.avatar:
            return obj.user.profile.avatar.url
        return None


class CreateReviewSerializer(serializers.ModelSerializer):
    """Serializer for creating a review."""
    
    product_id = serializers.UUIDField()
    order_id = serializers.UUIDField(required=False, allow_null=True)
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        max_length=5
    )

    class Meta:
        model = Review
        fields = [
            'product_id',
            'order_id',
            'rating',
            'title',
            'content',
            'quality_rating',
            'value_rating',
            'shipping_rating',
            'pros',
            'cons',
            'images'
        ]

    def validate_product_id(self, value):
        """Validate product exists."""
        from apps.business.commerce.products.models import Product
        
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError(_('Product not found'))
        return value

    def validate_order_id(self, value):
        """Validate order exists and belongs to user."""
        if not value:
            return value
            
        from apps.business.commerce.orders.models import Order
        
        user = self.context['request'].user
        if not Order.objects.filter(id=value, user=user).exists():
            raise serializers.ValidationError(_('Order not found'))
        return value

    def validate(self, attrs):
        """Validate user hasn't already reviewed this product."""
        user = self.context['request'].user
        product_id = attrs.get('product_id')
        
        if Review.objects.filter(user=user, product_id=product_id).exists():
            raise serializers.ValidationError({
                'product_id': _('You have already reviewed this product')
            })
        
        return attrs

    def create(self, validated_data):
        """Create review with images."""
        images_data = validated_data.pop('images', [])
        product_id = validated_data.pop('product_id')
        order_id = validated_data.pop('order_id', None)
        
        from apps.business.commerce.products.models import Product
        from apps.business.commerce.orders.models import Order, OrderItem
        
        user = self.context['request'].user
        product = Product.objects.get(id=product_id)
        
        # Check if verified purchase
        is_verified = False
        order = None
        
        if order_id:
            try:
                order = Order.objects.get(id=order_id, user=user)
                # Check product is in order
                if OrderItem.objects.filter(order=order, product=product).exists():
                    is_verified = True
            except Order.DoesNotExist:
                pass
        else:
            # Check if user has any delivered order with this product
            is_verified = OrderItem.objects.filter(
                order__user=user,
                order__status=Order.Status.DELIVERED,
                product=product
            ).exists()
        
        # Create review
        review = Review.objects.create(
            user=user,
            product=product,
            order=order,
            is_verified_purchase=is_verified,
            **validated_data
        )
        
        # Create images
        for idx, image in enumerate(images_data):
            ReviewImage.objects.create(
                review=review,
                image=image,
                order=idx
            )
        
        return review


class UpdateReviewSerializer(serializers.ModelSerializer):
    """Serializer for updating a review."""

    class Meta:
        model = Review
        fields = [
            'rating',
            'title',
            'content',
            'quality_rating',
            'value_rating',
            'shipping_rating',
            'pros',
            'cons'
        ]


class ReviewVoteSerializer(serializers.Serializer):
    """Serializer for voting on review helpfulness."""
    
    is_helpful = serializers.BooleanField()


class ProductReviewSummarySerializer(serializers.Serializer):
    """Serializer for product review summary/statistics."""
    
    total_reviews = serializers.IntegerField()
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    rating_distribution = serializers.DictField(
        child=serializers.IntegerField()
    )
    verified_purchase_count = serializers.IntegerField()
    with_images_count = serializers.IntegerField()


class AdminReviewResponseSerializer(serializers.Serializer):
    """Serializer for admin/vendor response to review."""
    
    response = serializers.CharField(max_length=2000)
