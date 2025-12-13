"""
Cart URL Configuration
======================
"""

from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.CartView.as_view(), name='cart'),
    path('add/', views.AddToCartView.as_view(), name='add-to-cart'),
    path('items/<int:item_id>/', views.UpdateCartItemView.as_view(), name='update-item'),
    path('items/<int:item_id>/remove/', views.RemoveCartItemView.as_view(), name='remove-item'),
    path('clear/', views.ClearCartView.as_view(), name='clear-cart'),
    path('coupon/apply/', views.ApplyCouponView.as_view(), name='apply-coupon'),
    path('coupon/remove/', views.RemoveCouponView.as_view(), name='remove-coupon'),
]
