"""
Order URL Configuration
=======================
"""

from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order-list'),
    path('create/', views.CreateOrderView.as_view(), name='create-order'),
    path('<str:order_number>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('<str:order_number>/cancel/', views.CancelOrderView.as_view(), name='cancel-order'),
    path('<str:order_number>/track/', views.OrderTrackingView.as_view(), name='track-order'),
]
