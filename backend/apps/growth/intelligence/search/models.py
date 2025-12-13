"""
Search Models for Owls E-commerce Platform
==========================================
Search history, suggestions, and analytics.
"""

import uuid
from django.db import models
from django.conf import settings
from apps.base.core.users.models import TimeStampedModel


class SearchQuery(TimeStampedModel):
    """
    Record of user search queries.
    Used for analytics and improving search results.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='search_queries'
    )
    session_id = models.CharField(max_length=100, blank=True)
    query = models.CharField(max_length=500)
    query_normalized = models.CharField(max_length=500, blank=True)

    # Results info
    results_count = models.PositiveIntegerField(default=0)
    clicked_product_ids = models.JSONField(default=list)

    # Context
    category_filter = models.CharField(max_length=100, blank=True)
    price_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    price_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    filters_applied = models.JSONField(default=dict)

    # Device info
    device_type = models.CharField(max_length=20, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = 'search_queries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['query']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"Search: {self.query}"


class SearchSuggestion(TimeStampedModel):
    """
    Pre-computed search suggestions.
    Can be auto-generated or manually curated.
    """

    class SuggestionType(models.TextChoices):
        POPULAR = 'popular', 'Popular Search'
        TRENDING = 'trending', 'Trending'
        CURATED = 'curated', 'Manually Curated'
        AUTOCOMPLETE = 'autocomplete', 'Autocomplete'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    term = models.CharField(max_length=200, unique=True)
    suggestion_type = models.CharField(
        max_length=20,
        choices=SuggestionType.choices,
        default=SuggestionType.POPULAR
    )

    # Ranking
    search_count = models.PositiveIntegerField(default=0)
    click_through_count = models.PositiveIntegerField(default=0)
    priority = models.PositiveIntegerField(default=0)

    # Optional category association
    category = models.CharField(max_length=100, blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'search_suggestions'
        ordering = ['-search_count', '-priority']
        indexes = [
            models.Index(fields=['term']),
            models.Index(fields=['suggestion_type', 'is_active']),
        ]

    def __str__(self):
        return self.term


class SearchSynonym(TimeStampedModel):
    """
    Search synonyms for better matching.
    Maps alternative terms to canonical terms.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    term = models.CharField(max_length=100)
    synonyms = models.JSONField(
        default=list,
        help_text='List of synonymous terms'
    )
    is_bidirectional = models.BooleanField(
        default=True,
        help_text='If True, synonyms work both ways'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'search_synonyms'
        ordering = ['term']

    def __str__(self):
        return f"{self.term} -> {', '.join(self.synonyms)}"


class SearchBoost(TimeStampedModel):
    """
    Boost specific products or categories in search results.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Target
    search_term = models.CharField(
        max_length=200, blank=True,
        help_text='Apply boost when this term is searched'
    )
    boost_category = models.CharField(max_length=100, blank=True)
    boost_product_ids = models.JSONField(default=list)

    # Boost settings
    boost_factor = models.FloatField(
        default=1.5,
        help_text='Multiplier for relevance score'
    )

    # Scheduling
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'search_boosts'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class SearchFilter(TimeStampedModel):
    """
    Dynamic search filters configuration.
    """

    class FilterType(models.TextChoices):
        CATEGORY = 'category', 'Category'
        BRAND = 'brand', 'Brand'
        PRICE_RANGE = 'price_range', 'Price Range'
        RATING = 'rating', 'Rating'
        ATTRIBUTE = 'attribute', 'Product Attribute'
        AVAILABILITY = 'availability', 'Availability'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    filter_type = models.CharField(
        max_length=20,
        choices=FilterType.choices
    )
    display_name = models.CharField(max_length=100)
    attribute_key = models.CharField(
        max_length=100, blank=True,
        help_text='For attribute filters, the attribute key to filter on'
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'search_filters'
        ordering = ['order']

    def __str__(self):
        return f"{self.display_name} ({self.filter_type})"
