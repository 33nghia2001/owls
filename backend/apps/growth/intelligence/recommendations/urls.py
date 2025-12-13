"""
Recommendations URLs for Owls E-commerce Platform
=================================================
"""

from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    # Product-based recommendations
    path('similar/<uuid:product_id>/', views.SimilarProductsView.as_view(), name='similar'),
    path('frequently-bought/<uuid:product_id>/', views.FrequentlyBoughtTogetherView.as_view(), name='fbt'),

    # User-based recommendations
    path('personalized/', views.PersonalizedRecommendationsView.as_view(), name='personalized'),
    path('recently-viewed/', views.RecentlyViewedView.as_view(), name='recently-viewed'),
    path('cart-based/', views.CartBasedRecommendationsView.as_view(), name='cart-based'),

    # General recommendations
    path('trending/', views.TrendingProductsView.as_view(), name='trending'),
    path('homepage/', views.HomepageRecommendationsView.as_view(), name='homepage'),

    # User preferences
    path('preferences/', views.MyPreferencesView.as_view(), name='preferences'),

    # Tracking
    path('interaction/', views.RecordInteractionView.as_view(), name='record-interaction'),
    path('click/', views.RecordRecommendationClickView.as_view(), name='record-click'),
]
