"""
Search Serializers for Owls E-commerce Platform
===============================================
"""

from rest_framework import serializers
from .models import SearchQuery, SearchSuggestion, SearchSynonym, SearchBoost, SearchFilter


class SearchQuerySerializer(serializers.ModelSerializer):
    """Serializer for search query records."""

    class Meta:
        model = SearchQuery
        fields = [
            'id', 'query', 'results_count', 'category_filter',
            'filters_applied', 'created_at'
        ]


class SearchSuggestionSerializer(serializers.ModelSerializer):
    """Serializer for search suggestions."""

    class Meta:
        model = SearchSuggestion
        fields = ['id', 'term', 'suggestion_type', 'category']


class SearchHistorySerializer(serializers.Serializer):
    """Serializer for user's search history."""

    query = serializers.CharField()
    search_count = serializers.IntegerField()
    last_searched = serializers.DateTimeField()


class AutocompleteResultSerializer(serializers.Serializer):
    """Serializer for autocomplete results."""

    type = serializers.CharField()  # 'suggestion', 'product', 'category', 'brand'
    term = serializers.CharField()
    highlight = serializers.CharField(required=False)
    category = serializers.CharField(required=False)
    url = serializers.CharField(required=False)


class SearchFilterSerializer(serializers.ModelSerializer):
    """Serializer for search filters."""

    class Meta:
        model = SearchFilter
        fields = ['id', 'name', 'filter_type', 'display_name', 'attribute_key']


class SearchFilterOptionSerializer(serializers.Serializer):
    """Serializer for filter options with counts."""

    value = serializers.CharField()
    label = serializers.CharField()
    count = serializers.IntegerField()


class SearchResultsSerializer(serializers.Serializer):
    """Serializer for complete search results."""

    query = serializers.CharField()
    total_count = serializers.IntegerField()
    page = serializers.IntegerField()
    per_page = serializers.IntegerField()
    products = serializers.ListField()
    filters = serializers.DictField()
    suggestions = serializers.ListField(required=False)
    did_you_mean = serializers.CharField(required=False, allow_null=True)


class RecordSearchSerializer(serializers.Serializer):
    """Serializer for recording a search query."""

    query = serializers.CharField(max_length=500)
    results_count = serializers.IntegerField(default=0)
    category_filter = serializers.CharField(required=False, allow_blank=True)
    filters_applied = serializers.DictField(required=False, default=dict)


class SearchClickSerializer(serializers.Serializer):
    """Serializer for recording search result clicks."""

    query = serializers.CharField(max_length=500)
    product_id = serializers.UUIDField()
    position = serializers.IntegerField()
