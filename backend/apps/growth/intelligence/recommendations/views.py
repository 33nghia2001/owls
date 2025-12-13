"""
Recommendations Views for Owls E-commerce Platform
==================================================
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from django.db.models import F
from .models import (
    ProductSimilarity, FrequentlyBoughtTogether,
    UserProductInteraction, UserPreference,
    RecommendationSet, RecommendationClick, RecommendationType
)
from .serializers import (
    UserPreferenceSerializer, RecordInteractionSerializer,
    RecommendationClickSerializer
)


class SimilarProductsView(APIView):
    """Get similar products for a given product."""
    permission_classes = [AllowAny]

    def get(self, request, product_id):
        limit = int(request.query_params.get('limit', 8))

        similarities = ProductSimilarity.objects.filter(
            product_id=product_id
        ).order_by('-similarity_score')[:limit]

        product_ids = [str(s.similar_product_id) for s in similarities]

        return Response({
            'recommendation_type': 'similar',
            'title': 'Similar Products',
            'source_product_id': str(product_id),
            'product_ids': product_ids
        })


class FrequentlyBoughtTogetherView(APIView):
    """Get products frequently bought with given product."""
    permission_classes = [AllowAny]

    def get(self, request, product_id):
        limit = int(request.query_params.get('limit', 4))

        fbt = FrequentlyBoughtTogether.objects.filter(
            product_id=product_id
        ).order_by('-co_purchase_count')[:limit]

        product_ids = [str(f.related_product_id) for f in fbt]

        return Response({
            'recommendation_type': 'frequently_bought',
            'title': 'Frequently Bought Together',
            'source_product_id': str(product_id),
            'product_ids': product_ids
        })


class PersonalizedRecommendationsView(APIView):
    """Get personalized recommendations for authenticated user."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = int(request.query_params.get('limit', 12))

        # Try to get pre-computed recommendations
        rec_set = RecommendationSet.objects.filter(
            user=request.user,
            recommendation_type=RecommendationType.PERSONALIZED,
            is_valid=True,
            expires_at__gt=timezone.now()
        ).first()

        if rec_set:
            product_ids = rec_set.recommended_product_ids[:limit]
        else:
            # Fallback: get products from user's preferred categories
            prefs = UserPreference.objects.filter(user=request.user).first()
            product_ids = []
            if prefs and prefs.preferred_categories:
                # Return empty for now - actual product fetching would happen in product service
                pass

        return Response({
            'recommendation_type': 'personalized',
            'title': 'Recommended For You',
            'product_ids': product_ids
        })


class TrendingProductsView(APIView):
    """Get trending products."""
    permission_classes = [AllowAny]

    def get(self, request):
        limit = int(request.query_params.get('limit', 12))
        category_id = request.query_params.get('category')

        rec_set = RecommendationSet.objects.filter(
            recommendation_type=RecommendationType.TRENDING,
            user__isnull=True,
            is_valid=True,
            expires_at__gt=timezone.now()
        )

        if category_id:
            rec_set = rec_set.filter(category_id=category_id)

        rec_set = rec_set.first()
        product_ids = rec_set.recommended_product_ids[:limit] if rec_set else []

        return Response({
            'recommendation_type': 'trending',
            'title': 'Trending Now',
            'product_ids': product_ids
        })


class RecentlyViewedView(APIView):
    """Get user's recently viewed products."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = int(request.query_params.get('limit', 12))

        interactions = UserProductInteraction.objects.filter(
            user=request.user,
            interaction_type=UserProductInteraction.InteractionType.VIEW
        ).order_by('-created_at').values('product_id', 'created_at').distinct()[:limit]

        results = [
            {
                'product_id': str(i['product_id']),
                'viewed_at': i['created_at']
            }
            for i in interactions
        ]

        return Response({
            'recommendation_type': 'recently_viewed',
            'title': 'Recently Viewed',
            'products': results
        })


class CartBasedRecommendationsView(APIView):
    """Get recommendations based on cart contents."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit = int(request.query_params.get('limit', 8))

        # Get products related to items in user's cart
        # This would integrate with the cart module
        rec_set = RecommendationSet.objects.filter(
            user=request.user,
            recommendation_type=RecommendationType.BASED_ON_CART,
            is_valid=True,
            expires_at__gt=timezone.now()
        ).first()

        product_ids = rec_set.recommended_product_ids[:limit] if rec_set else []

        return Response({
            'recommendation_type': 'cart_based',
            'title': 'Complete Your Order',
            'product_ids': product_ids
        })


