"""
Location URLs for Owls E-commerce Platform
==========================================
"""

from django.urls import path
from . import views

app_name = 'locations'

urlpatterns = [
    # Countries
    path('countries/', views.CountryListView.as_view(), name='country-list'),
    path('countries/<str:code>/', views.CountryDetailView.as_view(), name='country-detail'),

    # Regions
    path('countries/<str:country_code>/regions/', views.RegionListView.as_view(), name='region-list'),

    # Cities
    path('regions/<uuid:region_id>/cities/', views.CityListView.as_view(), name='city-list'),
    path('cities/search/', views.CitySearchView.as_view(), name='city-search'),

    # Districts (for VN addresses)
    path('cities/<uuid:city_id>/districts/', views.DistrictListView.as_view(), name='district-list'),

    # Wards (for VN addresses)
    path('districts/<uuid:district_id>/wards/', views.WardListView.as_view(), name='ward-list'),

    # User addresses
    path('addresses/', views.MyAddressesView.as_view(), name='address-list'),
    path('addresses/default/', views.DefaultAddressView.as_view(), name='default-address'),
    path('addresses/<uuid:pk>/', views.AddressDetailView.as_view(), name='address-detail'),
    path('addresses/<uuid:pk>/set-default/', views.SetDefaultAddressView.as_view(), name='set-default'),

    # Shipping zones
    path('shipping-zone/', views.ShippingZoneCheckView.as_view(), name='shipping-zone-check'),
]
