"""
Marketing Campaigns Views for Owls E-commerce Platform
======================================================
API endpoints for campaign management.
"""

import logging
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Campaign, CampaignMetrics, CampaignChannel
from .serializers import (
    CampaignSerializer, CampaignListSerializer, CampaignDetailSerializer,
    CampaignCreateSerializer, CampaignMetricsSerializer,
    CampaignChannelSerializer, CampaignStatsSerializer
)

logger = logging.getLogger(__name__)


# =============================================================================
# PUBLIC VIEWS (Customer-facing)
# =============================================================================

@extend_schema(tags=['Campaigns'])
class ActiveCampaignListView(generics.ListAPIView):
    """
    List active public campaigns.
    
    Shows campaigns that are currently running and visible to customers.
    """
    
    serializer_class = CampaignListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        now = timezone.now()
        return Campaign.objects.filter(
            status=Campaign.Status.ACTIVE,
            is_public=True,
            start_date__lte=now,
            end_date__gte=now
        ).order_by('-priority', '-created_at')


@extend_schema(tags=['Campaigns'])
class FeaturedCampaignListView(generics.ListAPIView):
    """
    List featured campaigns for homepage.
    """
    
    serializer_class = CampaignListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        now = timezone.now()
        return Campaign.objects.filter(
            status=Campaign.Status.ACTIVE,
            is_public=True,
            is_featured=True,
            start_date__lte=now,
            end_date__gte=now
        ).order_by('-priority')[:5]


@extend_schema(tags=['Campaigns'])
class CampaignPublicDetailView(generics.RetrieveAPIView):
    """
    Get public campaign details by slug.
    """
    
    serializer_class = CampaignDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        return Campaign.objects.filter(
            is_public=True,
            status__in=[Campaign.Status.ACTIVE, Campaign.Status.SCHEDULED]
        )
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Track impression
        metrics, _ = CampaignMetrics.objects.get_or_create(campaign=instance)
        metrics.increment_impressions()
        
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data
        })


@extend_schema(tags=['Campaigns'])
class TrackCampaignClickView(APIView):
    """
    Track campaign click/engagement.
    
    Called when user clicks on a campaign banner or link.
    """
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, slug):
        try:
            campaign = Campaign.objects.get(
                slug=slug,
                status=Campaign.Status.ACTIVE
            )
            metrics, _ = CampaignMetrics.objects.get_or_create(campaign=campaign)
            metrics.increment_clicks()
            
            return Response({'success': True})
        except Campaign.DoesNotExist:
            return Response({'success': False}, status=status.HTTP_404_NOT_FOUND)


# =============================================================================
# ADMIN VIEWS
# =============================================================================

@extend_schema(tags=['Campaigns - Admin'])
class CampaignAdminListView(generics.ListAPIView):
    """
    List all campaigns for admin.
    """
    
    serializer_class = CampaignListSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        queryset = Campaign.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by type
        campaign_type = self.request.query_params.get('type')
        if campaign_type:
            queryset = queryset.filter(campaign_type=campaign_type)
        
        # Filter active/upcoming/expired
        time_filter = self.request.query_params.get('time')
        now = timezone.now()
        if time_filter == 'active':
            queryset = queryset.filter(
                status=Campaign.Status.ACTIVE,
                start_date__lte=now,
                end_date__gte=now
            )
        elif time_filter == 'upcoming':
            queryset = queryset.filter(start_date__gt=now)
        elif time_filter == 'expired':
            queryset = queryset.filter(end_date__lt=now)
        
        return queryset.select_related('created_by')


