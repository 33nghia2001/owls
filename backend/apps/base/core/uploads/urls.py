"""
Upload URLs for Owls E-commerce Platform
========================================
"""

from django.urls import path
from . import views

app_name = 'uploads'

urlpatterns = [
    # List uploads
    path('', views.UploadListView.as_view(), name='list'),
    
    # Single file upload
    path('upload/', views.UploadCreateView.as_view(), name='upload'),
    
    # Bulk upload (multiple files)
    path('bulk/', views.BulkUploadView.as_view(), name='bulk-upload'),
    
    # Get presigned URL for direct upload to R2/S3
    path('presign/', views.PresignedUploadUrlView.as_view(), name='presign'),
    
    # Confirm presigned upload completed
    path('<uuid:id>/confirm/', views.ConfirmUploadView.as_view(), name='confirm'),
    
    # Get upload details
    path('<uuid:id>/', views.UploadDetailView.as_view(), name='detail'),
    
    # Delete upload
    path('<uuid:id>/delete/', views.UploadDeleteView.as_view(), name='delete'),
    
    # Mark uploads as used
    path('mark-used/', views.MarkUploadsUsedView.as_view(), name='mark-used'),
    
    # Admin: Storage statistics
    path('stats/', views.StorageStatsView.as_view(), name='stats'),
]
