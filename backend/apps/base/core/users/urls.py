"""
User URL Configuration
======================
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Password
    path('password/change/', views.ChangePasswordView.as_view(), name='password-change'),
    path('password/reset/', views.PasswordResetRequestView.as_view(), name='password-reset'),
    path('password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # Profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    
    # Addresses
    path('addresses/', views.UserAddressViewSet.as_view(), name='address-list'),
    path('addresses/<int:pk>/', views.UserAddressDetailView.as_view(), name='address-detail'),
]
