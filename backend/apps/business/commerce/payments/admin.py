"""
Payments Admin Configuration for Owls E-commerce Platform
=========================================================
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import PaymentMethod, Payment, Refund


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'gateway', 'is_active', 'order']
    list_filter = ['gateway', 'is_active']
    search_fields = ['name', 'code']
    ordering = ['order']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id', 'order', 'payment_method', 'amount',
        'status', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['transaction_id', 'order__order_number', 'gateway_transaction_id']
    raw_id_fields = ['order', 'payment_method']
    readonly_fields = [
        'id', 'transaction_id', 'gateway_response',
        'created_at', 'paid_at'
    ]
    date_hierarchy = 'created_at'


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'payment', 'amount', 'status', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['payment__transaction_id', 'payment__order__order_number']
    raw_id_fields = ['payment', 'processed_by']
    readonly_fields = ['id', 'created_at', 'processed_at']
