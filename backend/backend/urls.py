"""
URL Configuration for Owls E-commerce Platform
==============================================
API routing with versioning and documentation.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

# API v1 URLs
api_v1_patterns = [
    # ===== BASE CORE =====
    # Authentication
    path('auth/', include('apps.base.core.users.urls')),
    # Locations
    path('locations/', include('apps.base.core.locations.urls')),
    # Uploads
    path('uploads/', include('apps.base.core.uploads.urls')),

    # ===== BASE OPERATIONS =====
    # Audit Logs (Admin)
    path('audit/', include('apps.base.operations.audit_logs.urls')),
    # Support Tickets
    path('support/', include('apps.base.operations.support.urls')),

    # ===== BASE RISK =====
    # Fraud Detection
    path('fraud/', include('apps.base.risk.fraud_detection.urls')),

    # ===== BUSINESS COMMERCE =====
    path('products/', include('apps.business.commerce.products.urls')),
    path('cart/', include('apps.business.commerce.cart.urls')),
    path('orders/', include('apps.business.commerce.orders.urls')),
    path('payments/', include('apps.business.commerce.payments.urls')),

    # ===== BUSINESS PARTNERS =====
    path('vendors/', include('apps.business.partners.vendors.urls')),
    path('shipping/', include('apps.business.partners.shipping.urls')),

    # ===== CLIENT CONTENT =====
    # Blog
    path('blog/', include('apps.client.content.blog.urls')),
    # Static Pages
    path('pages/', include('apps.client.content.pages.urls')),
    # Banners
    path('banners/', include('apps.client.content.banners.urls')),

    # ===== CLIENT EXPERIENCE =====
    path('reviews/', include('apps.client.experience.reviews.urls')),
    path('wishlist/', include('apps.client.experience.wishlist.urls')),
    path('coupons/', include('apps.client.experience.coupons.urls')),
    # Loyalty Program
    path('loyalty/', include('apps.client.experience.loyalty.urls')),
    # Messaging/Notifications
    path('notifications/', include('apps.client.experience.messaging.urls')),

    # ===== GROWTH INTELLIGENCE =====
    # Search
    path('search/', include('apps.growth.intelligence.search.urls')),
    # Recommendations
    path('recommendations/', include('apps.growth.intelligence.recommendations.urls')),
]

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API v1
    path('api/v1/', include((api_v1_patterns, 'api-v1'))),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom Admin Site Configuration
admin.site.site_header = 'Owls E-commerce Admin'
admin.site.site_title = 'Owls Admin Portal'
admin.site.index_title = 'Welcome to Owls Management System'
