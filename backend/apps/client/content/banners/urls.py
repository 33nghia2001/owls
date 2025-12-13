"""
Banner URLs for Owls E-commerce Platform
========================================
"""

from django.urls import path
from . import views

app_name = 'banners'

urlpatterns = [
    # Banner endpoints
    path('slider/', views.HeroSliderView.as_view(), name='hero-slider'),
    path('homepage/', views.HomepageBannersView.as_view(), name='homepage-banners'),
    path('position/<str:position>/', views.BannersByPositionView.as_view(), name='by-position'),

    # Popup endpoints
    path('popups/', views.ActivePopupsView.as_view(), name='active-popups'),
    path('popups/impression/', views.TrackPopupImpressionView.as_view(), name='popup-impression'),
    path('popups/click/', views.TrackPopupClickView.as_view(), name='popup-click'),
    path('popups/conversion/', views.TrackPopupConversionView.as_view(), name='popup-conversion'),
]
