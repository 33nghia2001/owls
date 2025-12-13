"""
Marketing Campaigns URLs for Owls E-commerce Platform
=====================================================
"""

from django.urls import path
from . import views

app_name = 'campaigns'

urlpatterns = [
    # Public endpoints
    path('', views.ActiveCampaignListView.as_view(), name='list'),
    path('featured/', views.FeaturedCampaignListView.as_view(), name='featured'),
    path('<slug:slug>/', views.CampaignPublicDetailView.as_view(), name='detail'),
    path('<slug:slug>/click/', views.TrackCampaignClickView.as_view(), name='track-click'),
    
    # Admin endpoints
    path('admin/list/', views.CampaignAdminListView.as_view(), name='admin-list'),
    path('admin/create/', views.CampaignCreateView.as_view(), name='admin-create'),
    path('admin/stats/', views.CampaignStatsView.as_view(), name='admin-stats'),
    path('admin/<uuid:id>/', views.CampaignAdminDetailView.as_view(), name='admin-detail'),
    path('admin/<uuid:id>/status/', views.CampaignStatusView.as_view(), name='admin-status'),
    path('admin/<uuid:id>/metrics/', views.CampaignMetricsView.as_view(), name='admin-metrics'),
    path('admin/<uuid:id>/channels/', views.CampaignChannelListView.as_view(), name='admin-channels'),
]
