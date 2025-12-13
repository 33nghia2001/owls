"""
Product Filters for Owls E-commerce Platform
=============================================
"""

import django_filters
from django.db.models import Q, F
from .models import Product, Category, Brand


class ProductFilter(django_filters.FilterSet):
    """Filter for products."""
    
    category = django_filters.CharFilter(method='filter_category')
    brand = django_filters.CharFilter(field_name='brand__slug')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    rating = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    vendor = django_filters.CharFilter(field_name='vendor__slug')
    is_on_sale = django_filters.BooleanFilter(method='filter_on_sale')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    is_featured = django_filters.BooleanFilter()
    is_bestseller = django_filters.BooleanFilter()
    is_new_arrival = django_filters.BooleanFilter()

    class Meta:
        model = Product
        fields = [
            'category', 'brand', 'min_price', 'max_price', 'rating',
            'vendor', 'is_on_sale', 'in_stock', 'is_featured',
            'is_bestseller', 'is_new_arrival'
        ]

    def filter_category(self, queryset, name, value):
        """Filter by category slug, including subcategories."""
        try:
            category = Category.objects.get(slug=value, is_active=True)
            # Get category and all its descendants
            categories = Category.objects.filter(
                Q(pk=category.pk) | Q(path__startswith=f'{category.path}/')
            )
            return queryset.filter(category__in=categories)
        except Category.DoesNotExist:
            return queryset.none()

    def filter_on_sale(self, queryset, name, value):
        """Filter products on sale."""
        if value:
            return queryset.filter(
                compare_at_price__isnull=False,
                compare_at_price__gt=F('price')
            )
        return queryset

    def filter_in_stock(self, queryset, name, value):
        """Filter products in stock."""
        if value:
            return queryset.filter(
                Q(track_inventory=False) |
                Q(stock_quantity__gt=0) |
                Q(allow_backorder=True)
            )
        return queryset
