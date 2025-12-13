"""
Vendor URL Configuration
========================
"""

from django.urls import path
from . import views

app_name = 'vendors'

urlpatterns = [
    # Public
    path('', views.VendorListView.as_view(), name='vendor-list'),
    path('<slug:slug>/', views.VendorDetailView.as_view(), name='vendor-detail'),
    
    # Vendor registration & management
    path('register/', views.VendorRegisterView.as_view(), name='vendor-register'),
    path('profile/', views.VendorProfileView.as_view(), name='vendor-profile'),
    path('dashboard/', views.VendorDashboardView.as_view(), name='vendor-dashboard'),
    
    # Documents
    path('documents/', views.VendorDocumentListView.as_view(), name='vendor-documents'),
    
    # Bank accounts
    path('bank-accounts/', views.VendorBankAccountListView.as_view(), name='vendor-bank-accounts'),
    path('bank-accounts/<int:pk>/', views.VendorBankAccountDetailView.as_view(), name='vendor-bank-account-detail'),
]
