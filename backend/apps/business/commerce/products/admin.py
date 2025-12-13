"""
Products Admin Configuration for Owls E-commerce Platform
=========================================================
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Brand, Product, ProductImage, ProductVariant


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'level', 'is_active', 'created_at']
    list_filter = ['is_active', 'level']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ['parent']
    ordering = ['order', 'name']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'product_count', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'vendor', 'category', 'price', 
        'stock_quantity', 'is_active', 'rating', 'created_at'
    ]
    list_filter = ['is_active', 'is_featured', 'category', 'vendor', 'created_at']
    search_fields = ['name', 'sku', 'vendor__store_name']
    raw_id_fields = ['vendor', 'category', 'brand']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['id', 'sku', 'sold_count', 'view_count', 'rating', 'review_count', 'created_at', 'updated_at']
    inlines = [ProductImageInline, ProductVariantInline]
    date_hierarchy = 'created_at'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'alt_text', 'is_primary']
    list_filter = ['is_primary']
    raw_id_fields = ['product']
