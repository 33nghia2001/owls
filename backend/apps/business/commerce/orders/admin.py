"""
Orders Admin Configuration for Owls E-commerce Platform
=======================================================
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, OrderShipment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'vendor', 'product_name', 'unit_price']
    can_delete = False


class OrderShipmentInline(admin.TabularInline):
    model = OrderShipment
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'user', 'status', 'total',
        'payment_status', 'created_at'
    ]
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'user__email', 'phone']
    raw_id_fields = ['user']
    readonly_fields = [
        'id', 'order_number', 'subtotal', 
        'discount_amount', 'tax_amount', 'total', 'created_at'
    ]
    inlines = [OrderItemInline, OrderShipmentInline]
    date_hierarchy = 'created_at'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'vendor', 'quantity', 'unit_price', 'total_price', 'status']
    list_filter = ['status', 'vendor']
    search_fields = ['order__order_number', 'product_name']
    raw_id_fields = ['order', 'product', 'vendor']


@admin.register(OrderShipment)
class OrderShipmentAdmin(admin.ModelAdmin):
    list_display = ['order', 'carrier', 'tracking_number', 'status', 'shipped_at']
    list_filter = ['carrier', 'status']
    search_fields = ['order__order_number', 'tracking_number']
    raw_id_fields = ['order']