@extend_schema(
    tags=['Campaigns - Admin'],
    request=CampaignCreateSerializer,
    responses={201: CampaignSerializer}
)
class CampaignCreateView(APIView):
    """
    Create a new campaign.
    """
    
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        serializer = CampaignCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        campaign = serializer.save()
        
        # Create metrics record
        CampaignMetrics.objects.create(campaign=campaign)
        
        logger.info(f"Campaign created: {campaign.name} by {request.user.id}")
        
        return Response({
            'success': True,
            'message': 'Campaign created successfully',
            'data': CampaignSerializer(campaign).data
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Campaigns - Admin'])
class CampaignAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete a campaign.
    """
    
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Campaign.objects.all()
    lookup_field = 'id'
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'success': True,
            'message': 'Campaign updated',
            'data': serializer.data
        })
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        name = instance.name
        self.perform_destroy(instance)
        
        logger.info(f"Campaign deleted: {name} by {request.user.id}")
        
        return Response({
            'success': True,
            'message': 'Campaign deleted'
        })


@extend_schema(tags=['Campaigns - Admin'])
class CampaignStatusView(APIView):
    """
    Update campaign status (activate, pause, complete, cancel).
    """
    
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, id):
        campaign = get_object_or_404(Campaign, id=id)
        action = request.data.get('action')
        
        valid_actions = ['activate', 'pause', 'complete', 'cancel']
        if action not in valid_actions:
            return Response({
                'success': False,
                'error': {'message': f'Invalid action. Use: {valid_actions}'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if action == 'activate':
            campaign.status = Campaign.Status.ACTIVE
        elif action == 'pause':
            campaign.status = Campaign.Status.PAUSED
        elif action == 'complete':
            campaign.status = Campaign.Status.COMPLETED
        elif action == 'cancel':
            campaign.status = Campaign.Status.CANCELLED
        
        campaign.save(update_fields=['status', 'updated_at'])
        
        logger.info(f"Campaign {id} status changed to {action} by {request.user.id}")
        
        return Response({
            'success': True,
            'message': f'Campaign {action}d',
            'data': {'status': campaign.status}
        })


@extend_schema(tags=['Campaigns - Admin'])
class CampaignMetricsView(generics.RetrieveAPIView):
    """
    Get campaign performance metrics.
    """
    
    serializer_class = CampaignMetricsSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_object(self):
        campaign = get_object_or_404(Campaign, id=self.kwargs['id'])
        metrics, _ = CampaignMetrics.objects.get_or_create(campaign=campaign)
        return metrics


@extend_schema(tags=['Campaigns - Admin'])
class CampaignChannelListView(generics.ListCreateAPIView):
    """
    List and add channels for a campaign.
    """
    
    serializer_class = CampaignChannelSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        campaign_id = self.kwargs['id']
        return CampaignChannel.objects.filter(campaign_id=campaign_id)
    
    def perform_create(self, serializer):
        campaign = get_object_or_404(Campaign, id=self.kwargs['id'])
        serializer.save(campaign=campaign)


@extend_schema(
    tags=['Campaigns - Admin'],
    responses={200: CampaignStatsSerializer}
)
class CampaignStatsView(APIView):
    """
    Get overall campaign statistics.
    """
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        from django.db.models import Sum, Count, Avg
        
        now = timezone.now()
        
        # Campaign counts by status
        status_counts = dict(
            Campaign.objects.values('status')
            .annotate(count=Count('id'))
            .values_list('status', 'count')
        )
        
        # Active campaigns
        active = Campaign.objects.filter(
            status=Campaign.Status.ACTIVE,
            start_date__lte=now,
            end_date__gte=now
        ).count()
        
        # Total metrics
        total_metrics = CampaignMetrics.objects.aggregate(
            total_impressions=Sum('impressions'),
            total_clicks=Sum('clicks'),
            total_orders=Sum('orders'),
            total_revenue=Sum('revenue'),
            total_discount=Sum('discount_given')
        )
        
        # Total budget
        budget_stats = Campaign.objects.aggregate(
            total_budget=Sum('budget'),
            total_spent=Sum('spent')
        )
        
        return Response({
            'success': True,
            'data': {
                'by_status': status_counts,
                'active_campaigns': active,
                'total_impressions': total_metrics['total_impressions'] or 0,
                'total_clicks': total_metrics['total_clicks'] or 0,
                'total_orders': total_metrics['total_orders'] or 0,
                'total_revenue': str(total_metrics['total_revenue'] or 0),
                'total_discount_given': str(total_metrics['total_discount'] or 0),
                'total_budget': str(budget_stats['total_budget'] or 0),
                'total_spent': str(budget_stats['total_spent'] or 0)
            }
        })
