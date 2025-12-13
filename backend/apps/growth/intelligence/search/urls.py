"""
Search URLs for Owls E-commerce Platform
========================================
"""

from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    # Autocomplete and suggestions
    path('autocomplete/', views.AutocompleteView.as_view(), name='autocomplete'),
    path('popular/', views.PopularSearchesView.as_view(), name='popular'),
    path('trending/', views.TrendingSearchesView.as_view(), name='trending'),

    # User search history
    path('history/', views.SearchHistoryView.as_view(), name='history'),

    # Recording
    path('record/', views.RecordSearchView.as_view(), name='record'),
    path('record-click/', views.RecordSearchClickView.as_view(), name='record-click'),

    # Filters
    path('filters/', views.SearchFiltersView.as_view(), name='filters'),
]
