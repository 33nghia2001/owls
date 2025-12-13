"""
Audit Log Views for Owls E-commerce Platform
=============================================
Admin-only views for audit log management.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta
from .models import AuditLog, LoginAttempt, DataExportLog, SystemEvent, AuditAction
from .serializers import (
    AuditLogSerializer, AuditLogListSerializer,
    LoginAttemptSerializer, DataExportLogSerializer,
    SystemEventSerializer, SystemEventListSerializer,
    ResolveEventSerializer
)


class AuditLogListView(APIView):
    """List audit logs with filtering."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        logs = AuditLog.objects.all().select_related('user')

        # Filter by user
        user_id = request.query_params.get('user')
        if user_id:
            logs = logs.filter(user_id=user_id)

        # Filter by action
        action = request.query_params.get('action')
        if action:
            logs = logs.filter(action=action)

        # Filter by resource type
        resource_type = request.query_params.get('resource_type')
        if resource_type:
            logs = logs.filter(resource_type=resource_type)

        # Filter by resource id
        resource_id = request.query_params.get('resource_id')
        if resource_id:
            logs = logs.filter(resource_id=resource_id)

        # Filter by date range
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            logs = logs.filter(created_at__date__gte=start_date)
        if end_date:
            logs = logs.filter(created_at__date__lte=end_date)

        # Filter by status
        log_status = request.query_params.get('status')
        if log_status:
            logs = logs.filter(status=log_status)

        # Pagination
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 50))
        start = (page - 1) * per_page
        end = start + per_page

        total_count = logs.count()
        logs = logs.order_by('-created_at')[start:end]

        serializer = AuditLogListSerializer(logs, many=True)
        return Response({
            'results': serializer.data,
            'count': total_count,
            'page': page,
            'per_page': per_page
        })


class AuditLogDetailView(APIView):
    """View detailed audit log."""
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        log = get_object_or_404(AuditLog, pk=pk)
        serializer = AuditLogSerializer(log)
        return Response(serializer.data)


class AuditLogResourceHistoryView(APIView):
    """Get audit history for a specific resource."""
    permission_classes = [IsAdminUser]

    def get(self, request, resource_type, resource_id):
        logs = AuditLog.objects.filter(
            resource_type=resource_type,
            resource_id=str(resource_id)
        ).select_related('user').order_by('-created_at')

        serializer = AuditLogSerializer(logs, many=True)
        return Response(serializer.data)


class AuditLogUserActivityView(APIView):
    """Get audit logs for a specific user."""
    permission_classes = [IsAdminUser]

    def get(self, request, user_id):
        logs = AuditLog.objects.filter(
            user_id=user_id
        ).order_by('-created_at')[:100]

        serializer = AuditLogListSerializer(logs, many=True)
        return Response(serializer.data)


class LoginAttemptListView(APIView):
    """List login attempts."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        attempts = LoginAttempt.objects.all()

        # Filter by email
        email = request.query_params.get('email')
        if email:
            attempts = attempts.filter(email__icontains=email)

        # Filter by IP
        ip = request.query_params.get('ip')
        if ip:
            attempts = attempts.filter(ip_address=ip)

        # Filter by success
        success = request.query_params.get('success')
        if success is not None:
            attempts = attempts.filter(success=success.lower() == 'true')

        # Date range
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            attempts = attempts.filter(created_at__date__gte=start_date)
        if end_date:
            attempts = attempts.filter(created_at__date__lte=end_date)

        # Pagination
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 50))
        start = (page - 1) * per_page
        end = start + per_page

        total_count = attempts.count()
        attempts = attempts.order_by('-created_at')[start:end]

        serializer = LoginAttemptSerializer(attempts, many=True)
        return Response({
            'results': serializer.data,
            'count': total_count,
            'page': page,
            'per_page': per_page
        })


class SuspiciousActivityView(APIView):
    """Detect suspicious login activity."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        since = timezone.now() - timedelta(hours=24)

        # Find IPs with many failed attempts
        suspicious_ips = LoginAttempt.objects.filter(
            created_at__gte=since,
            success=False
        ).values('ip_address').annotate(
            failed_count=Count('id')
        ).filter(failed_count__gte=5).order_by('-failed_count')

        # Find accounts with many failed attempts
        suspicious_accounts = LoginAttempt.objects.filter(
            created_at__gte=since,
            success=False
        ).values('email').annotate(
            failed_count=Count('id')
        ).filter(failed_count__gte=3).order_by('-failed_count')

        return Response({
            'suspicious_ips': list(suspicious_ips),
            'suspicious_accounts': list(suspicious_accounts),
            'time_window_hours': 24
        })


