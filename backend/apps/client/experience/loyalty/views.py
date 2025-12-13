"""
Loyalty Views for Owls E-commerce Platform
==========================================
"""

from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import (
    LoyaltyTier, LoyaltyAccount, PointTransaction, 
    Reward, RewardRedemption
)
from .serializers import (
    LoyaltyTierSerializer,
    LoyaltyAccountSerializer,
    LoyaltyAccountSummarySerializer,
    PointTransactionSerializer,
    RewardSerializer,
    RedeemRewardSerializer,
    RewardRedemptionSerializer
)


def get_or_create_loyalty_account(user):
    """Get or create user's loyalty account."""
    account, _ = LoyaltyAccount.objects.get_or_create(user=user)
    return account


@extend_schema(tags=['Loyalty'])
class LoyaltyTiersView(generics.ListAPIView):
    """List all loyalty tiers."""
    
    serializer_class = LoyaltyTierSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return LoyaltyTier.objects.filter(is_active=True).order_by('order')


@extend_schema(tags=['Loyalty'])
class MyLoyaltyAccountView(generics.RetrieveAPIView):
    """Get current user's loyalty account."""
    
    serializer_class = LoyaltyAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_or_create_loyalty_account(self.request.user)


@extend_schema(tags=['Loyalty'])
class MyLoyaltySummaryView(APIView):
    """Get quick summary of loyalty status."""
    
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        account = get_or_create_loyalty_account(request.user)
        
        # Calculate next tier
        next_tier = None
        points_to_next_tier = None
        
        if account.tier:
            next_tier_obj = LoyaltyTier.objects.filter(
                is_active=True,
                min_points__gt=account.tier.min_points
            ).order_by('min_points').first()
            
            if next_tier_obj:
                next_tier = next_tier_obj.name
                points_to_next_tier = next_tier_obj.min_points - account.points_earned_total
        else:
            # No tier yet, get first tier
            first_tier = LoyaltyTier.objects.filter(
                is_active=True,
                min_points__gt=0
            ).order_by('min_points').first()
            
            if first_tier:
                next_tier = first_tier.name
                points_to_next_tier = first_tier.min_points - account.points_earned_total
        
        return Response({
            'success': True,
            'data': {
                'points_balance': account.points_balance,
                'points_value': str(account.get_points_value()),
                'current_tier': account.tier.name if account.tier else None,
                'next_tier': next_tier,
                'points_to_next_tier': max(0, points_to_next_tier) if points_to_next_tier else None,
                'total_orders': account.total_orders,
                'total_spent': str(account.total_spent)
            }
        })


@extend_schema(tags=['Loyalty'])
class MyPointTransactionsView(generics.ListAPIView):
    """List user's point transactions."""
    
    serializer_class = PointTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        account = get_or_create_loyalty_account(self.request.user)
        return PointTransaction.objects.filter(account=account)


@extend_schema(tags=['Loyalty'])
class AvailableRewardsView(generics.ListAPIView):
    """List available rewards."""
    
    serializer_class = RewardSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        now = timezone.now()
        queryset = Reward.objects.filter(
            is_active=True,
            starts_at__lte=now
        ).filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
        )
        
        # Filter by affordability if authenticated
        if self.request.user.is_authenticated:
            affordable = self.request.query_params.get('affordable')
            if affordable == 'true':
                account = get_or_create_loyalty_account(self.request.user)
                queryset = queryset.filter(points_required__lte=account.points_balance)
        
        return queryset.order_by('points_required')


@extend_schema(tags=['Loyalty'])
class FeaturedRewardsView(generics.ListAPIView):
    """List featured rewards."""
    
    serializer_class = RewardSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        now = timezone.now()
        return Reward.objects.filter(
            is_active=True,
            is_featured=True,
            starts_at__lte=now
        ).filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
        ).order_by('points_required')[:6]


@extend_schema(
    tags=['Loyalty'],
    request=RedeemRewardSerializer,
    responses={
        201: RewardRedemptionSerializer,
        400: OpenApiResponse(description='Insufficient points or validation error'),
        404: OpenApiResponse(description='Reward not found')
    }
)
class RedeemRewardView(APIView):
    """Redeem a reward."""
    
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = RedeemRewardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        reward = get_object_or_404(Reward, id=serializer.validated_data['reward_id'])
        account = get_or_create_loyalty_account(request.user)
        
        # Check availability
        if not reward.is_available:
            return Response({
                'success': False,
                'error': {'message': 'This reward is no longer available'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check tier requirement
        if reward.min_tier:
            if not account.tier or account.tier.min_points < reward.min_tier.min_points:
                return Response({
                    'success': False,
                    'error': {'message': f'Requires {reward.min_tier.name} tier or higher'}
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check points
        if account.points_balance < reward.points_required:
            return Response({
                'success': False,
                'error': {
                    'message': 'Insufficient points',
                    'points_required': reward.points_required,
                    'points_available': account.points_balance
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check per-user limit
        user_redemptions = RewardRedemption.objects.filter(
            account=account,
            reward=reward,
            status__in=['pending', 'completed']
        ).count()
        
        if user_redemptions >= reward.redemption_limit_per_user:
            return Response({
                'success': False,
                'error': {'message': 'You have reached the redemption limit for this reward'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Spend points
        account.spend_points(
            points=reward.points_required,
            description=f'Redeemed: {reward.name}'
        )
        
        # Create redemption
        redemption = RewardRedemption.objects.create(
            account=account,
            reward=reward,
            points_spent=reward.points_required,
            status=RewardRedemption.Status.COMPLETED
        )
        
        # Update reward quantity
        reward.quantity_redeemed += 1
        reward.save(update_fields=['quantity_redeemed'])
        
        return Response({
            'success': True,
            'message': 'Reward redeemed successfully',
            'data': RewardRedemptionSerializer(redemption).data
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Loyalty'])
class MyRedemptionsView(generics.ListAPIView):
    """List user's reward redemptions."""
    
    serializer_class = RewardRedemptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        account = get_or_create_loyalty_account(self.request.user)
        return RewardRedemption.objects.filter(account=account)


@extend_schema(tags=['Loyalty'])
class RedemptionDetailView(generics.RetrieveAPIView):
    """Get redemption details."""
    
    serializer_class = RewardRedemptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        account = get_or_create_loyalty_account(self.request.user)
        return RewardRedemption.objects.filter(account=account)


# Import models for Q lookups
from django.db import models
