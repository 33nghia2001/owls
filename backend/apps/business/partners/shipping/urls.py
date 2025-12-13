"""
Shipping URLs for Owls E-commerce Platform
==========================================
"""

from django.urls import path
from . import views

app_name = 'shipping'

urlpatterns = [
    # Providers
    path('providers/', views.ShippingProvidersView.as_view(), name='shipping-providers'),
    
    # Rate calculation
    path('calculate/', views.CalculateShippingView.as_view(), name='calculate-shipping'),
    path('calculate/cart/', views.CalculateCartShippingView.as_view(), name='calculate-cart-shipping'),
    
    # Zones and rates (for admin/config)
    path('zones/', views.ShippingZonesView.as_view(), name='shipping-zones'),
    path('rates/', views.ShippingRatesView.as_view(), name='shipping-rates'),
]
