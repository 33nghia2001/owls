"""
Reviews Views for Owls E-commerce Platform
==========================================
"""

from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

from .models import Review, ReviewImage, ReviewVote
from .serializers import (
    ReviewSerializer,
    CreateReviewSerializer,
    UpdateReviewSerializer,
    ReviewVoteSerializer,
    ProductReviewSummarySerializer,
    AdminReviewResponseSerializer
)
from apps.business.commerce.products.models import Product


@extend_schema(tags=['Reviews'])
class ProductReviewsView(generics.ListAPIView):
    """
    List all approved reviews for a product.
    
    Supports filtering by:
    - rating: Filter by specific rating (1-5)
    - verified: Filter verified purchases only
    - with_images: Filter reviews with images only
    - sort: Sort by 'newest', 'oldest', 'helpful', 'rating_high', 'rating_low'
    """
    
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        queryset = Review.objects.filter(
            product_id=product_id,
            status=Review.Status.APPROVED
        ).select_related('user', 'product').prefetch_related('images')
        
        # Filter by rating
        rating = self.request.query_params.get('rating')
        if rating:
            queryset = queryset.filter(rating=int(rating))
        
        # Filter verified purchases
        verified = self.request.query_params.get('verified')
        if verified == 'true':
            queryset = queryset.filter(is_verified_purchase=True)
        
        # Filter with images
        with_images = self.request.query_params.get('with_images')
        if with_images == 'true':
            queryset = queryset.filter(images__isnull=False).distinct()
        
        # Sorting
        sort = self.request.query_params.get('sort', 'newest')
        if sort == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort == 'helpful':
            queryset = queryset.order_by('-helpful_count')
        elif sort == 'rating_high':
            queryset = queryset.order_by('-rating')
        elif sort == 'rating_low':
            queryset = queryset.order_by('rating')
        else:  # newest
            queryset = queryset.order_by('-created_at')
        
        return queryset


@extend_schema(
    tags=['Reviews'],
    responses={200: ProductReviewSummarySerializer}
)
class ProductReviewSummaryView(APIView):
    """Get review summary/statistics for a product."""
    
    permission_classes = [permissions.AllowAny]

    def get(self, request, product_id):
        reviews = Review.objects.filter(
            product_id=product_id,
            status=Review.Status.APPROVED
        )
        
        # Calculate statistics
        stats = reviews.aggregate(
            total=Count('id'),
            avg_rating=Avg('rating'),
            verified_count=Count('id', filter=Q(is_verified_purchase=True))
        )
        
        # Rating distribution
        distribution = {}
        for i in range(1, 6):
            distribution[str(i)] = reviews.filter(rating=i).count()
        
        # Reviews with images
        with_images = reviews.filter(images__isnull=False).distinct().count()
        
        data = {
            'total_reviews': stats['total'] or 0,
            'average_rating': round(stats['avg_rating'] or 0, 2),
            'rating_distribution': distribution,
            'verified_purchase_count': stats['verified_count'] or 0,
            'with_images_count': with_images
        }
        
        return Response({
            'success': True,
            'data': data
        })


@extend_schema(
    tags=['Reviews'],
    request=CreateReviewSerializer,
    responses={
        201: ReviewSerializer,
        400: OpenApiResponse(description='Validation error'),
        409: OpenApiResponse(description='Already reviewed')
    }
)
class CreateReviewView(generics.CreateAPIView):
    """Create a new review for a product."""
    
    serializer_class = CreateReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        
        return Response({
            'success': True,
            'message': 'Review submitted successfully. It will be visible after approval.',
            'data': ReviewSerializer(review).data
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Reviews'])
class MyReviewsView(generics.ListAPIView):
    """List current user's reviews."""
    
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(
            user=self.request.user
        ).select_related('product').prefetch_related('images')


@extend_schema(tags=['Reviews'])
class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete a review.
    
    Users can only modify their own reviews.
    """
    
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UpdateReviewSerializer
        return ReviewSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Reset to pending after edit
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save(status=Review.Status.PENDING)
        
        return Response({
            'success': True,
            'message': 'Review updated. It will be visible after re-approval.',
            'data': ReviewSerializer(instance).data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=['Reviews'],
    request=ReviewVoteSerializer,
    responses={
        200: OpenApiResponse(description='Vote recorded'),
        404: OpenApiResponse(description='Review not found')
    }
)
class VoteReviewView(APIView):
    """Vote on a review's helpfulness."""
    
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, review_id):
        serializer = ReviewVoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            review = Review.objects.get(
                id=review_id,
                status=Review.Status.APPROVED
            )
        except Review.DoesNotExist:
            return Response({
                'success': False,
                'error': {'message': 'Review not found'}
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Can't vote on own review
        if review.user == request.user:
            return Response({
                'success': False,
                'error': {'message': 'Cannot vote on your own review'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create or update vote
        vote, created = ReviewVote.objects.update_or_create(
            review=review,
            user=request.user,
            defaults={'is_helpful': serializer.validated_data['is_helpful']}
        )
        
        return Response({
            'success': True,
            'message': 'Vote recorded',
            'data': {
                'helpful_count': review.helpful_count,
                'not_helpful_count': review.not_helpful_count
            }
        })


@extend_schema(
    tags=['Reviews'],
    responses={
        204: OpenApiResponse(description='Vote removed'),
        404: OpenApiResponse(description='Vote not found')
    }
)
class RemoveVoteView(APIView):
    """Remove vote from a review."""
    
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, review_id):
        try:
            vote = ReviewVote.objects.get(
                review_id=review_id,
                user=request.user
            )
            
            # Update review counts
            if vote.is_helpful:
                vote.review.helpful_count = max(0, vote.review.helpful_count - 1)
            else:
                vote.review.not_helpful_count = max(0, vote.review.not_helpful_count - 1)
            vote.review.save(update_fields=['helpful_count', 'not_helpful_count'])
            
            vote.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except ReviewVote.DoesNotExist:
            return Response({
                'success': False,
                'error': {'message': 'Vote not found'}
            }, status=status.HTTP_404_NOT_FOUND)


@extend_schema(
    tags=['Reviews'],
    responses={
        200: OpenApiResponse(description='Can review status')
    }
)
class CanReviewView(APIView):
    """Check if user can review a product."""
    
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, product_id):
        from apps.business.commerce.orders.models import Order, OrderItem
        
        # Check if already reviewed
        already_reviewed = Review.objects.filter(
            user=request.user,
            product_id=product_id
        ).exists()
        
        if already_reviewed:
            return Response({
                'success': True,
                'data': {
                    'can_review': False,
                    'reason': 'already_reviewed'
                }
            })
        
        # Check if purchased
        has_purchased = OrderItem.objects.filter(
            order__user=request.user,
            order__status=Order.Status.DELIVERED,
            product_id=product_id
        ).exists()
        
        return Response({
            'success': True,
            'data': {
                'can_review': True,
                'is_verified_purchase': has_purchased
            }
        })
