"""
Fraud Detection Views for Owls E-commerce Platform
==================================================
Admin API for fraud management and risk assessment.
"""

import logging
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import (
    FraudRule, RiskAssessment, IPBlacklist, DeviceFingerprint
)
from .serializers import (
    FraudRuleSerializer, RiskAssessmentSerializer, RiskAssessmentListSerializer,
    ReviewAssessmentSerializer, IPBlacklistSerializer, BlockIPSerializer,
    DeviceFingerprintSerializer, FraudStatsSerializer
)
from .services import FraudDetectionService

logger = logging.getLogger(__name__)


# =============================================================================
# FRAUD RULES MANAGEMENT (Admin)
# =============================================================================

@extend_schema(tags=['Fraud Detection - Admin'])
class FraudRuleListCreateView(generics.ListCreateAPIView):
    """
    List and create fraud detection rules.
    
    Admin only.
    """
    
    serializer_class = FraudRuleSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        queryset = FraudRule.objects.all()
        
        # Filter by type
        rule_type = self.request.query_params.get('type')
        if rule_type:
            queryset = queryset.filter(rule_type=rule_type)
        
        # Filter by active status
        is_active = self.request.query_params.get('active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset


@extend_schema(tags=['Fraud Detection - Admin'])
class FraudRuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete a fraud rule.
    
    Admin only.
    """
    
    serializer_class = FraudRuleSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = FraudRule.objects.all()
    lookup_field = 'id'


# =============================================================================
# RISK ASSESSMENTS
# =============================================================================

@extend_schema(tags=['Fraud Detection - Admin'])
class RiskAssessmentListView(generics.ListAPIView):
    """
    List risk assessments with filtering.
    
    Admin only.
    """
    
    serializer_class = RiskAssessmentListSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        queryset = RiskAssessment.objects.select_related(
            'order', 'user'
        ).prefetch_related('rule_triggers')
        
        # Filter by risk level
        risk_level = self.request.query_params.get('risk_level')
        if risk_level:
            queryset = queryset.filter(risk_level=risk_level)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter pending review only
        pending = self.request.query_params.get('pending')
        if pending and pending.lower() == 'true':
            queryset = queryset.filter(status=RiskAssessment.Status.PENDING)
        
        # Filter high risk only
        high_risk = self.request.query_params.get('high_risk')
        if high_risk and high_risk.lower() == 'true':
            queryset = queryset.filter(
                risk_level__in=[
                    RiskAssessment.RiskLevel.HIGH,
                    RiskAssessment.RiskLevel.CRITICAL
                ]
            )
        
        # Date range
        days = self.request.query_params.get('days')
        if days:
            try:
                since = timezone.now() - timedelta(days=int(days))
                queryset = queryset.filter(created_at__gte=since)
            except ValueError:
                pass
        
        return queryset


@extend_schema(tags=['Fraud Detection - Admin'])
class RiskAssessmentDetailView(generics.RetrieveAPIView):
    """
    Get detailed risk assessment.
    
    Admin only.
    """
    
    serializer_class = RiskAssessmentSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'id'
    
    def get_queryset(self):
        return RiskAssessment.objects.select_related(
            'order', 'user', 'reviewed_by'
        ).prefetch_related('rule_triggers__rule')


@extend_schema(
    tags=['Fraud Detection - Admin'],
    request=ReviewAssessmentSerializer,
    responses={200: RiskAssessmentSerializer}
)
class ReviewAssessmentView(APIView):
    """
    Review and update assessment status.
    
    Admin can approve, reject, or escalate assessments.
    """
    
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, id):
        assessment = get_object_or_404(RiskAssessment, id=id)
        
        serializer = ReviewAssessmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Update assessment
        assessment.status = serializer.validated_data['status']
        assessment.review_notes = serializer.validated_data.get('review_notes', '')
        assessment.reviewed_by = request.user
        assessment.reviewed_at = timezone.now()
        assessment.save()
        
        logger.info(
            f"Assessment {id} reviewed by {request.user.id}: "
            f"status={assessment.status}"
        )
        
        return Response({
            'success': True,
            'message': f'Assessment {assessment.status}',
            'data': RiskAssessmentSerializer(assessment).data
        })


# =============================================================================
# IP BLACKLIST MANAGEMENT
# =============================================================================

@extend_schema(tags=['Fraud Detection - Admin'])
class IPBlacklistListView(generics.ListAPIView):
    """
    List blacklisted IPs.
    
    Admin only.
    """
    
    serializer_class = IPBlacklistSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        queryset = IPBlacklist.objects.select_related('created_by')
        
        # Filter by reason
        reason = self.request.query_params.get('reason')
        if reason:
            queryset = queryset.filter(reason=reason)
        
        # Filter active only (not expired)
        active = self.request.query_params.get('active')
        if active and active.lower() == 'true':
            queryset = queryset.filter(
                Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
            )
        
        return queryset.order_by('-created_at')


@extend_schema(
    tags=['Fraud Detection - Admin'],
    request=BlockIPSerializer,
    responses={201: IPBlacklistSerializer}
)
class BlockIPView(APIView):
    """
    Block an IP address.
    
    Admin only.
    """
    
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        serializer = BlockIPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = FraudDetectionService()
        blacklist = service.block_ip(
            ip_address=serializer.validated_data['ip_address'],
            reason=serializer.validated_data['reason'],
            notes=serializer.validated_data.get('notes', ''),
            expires_hours=serializer.validated_data.get('expires_hours'),
            created_by=request.user
        )
        
        return Response({
            'success': True,
            'message': 'IP blocked successfully',
            'data': IPBlacklistSerializer(blacklist).data
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Fraud Detection - Admin'])
class UnblockIPView(APIView):
    """
    Remove an IP from blacklist.
    
    Admin only.
    """
    
    permission_classes = [permissions.IsAdminUser]
    
    def delete(self, request, id):
        blacklist = get_object_or_404(IPBlacklist, id=id)
        ip_address = blacklist.ip_address
        blacklist.delete()
        
        # Clear cache
        from django.core.cache import cache
        cache.delete(f'ip_blocked:{ip_address}')
        
        logger.info(f"IP unblocked: {ip_address} by {request.user.id}")
        
        return Response({
            'success': True,
            'message': f'IP {ip_address} unblocked'
        })


# =============================================================================
# DEVICE FINGERPRINTS
# =============================================================================

@extend_schema(tags=['Fraud Detection - Admin'])
class DeviceFingerprintListView(generics.ListAPIView):
    """
    List device fingerprints.
    
    Admin only.
    """
    
    serializer_class = DeviceFingerprintSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        queryset = DeviceFingerprint.objects.select_related('user')
        
        # Filter blocked only
        blocked = self.request.query_params.get('blocked')
        if blocked and blocked.lower() == 'true':
            queryset = queryset.filter(is_blocked=True)
        
        # Filter by user
        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset.order_by('-last_seen')


@extend_schema(tags=['Fraud Detection - Admin'])
class BlockDeviceView(APIView):
    """
    Block or unblock a device.
    
    Admin only.
    """
    
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, id):
        device = get_object_or_404(DeviceFingerprint, id=id)
        
        block = request.data.get('block', True)
        reason = request.data.get('reason', 'Manual block')
        
        device.is_blocked = block
        device.block_reason = reason if block else ''
        device.save(update_fields=['is_blocked', 'block_reason'])
        
        action = 'blocked' if block else 'unblocked'
        logger.info(f"Device {id} {action} by {request.user.id}")
        
        return Response({
            'success': True,
            'message': f'Device {action}',
            'data': DeviceFingerprintSerializer(device).data
        })


# =============================================================================
# FRAUD STATISTICS
# =============================================================================

@extend_schema(
    tags=['Fraud Detection - Admin'],
    responses={200: FraudStatsSerializer}
)
class FraudStatsView(APIView):
    """
    Get fraud detection statistics.
    
    Admin only.
    """
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        # Assessment stats
        assessment_stats = RiskAssessment.objects.aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status=RiskAssessment.Status.PENDING)),
            approved=Count('id', filter=Q(status=RiskAssessment.Status.APPROVED)),
            rejected=Count('id', filter=Q(status=RiskAssessment.Status.REJECTED))
        )
        
        # By risk level
        by_risk = dict(
            RiskAssessment.objects.values('risk_level')
            .annotate(count=Count('id'))
            .values_list('risk_level', 'count')
        )
        
        # Recent high risk (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        recent_high = RiskAssessment.objects.filter(
            created_at__gte=week_ago,
            risk_level__in=[
                RiskAssessment.RiskLevel.HIGH,
                RiskAssessment.RiskLevel.CRITICAL
            ]
        ).count()
        
        # Blocked counts
        blocked_ips = IPBlacklist.objects.filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        ).count()
        blocked_devices = DeviceFingerprint.objects.filter(is_blocked=True).count()
        
        return Response({
            'success': True,
            'data': {
                'total_assessments': assessment_stats['total'],
                'pending_review': assessment_stats['pending'],
                'approved': assessment_stats['approved'],
                'rejected': assessment_stats['rejected'],
                'by_risk_level': by_risk,
                'recent_high_risk': recent_high,
                'blocked_ips': blocked_ips,
                'blocked_devices': blocked_devices
            }
        })


# =============================================================================
# IP CHECK (Public - for middleware)
# =============================================================================

@extend_schema(tags=['Fraud Detection'])
class CheckIPView(APIView):
    """
    Check if an IP is blocked.
    
    Used by middleware or frontend for quick checks.
    """
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        ip_address = request.META.get('REMOTE_ADDR')
        
        service = FraudDetectionService()
        blocked = service.is_ip_blocked(ip_address)
        
        return Response({
            'ip': ip_address,
            'blocked': blocked
        })