class RecordInteractionView(APIView):
    """Record user interaction with a product."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RecordInteractionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # Assign interaction weight based on type
        weights = {
            'view': 1.0,
            'click': 1.5,
            'add_cart': 3.0,
            'add_wishlist': 2.5,
            'purchase': 5.0,
            'review': 4.0,
            'share': 2.0
        }

        UserProductInteraction.objects.create(
            user=request.user,
            product_id=data['product_id'],
            interaction_type=data['interaction_type'],
            interaction_weight=weights.get(data['interaction_type'], 1.0),
            session_id=request.session.session_key or '',
            source=data.get('source', '')
        )

        return Response({'detail': 'Interaction recorded.'}, status=status.HTTP_201_CREATED)


class RecordRecommendationClickView(APIView):
    """Record when user clicks a recommendation."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RecommendationClickSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        RecommendationClick.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_id=request.session.session_key or '',
            recommendation_type=data['recommendation_type'],
            source_product_id=data.get('source_product_id'),
            clicked_product_id=data['clicked_product_id'],
            position=data['position']
        )

        return Response({'detail': 'Click recorded.'}, status=status.HTTP_201_CREATED)


class MyPreferencesView(APIView):
    """Get user's computed preferences."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        prefs = UserPreference.objects.filter(user=request.user).first()
        if not prefs:
            return Response({
                'detail': 'No preferences computed yet.',
                'preferences': None
            })

        serializer = UserPreferenceSerializer(prefs)
        return Response({'preferences': serializer.data})


class HomepageRecommendationsView(APIView):
    """Get all recommendation sections for homepage."""
    permission_classes = [AllowAny]

    def get(self, request):
        limit = int(request.query_params.get('limit', 8))
        result = {}

        # Trending
        trending_set = RecommendationSet.objects.filter(
            recommendation_type=RecommendationType.TRENDING,
            user__isnull=True,
            is_valid=True,
            expires_at__gt=timezone.now()
        ).first()
        result['trending'] = {
            'title': 'Trending Now',
            'product_ids': trending_set.recommended_product_ids[:limit] if trending_set else []
        }

        # New arrivals
        new_set = RecommendationSet.objects.filter(
            recommendation_type=RecommendationType.NEW_ARRIVALS,
            user__isnull=True,
            is_valid=True,
            expires_at__gt=timezone.now()
        ).first()
        result['new_arrivals'] = {
            'title': 'New Arrivals',
            'product_ids': new_set.recommended_product_ids[:limit] if new_set else []
        }

        # Best sellers
        best_set = RecommendationSet.objects.filter(
            recommendation_type=RecommendationType.BEST_SELLERS,
            user__isnull=True,
            is_valid=True,
            expires_at__gt=timezone.now()
        ).first()
        result['best_sellers'] = {
            'title': 'Best Sellers',
            'product_ids': best_set.recommended_product_ids[:limit] if best_set else []
        }

        # Personalized (if authenticated)
        if request.user.is_authenticated:
            personalized_set = RecommendationSet.objects.filter(
                user=request.user,
                recommendation_type=RecommendationType.PERSONALIZED,
                is_valid=True,
                expires_at__gt=timezone.now()
            ).first()
            result['personalized'] = {
                'title': 'Recommended For You',
                'product_ids': personalized_set.recommended_product_ids[:limit] if personalized_set else []
            }

            # Recently viewed
            recent = UserProductInteraction.objects.filter(
                user=request.user,
                interaction_type=UserProductInteraction.InteractionType.VIEW
            ).order_by('-created_at').values_list('product_id', flat=True).distinct()[:limit]
            result['recently_viewed'] = {
                'title': 'Recently Viewed',
                'product_ids': [str(pid) for pid in recent]
            }

        return Response(result)
