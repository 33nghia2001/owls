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
    # Authentication
    path('auth/', include('apps.base.core.users.urls')),
    
    # Commerce
    path('products/', include('apps.business.commerce.products.urls')),
    path('cart/', include('apps.business.commerce.cart.urls')),
    path('orders/', include('apps.business.commerce.orders.urls')),
    path('payments/', include('apps.business.commerce.payments.urls')),
    
    # Partners
    path('vendors/', include('apps.business.partners.vendors.urls')),
    
    # Client Experience
    path('reviews/', include('apps.client.experience.reviews.urls')),
    path('wishlist/', include('apps.client.experience.wishlist.urls')),
    path('coupons/', include('apps.client.experience.coupons.urls')),
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
