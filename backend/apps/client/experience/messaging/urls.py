"""
Messaging URLs for Owls E-commerce Platform
===========================================
"""

from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    # Notifications
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('count/', views.NotificationCountView.as_view(), name='notification-count'),
    path('mark-read/', views.MarkNotificationsReadView.as_view(), name='mark-read'),
    path('clear/', views.ClearNotificationsView.as_view(), name='clear-notifications'),
    path('<uuid:id>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('<uuid:notification_id>/delete/', views.DeleteNotificationView.as_view(), name='delete-notification'),
    
    # Preferences
    path('preferences/', views.NotificationPreferencesView.as_view(), name='notification-preferences'),
    
    # Devices
    path('devices/', views.MyDevicesView.as_view(), name='my-devices'),
    path('devices/register/', views.RegisterDeviceView.as_view(), name='register-device'),
    path('devices/<uuid:device_id>/unregister/', views.UnregisterDeviceView.as_view(), name='unregister-device'),
]
