"""
Wishlist URLs for Owls E-commerce Platform
==========================================
"""

from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    # Wishlist
    path('', views.WishlistView.as_view(), name='wishlist'),
    path('items/', views.WishlistItemsView.as_view(), name='wishlist-items'),
    path('add/', views.AddToWishlistView.as_view(), name='add-to-wishlist'),
    path('remove/<uuid:item_id>/', views.RemoveFromWishlistView.as_view(), name='remove-from-wishlist'),
    path('clear/', views.ClearWishlistView.as_view(), name='clear-wishlist'),
    path('check/<uuid:product_id>/', views.CheckWishlistView.as_view(), name='check-wishlist'),
    path('move-to-cart/<uuid:item_id>/', views.MoveToCartView.as_view(), name='move-to-cart'),
]
