"""
Coupons URLs for Owls E-commerce Platform
=========================================
"""

from django.urls import path
from . import views

app_name = 'coupons'

urlpatterns = [
    # Public coupons
    path('', views.PublicCouponsView.as_view(), name='public-coupons'),
    path('validate/', views.ValidateCouponView.as_view(), name='validate-coupon'),
    path('detail/<str:code>/', views.CouponDetailView.as_view(), name='coupon-detail'),
    
    # Cart coupon operations
    path('apply/', views.ApplyCouponToCartView.as_view(), name='apply-coupon'),
    path('remove/', views.RemoveCouponFromCartView.as_view(), name='remove-coupon'),
    
    # User's coupon history
    path('my-usage/', views.MyCouponUsageView.as_view(), name='my-coupon-usage'),
]
