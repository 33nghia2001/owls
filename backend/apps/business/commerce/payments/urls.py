"""
Payment URL Configuration
=========================
"""

from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('methods/', views.PaymentMethodListView.as_view(), name='payment-methods'),
    path('create/', views.CreatePaymentView.as_view(), name='create-payment'),
    path('<str:transaction_id>/', views.PaymentDetailView.as_view(), name='payment-detail'),
    path('<str:transaction_id>/verify/', views.VerifyPaymentView.as_view(), name='verify-payment'),
    path('webhook/<str:gateway>/', views.PaymentWebhookView.as_view(), name='payment-webhook'),
]
