"""
Fraud Detection URLs for Owls E-commerce Platform
=================================================
"""

from django.urls import path
from . import views

app_name = 'fraud_detection'

urlpatterns = [
    # Fraud Rules (Admin)
    path('rules/', views.FraudRuleListCreateView.as_view(), name='rules-list'),
    path('rules/<uuid:id>/', views.FraudRuleDetailView.as_view(), name='rules-detail'),
    
    # Risk Assessments (Admin)
    path('assessments/', views.RiskAssessmentListView.as_view(), name='assessments-list'),
    path('assessments/<uuid:id>/', views.RiskAssessmentDetailView.as_view(), name='assessments-detail'),
    path('assessments/<uuid:id>/review/', views.ReviewAssessmentView.as_view(), name='assessments-review'),
    
    # IP Blacklist (Admin)
    path('ip-blacklist/', views.IPBlacklistListView.as_view(), name='ip-blacklist-list'),
    path('ip-blacklist/block/', views.BlockIPView.as_view(), name='ip-block'),
    path('ip-blacklist/<uuid:id>/unblock/', views.UnblockIPView.as_view(), name='ip-unblock'),
    
    # Device Fingerprints (Admin)
    path('devices/', views.DeviceFingerprintListView.as_view(), name='devices-list'),
    path('devices/<uuid:id>/block/', views.BlockDeviceView.as_view(), name='devices-block'),
    
    # Statistics (Admin)
    path('stats/', views.FraudStatsView.as_view(), name='stats'),
    
    # Public endpoint for IP check
    path('check-ip/', views.CheckIPView.as_view(), name='check-ip'),
]
