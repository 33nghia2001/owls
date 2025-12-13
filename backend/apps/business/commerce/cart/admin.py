"""
Cart Admin Configuration for Owls E-commerce Platform
=====================================================
"""

from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'item_count', 'total', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['user__email', 'session_key']
    raw_id_fields = ['user']
    readonly_fields = ['id', 'session_key', 'created_at', 'updated_at']
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'variant', 'quantity', 'unit_price', 'total_price']
    search_fields = ['cart__user__email', 'product__name']
    raw_id_fields = ['cart', 'product', 'variant']
