"""
Recommendations Serializers for Owls E-commerce Platform
========================================================
"""

from rest_framework import serializers
from .models import (
    ProductSimilarity, FrequentlyBoughtTogether,
    UserProductInteraction, UserPreference,
    RecommendationSet, RecommendationClick, RecommendationType
)


class ProductSimilaritySerializer(serializers.ModelSerializer):
    """Serializer for product similarity."""

    class Meta:
        model = ProductSimilarity
        fields = [
            'id', 'product_id', 'similar_product_id', 'similarity_score',
            'category_match', 'brand_match'
        ]


class FrequentlyBoughtTogetherSerializer(serializers.ModelSerializer):
    """Serializer for frequently bought together."""

    class Meta:
        model = FrequentlyBoughtTogether
        fields = ['id', 'product_id', 'related_product_id', 'co_purchase_count', 'confidence_score']


class UserProductInteractionSerializer(serializers.ModelSerializer):
    """Serializer for user product interactions."""

    class Meta:
        model = UserProductInteraction
        fields = ['id', 'product_id', 'interaction_type', 'created_at']


class RecordInteractionSerializer(serializers.Serializer):
    """Serializer for recording a user interaction."""

    product_id = serializers.UUIDField()
    interaction_type = serializers.ChoiceField(
        choices=UserProductInteraction.InteractionType.choices
    )
    source = serializers.CharField(required=False, allow_blank=True)


class UserPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for user preferences."""

    class Meta:
        model = UserPreference
        fields = [
            'preferred_categories', 'preferred_brands',
            'avg_price_preference', 'price_range_min', 'price_range_max',
            'last_computed_at'
        ]
        read_only_fields = fields


class RecommendationRequestSerializer(serializers.Serializer):
    """Serializer for recommendation requests."""

    recommendation_type = serializers.ChoiceField(choices=RecommendationType.choices)
    product_id = serializers.UUIDField(required=False)
    category_id = serializers.UUIDField(required=False)
    limit = serializers.IntegerField(default=12, min_value=1, max_value=50)


class RecommendationResponseSerializer(serializers.Serializer):
    """Serializer for recommendation responses."""

    recommendation_type = serializers.CharField()
    title = serializers.CharField()
    products = serializers.ListField()
    source_product_id = serializers.UUIDField(required=False, allow_null=True)


class RecommendationClickSerializer(serializers.Serializer):
    """Serializer for recording recommendation clicks."""

    recommendation_type = serializers.ChoiceField(choices=RecommendationType.choices)
    source_product_id = serializers.UUIDField(required=False, allow_null=True)
    clicked_product_id = serializers.UUIDField()
    position = serializers.IntegerField()


class RecentlyViewedSerializer(serializers.Serializer):
    """Serializer for recently viewed products."""

    product_id = serializers.UUIDField()
    viewed_at = serializers.DateTimeField()


class PersonalizedHomeSerializer(serializers.Serializer):
    """Serializer for personalized homepage recommendations."""

    recently_viewed = serializers.ListField()
    personalized = serializers.ListField()
    trending = serializers.ListField()
    based_on_cart = serializers.ListField(required=False)
    based_on_wishlist = serializers.ListField(required=False)
