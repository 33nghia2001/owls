"""
Search Views for Owls E-commerce Platform
==========================================
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q, Count
from django.utils import timezone
from .models import SearchQuery, SearchSuggestion, SearchSynonym, SearchFilter
from .serializers import (
    SearchSuggestionSerializer, SearchFilterSerializer,
    RecordSearchSerializer, SearchClickSerializer
)


class AutocompleteView(APIView):
    """Autocomplete suggestions as user types."""
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if len(query) < 2:
            return Response({'suggestions': []})

        # Get matching suggestions
        suggestions = SearchSuggestion.objects.filter(
            is_active=True,
            term__icontains=query
        ).order_by('-search_count', '-priority')[:10]

        results = []
        for s in suggestions:
            results.append({
                'type': 'suggestion',
                'term': s.term,
                'category': s.category or None
            })

        return Response({'suggestions': results})


class PopularSearchesView(APIView):
    """Get popular search terms."""
    permission_classes = [AllowAny]

    def get(self, request):
        limit = int(request.query_params.get('limit', 10))

        suggestions = SearchSuggestion.objects.filter(
            is_active=True,
            suggestion_type__in=['popular', 'trending']
        ).order_by('-search_count')[:limit]

        serializer = SearchSuggestionSerializer(suggestions, many=True)
        return Response(serializer.data)


class TrendingSearchesView(APIView):
    """Get trending search terms (recent popularity)."""
    permission_classes = [AllowAny]

    def get(self, request):
        limit = int(request.query_params.get('limit', 10))

        # Get searches from last 24 hours
        since = timezone.now() - timezone.timedelta(hours=24)
        trending = SearchQuery.objects.filter(
            created_at__gte=since
        ).values('query').annotate(
            count=Count('id')
        ).order_by('-count')[:limit]

        results = [{'term': t['query'], 'count': t['count']} for t in trending]
        return Response(results)


class SearchHistoryView(APIView):
    """Get user's search history."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = int(request.query_params.get('limit', 20))

        history = SearchQuery.objects.filter(
            user=request.user
        ).values('query').annotate(
            search_count=Count('id')
        ).order_by('-search_count')[:limit]

        # Get latest timestamp for each query
        results = []
        for h in history:
            last_search = SearchQuery.objects.filter(
                user=request.user, query=h['query']
            ).order_by('-created_at').first()
            results.append({
                'query': h['query'],
                'search_count': h['search_count'],
                'last_searched': last_search.created_at if last_search else None
            })

        return Response(results)

    def delete(self, request):
        """Clear search history."""
        SearchQuery.objects.filter(user=request.user).delete()
        return Response({'detail': 'Search history cleared.'})


class RecordSearchView(APIView):
    """Record a search query."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RecordSearchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        query = data['query'].strip().lower()

        # Create search record
        SearchQuery.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_id=request.session.session_key or '',
            query=data['query'],
            query_normalized=query,
            results_count=data.get('results_count', 0),
            category_filter=data.get('category_filter', ''),
            filters_applied=data.get('filters_applied', {}),
            device_type=request.META.get('HTTP_USER_AGENT', '')[:20],
            ip_address=self._get_client_ip(request)
        )

        # Update or create suggestion
        suggestion, created = SearchSuggestion.objects.get_or_create(
            term=query,
            defaults={'suggestion_type': 'popular'}
        )
        if not created:
            suggestion.search_count += 1
            suggestion.save()

        return Response({'detail': 'Search recorded.'}, status=status.HTTP_201_CREATED)

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')


class RecordSearchClickView(APIView):
    """Record when user clicks a search result."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SearchClickSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # Find the latest search query
        search_query = SearchQuery.objects.filter(
            query__iexact=data['query']
        )
        if request.user.is_authenticated:
            search_query = search_query.filter(user=request.user)

        search_query = search_query.order_by('-created_at').first()

        if search_query:
            clicked_ids = search_query.clicked_product_ids or []
            if str(data['product_id']) not in clicked_ids:
                clicked_ids.append(str(data['product_id']))
                search_query.clicked_product_ids = clicked_ids
                search_query.save()

            # Update suggestion click-through count
            SearchSuggestion.objects.filter(
                term__iexact=data['query']
            ).update(click_through_count=models.F('click_through_count') + 1)

        return Response({'detail': 'Click recorded.'})


class SearchFiltersView(APIView):
    """Get available search filters."""
    permission_classes = [AllowAny]

    def get(self, request):
        filters = SearchFilter.objects.filter(is_active=True).order_by('order')
        serializer = SearchFilterSerializer(filters, many=True)
        return Response(serializer.data)


# Import models for F expression
from django.db import models
