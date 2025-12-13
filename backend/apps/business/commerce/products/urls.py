"""
Product URL Configuration
=========================
"""

from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
    # Brands
    path('brands/', views.BrandListView.as_view(), name='brand-list'),
    
    # Products
    path('', views.ProductListView.as_view(), name='product-list'),
    path('featured/', views.FeaturedProductsView.as_view(), name='featured-products'),
    path('bestsellers/', views.BestsellerProductsView.as_view(), name='bestseller-products'),
    path('new-arrivals/', views.NewArrivalsView.as_view(), name='new-arrivals'),
    path('attributes/', views.ProductAttributeListView.as_view(), name='attribute-list'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    
    # Vendor products
    path('vendor/products/', views.VendorProductListView.as_view(), name='vendor-product-list'),
    path('vendor/products/<slug:slug>/', views.VendorProductDetailView.as_view(), name='vendor-product-detail'),
]