class DataExportLogListView(APIView):
    """List data export logs."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        exports = DataExportLog.objects.all().select_related('user')

        # Filter by type
        export_type = request.query_params.get('type')
        if export_type:
            exports = exports.filter(export_type=export_type)

        # Filter by user
        user_id = request.query_params.get('user')
        if user_id:
            exports = exports.filter(user_id=user_id)

        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 50))
        start = (page - 1) * per_page
        end = start + per_page

        total_count = exports.count()
        exports = exports.order_by('-created_at')[start:end]

        serializer = DataExportLogSerializer(exports, many=True)
        return Response({
            'results': serializer.data,
            'count': total_count,
            'page': page,
            'per_page': per_page
        })


class SystemEventListView(APIView):
    """List system events."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        events = SystemEvent.objects.all()

        # Filter by level
        level = request.query_params.get('level')
        if level:
            events = events.filter(event_level=level)

        # Filter by type
        event_type = request.query_params.get('type')
        if event_type:
            events = events.filter(event_type__icontains=event_type)

        # Filter by resolved status
        resolved = request.query_params.get('resolved')
        if resolved is not None:
            events = events.filter(resolved=resolved.lower() == 'true')

        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 50))
        start = (page - 1) * per_page
        end = start + per_page

        total_count = events.count()
        events = events.order_by('-created_at')[start:end]

        serializer = SystemEventListSerializer(events, many=True)
        return Response({
            'results': serializer.data,
            'count': total_count,
            'page': page,
            'per_page': per_page
        })


class SystemEventDetailView(APIView):
    """View detailed system event."""
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        event = get_object_or_404(SystemEvent, pk=pk)
        serializer = SystemEventSerializer(event)
        return Response(serializer.data)


class ResolveSystemEventView(APIView):
    """Mark a system event as resolved."""
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        event = get_object_or_404(SystemEvent, pk=pk)

        if event.resolved:
            return Response(
                {'detail': 'Event is already resolved.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ResolveEventSerializer(data=request.data)
        if serializer.is_valid():
            event.resolved = True
            event.resolved_at = timezone.now()
            event.resolved_by = request.user
            event.resolution_notes = serializer.validated_data.get('resolution_notes', '')
            event.save()

            return Response({
                'detail': 'Event marked as resolved.',
                'event': SystemEventSerializer(event).data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuditStatisticsView(APIView):
    """Get audit log statistics."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        since = timezone.now() - timedelta(days=7)

        # Actions breakdown
        action_stats = AuditLog.objects.filter(
            created_at__gte=since
        ).values('action').annotate(count=Count('id')).order_by('-count')

        # Resource types breakdown
        resource_stats = AuditLog.objects.filter(
            created_at__gte=since
        ).values('resource_type').annotate(count=Count('id')).order_by('-count')

        # Daily counts
        daily_stats = AuditLog.objects.filter(
            created_at__gte=since
        ).extra(
            select={'date': 'DATE(created_at)'}
        ).values('date').annotate(count=Count('id')).order_by('date')

        # System events summary
        event_stats = {
            'total': SystemEvent.objects.count(),
            'unresolved': SystemEvent.objects.filter(resolved=False).count(),
            'critical_unresolved': SystemEvent.objects.filter(
                resolved=False, event_level='critical'
            ).count()
        }

        return Response({
            'time_window_days': 7,
            'actions': list(action_stats),
            'resource_types': list(resource_stats),
            'daily_counts': list(daily_stats),
            'system_events': event_stats
        })
