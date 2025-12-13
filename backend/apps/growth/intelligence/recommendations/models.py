"""
Recommendation Models for Owls E-commerce Platform
==================================================
Product recommendations, personalization, and ML models.
"""

import uuid
from django.db import models
from django.conf import settings
from apps.base.core.users.models import TimeStampedModel


class RecommendationType(models.TextChoices):
    """Types of recommendation algorithms."""
    SIMILAR_PRODUCTS = 'similar', 'Similar Products'
    FREQUENTLY_BOUGHT = 'frequently_bought', 'Frequently Bought Together'
    CUSTOMERS_ALSO_VIEWED = 'also_viewed', 'Customers Also Viewed'
    PERSONALIZED = 'personalized', 'Personalized For You'
    TRENDING = 'trending', 'Trending Now'
    NEW_ARRIVALS = 'new_arrivals', 'New Arrivals'
    BEST_SELLERS = 'best_sellers', 'Best Sellers'
    RECENTLY_VIEWED = 'recently_viewed', 'Recently Viewed'
    BASED_ON_CART = 'cart_based', 'Based On Your Cart'
    BASED_ON_WISHLIST = 'wishlist_based', 'Based On Your Wishlist'


class ProductSimilarity(TimeStampedModel):
    """
    Pre-computed product similarity scores.
    Used for "Similar Products" recommendations.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_id = models.UUIDField(db_index=True)
    similar_product_id = models.UUIDField()
    similarity_score = models.FloatField(
        help_text='Similarity score between 0 and 1'
    )

    # Similarity factors
    category_match = models.BooleanField(default=False)
    brand_match = models.BooleanField(default=False)
    price_similarity = models.FloatField(default=0)
    attribute_similarity = models.FloatField(default=0)

    class Meta:
        db_table = 'product_similarities'
        unique_together = ['product_id', 'similar_product_id']
        ordering = ['-similarity_score']
        indexes = [
            models.Index(fields=['product_id', '-similarity_score']),
        ]

    def __str__(self):
        return f"Similarity: {self.product_id} -> {self.similar_product_id}"


class FrequentlyBoughtTogether(TimeStampedModel):
    """
    Products frequently purchased together.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_id = models.UUIDField(db_index=True)
    related_product_id = models.UUIDField()
    co_purchase_count = models.PositiveIntegerField(default=0)
    confidence_score = models.FloatField(
        default=0,
        help_text='Confidence that these products are bought together'
    )

    class Meta:
        db_table = 'frequently_bought_together'
        unique_together = ['product_id', 'related_product_id']
        ordering = ['-co_purchase_count']
        indexes = [
            models.Index(fields=['product_id', '-co_purchase_count']),
        ]

    def __str__(self):
        return f"FBT: {self.product_id} + {self.related_product_id}"


class UserProductInteraction(TimeStampedModel):
    """
    Track user interactions with products for personalization.
    """

    class InteractionType(models.TextChoices):
        VIEW = 'view', 'Viewed'
        CLICK = 'click', 'Clicked'
        ADD_TO_CART = 'add_cart', 'Added to Cart'
        ADD_TO_WISHLIST = 'add_wishlist', 'Added to Wishlist'
        PURCHASE = 'purchase', 'Purchased'
        REVIEW = 'review', 'Reviewed'
        SHARE = 'share', 'Shared'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='product_interactions'
    )
    product_id = models.UUIDField()
    interaction_type = models.CharField(
        max_length=20,
        choices=InteractionType.choices
    )
    interaction_weight = models.FloatField(
        default=1.0,
        help_text='Weight of this interaction for scoring'
    )

    # Context
    session_id = models.CharField(max_length=100, blank=True)
    source = models.CharField(max_length=50, blank=True)  # e.g., 'search', 'category', 'recommendation'

    class Meta:
        db_table = 'user_product_interactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['product_id', '-created_at']),
            models.Index(fields=['user', 'interaction_type']),
        ]

    def __str__(self):
        return f"{self.user} - {self.interaction_type} - {self.product_id}"


class UserPreference(TimeStampedModel):
    """
    Computed user preferences based on behavior.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recommendation_preferences'
    )

    # Category preferences
    preferred_categories = models.JSONField(
        default=dict,
        help_text='Category ID -> preference score'
    )

    # Brand preferences
    preferred_brands = models.JSONField(
        default=dict,
        help_text='Brand ID -> preference score'
    )

    # Price preference
    avg_price_preference = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True
    )
    price_range_min = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True
    )
    price_range_max = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True
    )

    # Attribute preferences
    attribute_preferences = models.JSONField(default=dict)

    # Computed embeddings for ML
    user_embedding = models.JSONField(
        default=list,
        help_text='User embedding vector for ML recommendations'
    )

    last_computed_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_preferences'

    def __str__(self):
        return f"Preferences for {self.user}"


class RecommendationSet(TimeStampedModel):
    """
    Pre-computed recommendation sets for quick retrieval.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recommendation_type = models.CharField(
        max_length=30,
        choices=RecommendationType.choices
    )

    # Target
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='recommendation_sets'
    )
    product_id = models.UUIDField(null=True, blank=True)
    category_id = models.UUIDField(null=True, blank=True)

    # Recommended products
    recommended_product_ids = models.JSONField(default=list)
    scores = models.JSONField(
        default=list,
        help_text='Recommendation scores for each product'
    )

    # Validity
    expires_at = models.DateTimeField()
    is_valid = models.BooleanField(default=True)

    class Meta:
        db_table = 'recommendation_sets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recommendation_type', 'user']),
            models.Index(fields=['recommendation_type', 'product_id']),
            models.Index(fields=['expires_at', 'is_valid']),
        ]

    def __str__(self):
        return f"{self.get_recommendation_type_display()} - {self.user or self.product_id}"


class RecommendationClick(TimeStampedModel):
    """
    Track clicks on recommendations for analytics.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='recommendation_clicks'
    )
    session_id = models.CharField(max_length=100, blank=True)

    recommendation_type = models.CharField(
        max_length=30,
        choices=RecommendationType.choices
    )
    source_product_id = models.UUIDField(null=True, blank=True)
    clicked_product_id = models.UUIDField()
    position = models.PositiveIntegerField(
        help_text='Position in recommendation list when clicked'
    )

    # Did the click lead to a conversion?
    converted = models.BooleanField(default=False)

    class Meta:
        db_table = 'recommendation_clicks'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recommendation_type', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"Click: {self.recommendation_type} -> {self.clicked_product_id}"
