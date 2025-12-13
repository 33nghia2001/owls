"""
Audit Log URLs for Owls E-commerce Platform
===========================================
"""

from django.urls import path
from . import views

app_name = 'audit_logs'

urlpatterns = [
    # Audit logs
    path('', views.AuditLogListView.as_view(), name='list'),
    path('<uuid:pk>/', views.AuditLogDetailView.as_view(), name='detail'),
    path('resource/<str:resource_type>/<str:resource_id>/', views.AuditLogResourceHistoryView.as_view(), name='resource-history'),
    path('user/<uuid:user_id>/', views.AuditLogUserActivityView.as_view(), name='user-activity'),
    path('statistics/', views.AuditStatisticsView.as_view(), name='statistics'),

    # Login attempts
    path('login-attempts/', views.LoginAttemptListView.as_view(), name='login-attempts'),
    path('suspicious/', views.SuspiciousActivityView.as_view(), name='suspicious'),

    # Data exports
    path('exports/', views.DataExportLogListView.as_view(), name='exports'),

    # System events
    path('events/', views.SystemEventListView.as_view(), name='events'),
    path('events/<uuid:pk>/', views.SystemEventDetailView.as_view(), name='event-detail'),
    path('events/<uuid:pk>/resolve/', views.ResolveSystemEventView.as_view(), name='resolve-event'),
]
